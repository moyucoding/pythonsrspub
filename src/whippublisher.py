import asyncio

from aiohttp import ClientSession, TCPConnector
from aiortc import RTCPeerConnection, RTCSessionDescription

from customstreamtrack import CustomVideoStreamTrack

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
            @self.pc.on('iceconnectionstatechange')
            async def on_iceconnectionstatechange():
                print(f'RTC: onIceConnectionChanged: {self.pc.iceConnectionState} ')
                
            @self.pc.on("connectionstatechange")
            async def on_connectionstatechange():
                print(f"Connection state is {self.pc.connectionState}")
                if self.pc.connectionState == "connected":
                    print("WebRTC connection established successfully")

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
        'camera': '/dev/video0',
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