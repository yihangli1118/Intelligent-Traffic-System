# videoController.py
from services.videoService import VideoService

class VideoController:
    def __init__(self, view):
        self.view = view
        self.video_service = VideoService()
        self.on_video_switched_callback = None  # 添加回调属性

    def set_video_switched_callback(self, callback):
        """设置视频切换回调"""
        self.on_video_switched_callback = callback

    def open_video(self):
        """
        处理打开视频文件的请求
        """
        return self.video_service.open_video_file()

    def play_video(self, file_path):
        """
        处理播放视频的请求
        """
        result = self.video_service.play_video(file_path)
        # 视频切换后调用回调
        if result and self.on_video_switched_callback:
            self.on_video_switched_callback()
        return result

    def pause_video(self):
        """
        处理暂停视频的请求
        """
        self.video_service.pause_video()

    def resume_video(self):
        """
        处理恢复视频播放的请求
        """
        self.video_service.resume_video()

    def stop_video(self):
        """
        处理停止视频的请求
        """
        self.video_service.stop_video()

    def seek_video(self, position):
        """
        处理跳转到指定位置的请求
        """
        self.video_service.seek_to_position(position)

    def get_frame(self):
        """
        获取当前帧
        """
        return self.video_service.get_frame()

    def process_frame_for_detection(self, frame):
        """
        处理帧以进行目标检测
        """
        return self.video_service.process_frame_for_detection(frame)
