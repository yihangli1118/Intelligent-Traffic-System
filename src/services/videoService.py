# videoService.py
import cv2

class VideoService:
    def __init__(self):
        self.video_capture = None
        self.is_playing = False

    def open_video_file(self):
        """
        打开视频文件
        """
        # 这个方法在View层处理文件选择对话框
        pass

    def play_video(self, file_path):
        """
        播放视频文件
        :param file_path: 视频文件路径
        :return: 是否成功开始播放
        """
        try:
            if self.video_capture:
                self.video_capture.release()

            self.video_capture = cv2.VideoCapture(file_path)
            if self.video_capture.isOpened():
                self.is_playing = True
                return True
            else:
                return False
        except Exception as e:
            print(f"播放视频时出错: {e}")
            return False

    def pause_video(self):
        """
        暂停视频播放
        """
        self.is_playing = False

    def resume_video(self):
        """
        恢复视频播放
        """
        if self.video_capture and self.video_capture.isOpened():
            self.is_playing = True

    def stop_video(self):
        """
        停止视频播放并释放资源
        """
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        self.is_playing = False

    def seek_to_position(self, frame_position):
        """
        跳转到指定帧位置
        :param frame_position: 帧位置
        """
        if self.video_capture and self.video_capture.isOpened():
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_position)

    def get_frame(self):
        """
        获取当前帧
        :return: (ret, frame) ret表示是否成功获取帧，frame为帧数据
        """
        if self.video_capture and self.is_playing:
            return self.video_capture.read()
        return False, None

    def get_total_frames(self):
        """
        获取视频总帧数
        :return: 总帧数
        """
        if self.video_capture:
            return int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        return 0

    def get_current_frame_position(self):
        """
        获取当前帧位置
        :return: 当前帧位置
        """
        if self.video_capture:
            return int(self.video_capture.get(cv2.CAP_PROP_POS_FRAMES))
        return 0

    def is_video_opened(self):
        """
        检查视频是否已打开
        :return: 是否已打开
        """
        if self.video_capture:
            return self.video_capture.isOpened()
        return False
