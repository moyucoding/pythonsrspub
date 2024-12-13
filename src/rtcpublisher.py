import asyncio
import json
import random
import time

from aiohttp import ClientSession, TCPConnector
from aiortc import RTCPeerConnection, RTCSessionDescription

from customstreamtrack import CustomVideoStreamTrack

class RtcPublisher:
    def __init__(self, config):
        self.api = ''
        if config['serverip'] == 'localhost':
            self.api = f"http://localhost:{config['port']}/rtc/v1/publish/"
        else:
            self.api = f"https://{config['serverip']}:{config['port']}/rtc/v1/publish/"

        self.streamurl = f"webrtc://{config['serverip']}:{config['port']}/{config['app']}/{config['stream']}"
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
            async with ClientSession(connector=TCPConnector(ssl=self.ssl)) as session:
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
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            while True:
                await asyncio.sleep(1)

    def setup_media(self):
        self.pc.addTransceiver("audio", "sendonly");
        self.pc.addTransceiver("video", "sendonly");

        video_sender = CustomVideoStreamTrack(self.camera)
        self.pc.addTrack(video_sender)

async def main():
    config = {
        'camera': '/dev/video0',
        'serverip':'127.0.0.1',
        'port':1990,
        'app': 'live',
        'stream':'rtc',
        'sslcheck': False,
        'width': 640,
        'height': 480
    }
    publisher = RtcPublisher(config)
    await publisher.start()

if __name__ == '__main__':
   asyncio.run(main())