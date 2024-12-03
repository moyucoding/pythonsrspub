import subprocess

def publish_stream(config):
    command = f"ffmpeg -f v4l2 -i {config['camera']} -vcodec libx264 -preset veryfast -tune zerolatency -f flv rtmp://{config['serverip']}/{config['app']}/{config['stream']}"
    subprocess.run(command, shell=True)


if __name__ == '__main__':
    config = {
        'camera':'/dev/video0',
        'serverip':'localhost',
        'app':'live',
        'stream':'livestream'
    }
    publish_stream(config)