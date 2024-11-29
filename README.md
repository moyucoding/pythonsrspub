# Python WebRTC Publisher
This is a Python program that streams a webcam to SRS via WebRTC.

![image](https://github.com/moyucoding/pythonsrspub/blob/main/images/sample.png)

To work with SRS, see [SRS](https://github.com/ossrs/srs) and deploy server. Then install python packages:

```bash
pip install -r requirements.txt
```

Then edit configs in publisher.py, to publish to ```webrtc://localhost/live/livestream``` for example:

```python
config = {
        'camera': '/dev/video0', # Path of camera
        'serverip':'localhost', # IP address of server
        'port':1985, # HTTP API port of server
        'app': 'live', # App name
        'stream':'livestream' # Stream name
    }
```


