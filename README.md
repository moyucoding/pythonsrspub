# Python SRS Publisher
This is a Python program that streams a webcam to SRS. Supporting RTMP, WebRTC, and WHIP.

![image](https://github.com/moyucoding/pythonsrspub/blob/main/images/rtmp.jpg)

To work with SRS, see [SRS](https://github.com/ossrs/srs) and deploy server. Then install python packages:

```bash
pip install -r requirements.txt
```

## To publish
### Publish via WebRTC
Edit configs in rtcpublisher.py, for streaming ```webrtc://127.0.0.1:1990/live/rtc``` for example:

```python
config = {
        'camera': '/dev/video0', # Camera path
        'serverip':'127.0.0.1', # Server IP address
        'port':1985, # Server HTTPS API port
        'app': 'live', # Application name
        'stream':'rtc' # Stream name
        'sslcheck': False, # For self-signed SSL, set to False
        'width': 640, # Stream size, use camera default if 0
        'height': 480
    }
```
Then run the script.
```bash
python rtcpublisher.py
```

### Publish via WHIP
Edit configs in whippublisher.py, for streaming ```https://127.0.0.1:1990/rtc/v1/whip/?app=live&stream=whip``` for example:

```python
config = {
        'camera': '/dev/video0', # Camera path
        'serverip':'127.0.0.1', # Server IP address
        'port':1990, # Server HTTPS API port
        'app': 'live', # Application name
        'stream':'whip', # Stream name
        'sslcheck': False, # For self-signed SSL, set to False
        'width': 640, # Stream size, use camera default if 0
        'height': 480
    }
```

Then run the script.
```bash
python whippublisher.py
```

### Publish via Rtmp
Edit configs in whippublisher.py, for streaming ```rtmp://127.0.0.1/live/rtmp``` for example:

```python
config = {
        'camera': '/dev/video0', # Camera path
        'serverip':'127.0.0.1', # Server IP address
        'app': 'live', # Application name
        'stream':'whip' # Stream name
        'width': 640, # Stream size, use camera default if 0
        'height': 480
    }
```
Then run the script.
```bash
python rtmppublisher.py
```

### Configs
* For Mac/Windows Users: 

Use 
```json
    'camera': 0 # Camera Index
 ```

* For connecting localhost:

Use
```json
    'serverip':'localhost',
    'port':1985,
```
## To play
According to SRS, the video streams pushed in the above three ways can be played in the following ways.

| Protocol | Address |
|--|--|
|Publisher||
|WebRtc Publisher|webrtc://127.0.0.1:1990/live/stream|
|WHIP Publisher|https://127.0.0.1:1990/rtc/v1/whip/?app=live&stream=stream|
|RTMP Publisher|rtmp://127.0.0.1/live/stream|
|Player||
|WebRtc Player|webrtc://127.0.0.1:1990/live/stream|
|WHEP Player|https://127.0.0.1:1990/rtc/v1/whip/?app=live&stream=stream|
|RTMP Player|https://127.0.0.1:8088/live/stream.flv|
|FLV Player|https://127.0.0.1:8088/live/stream.flv|
|HLS Player|https://127.0.0.1:8088/live/stream.m3u8|
