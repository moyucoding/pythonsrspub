from aiohttp import ClientSession
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import asyncio
from av import VideoFrame
import cv2
import fractions
import json
import random
import time 

class CustomVideoStreamTrack(VideoStreamTrack):
    def __init__(self, camera_path):
        super().__init__()
        self.cap = cv2.VideoCapture(camera_path)
        self.frame_count = 0

    async def recv(self):
        self.frame_count += 1
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to read frame from camera")
            return None
        a = 1 + 1

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = 104
        video_frame.time_base = fractions.Fraction(1, 30)

        return video_frame

class RtcPublisher:
    def __init__(self, config):
        self.api = ''
        if config['serverip'] == 'localhost':
            self.api = f"http://localhost:{config['port']}/rtc/v1/publish/"
        else:
            self.api = f"https://{config['serverip']}:{config['port']}/rtc/v1/publish/"

        self.streamurl = f"webrtc://{config['serverip']}:{config['port']}/{config['app']}/{config['stream']}"
        self.camera = config['camera']

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
            
            # uri = 'http://localhost:1985/rtc/v1/publish/'
            # uri = 'https://127.0.0.1:1990/rtc/v1/publish/'
            headers = {
                "Content-Type": "application/json"
            }
            data =  {
                'api': self.api,
                'clientip': None,
                'sdp': offer.sdp,
                'streamurl': self.streamurl,
                'tid': str(int(time.time() * random.random() * 100))[:7]
            }
            answer = ''
            async with ClientSession() as session:
                async with session.post(self.api, headers=headers, data=json.dumps(data)) as response:
                    if response.status == 200:
                        print("SDP exchange successful")
                        text = await response.text()
                        answer = json.loads(text)
                    else:
                        raise Exception("SDP exchange failed")
            if answer['code'] != 0:
                return
            if self.pc.connectionState == "new" or self.pc.connectionState == "connecting":
                await self.pc.setRemoteDescription(RTCSessionDescription(sdp=answer['sdp'], type='answer'))
            else:
                print("Connection state is not suitable for setting remote description")
        finally:
            while True:
                await asyncio.sleep(1)
            # await self.pc.close()

    def setup_media(self):
        self.pc.addTransceiver("audio", "sendonly");
        self.pc.addTransceiver("video", "sendonly");

        video_sender = CustomVideoStreamTrack(self.camera)
        self.pc.addTrack(video_sender)

async def main():
    config = {
        'camera':'/dev/video0',
        'serverip':'localhost',
        'port':1985,
        'app': 'live',
        'stream':'livestream'
    }
    publisher = RtcPublisher(config)
    await publisher.start()

if __name__ == '__main__':
   asyncio.run(main())