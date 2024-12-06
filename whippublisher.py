from aiohttp import ClientSession, TCPConnector
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import asyncio
from av import VideoFrame
import cv2
import fractions

class CustomVideoStreamTrack(VideoStreamTrack):
    def __init__(self, camera_path, width=0, height=0):
        super().__init__()
        self.cap = cv2.VideoCapture(camera_path)
        self.frame_count = 0
        self.width = width
        self.height = height

    async def recv(self):
        self.frame_count += 1
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to read frame from camera")
            return None

        if self.width > 0 and self.height > 0:
            frame = cv2.resize(frame, (self.width, self.height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = 104
        video_frame.time_base = fractions.Fraction(1, 30)

        return video_frame
    
class WhipPublisher:
    def __init__(self, config):
        self.url = f"https://{config['serverip']}:{config['port']}/rtc/v1/whip/?app={config['app']}&stream={config['stream']}"
        self.camera = config['camera']
        self.ssl = config['sslcheck']
        self.width = config['width']
        self.height = config['height']
        
    async def start(self):
        self.pc = RTCPeerConnection()
        
        try:
            @self.pc.on('icecandidate')
            def on_icecandidate(candidate):
                print(f'RTC: onIceCandidate: {candidate} ')

            @self.pc.on('iceconnectionstatechange')
            async def on_iceconnectionstatechange():
                print(f'RTC: onIceConnectionChanged: {self.pc.iceConnectionState} ')
                
            @self.pc.on("track")
            async def on_track(track):
                print(f'RTC: onTrack: id: {track.id}, kind: {track.kind}')

            @self.pc.on("connectionstatechange")
            async def on_connectionstatechange():
                print(f"Connection state is {self.pc.connectionState}")
                if self.pc.connectionState == "connected":
                    print("WebRTC connection established successfully")

            @self.pc.on('icegetheringstatechange')
            async def on_icegetheringstatechange():
                print(f'RTC: onIceGatheringChanged: {self.pc.iceGatheringState} ')
            

            self.setup_media()
            
            #Send offer
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
            headers = {
                "Content-Type": "application/sdp"
            }
            answer = ''
            async with ClientSession(connector=TCPConnector(ssl=self.ssl)) as session:
                async with session.post(self.url, headers=headers, data=offer.sdp) as response:
                    if response.status == 201:
                        print("SDP exchange successful")
                        answer = await response.text()
                    else:
                        raise Exception("SDP exchange failed")
            if self.pc.connectionState == "new" or self.pc.connectionState == "connecting":
                await self.pc.setRemoteDescription(RTCSessionDescription(sdp=answer, type='answer'))
            else:
                print("Connection state is not suitable for setting remote description")
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            while True:
                await asyncio.sleep(1)

    def setup_media(self):
        self.pc.addTransceiver("audio", "sendonly")
        self.pc.addTransceiver("video", "sendonly")

        video_sender = CustomVideoStreamTrack(self.camera)
        self.pc.addTrack(video_sender)

async def main():
    config = {
        'camera':'/dev/video0',
        'serverip':'127.0.0.1',
        'port':1990,
        'app': 'live',
        'stream':'whip',
        'sslcheck': False,
        'width': 640,
        'height': 480
    }
    publisher = WhipPublisher(config)
    await publisher.start()

if __name__ == '__main__':
   asyncio.run(main())