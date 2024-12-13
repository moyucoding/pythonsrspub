import cv2
import fractions

from aiortc import VideoStreamTrack
from av import VideoFrame

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