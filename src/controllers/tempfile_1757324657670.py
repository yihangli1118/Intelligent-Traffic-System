# videoController.py
from services.videoService import VideoService

class VideoController:
    def __init__(self, view):
        self.view = view
        self.video_service = VideoService()
        
    def open_video(self):
        """
        处理打开视频文件的请求
        """
        return self.video_service.open_video_file()
        
    def play_video(self, file_path):
        """
        处理播放视频的请求
        """
        return self.video_service.play_video(file_path)
        
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
