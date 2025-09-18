# file: src/views/person_violation_view.py

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2

class PersonViolationView:
    def __init__(self, ui):
        self.ui = ui
        self.original_video_capture = None
        self.processed_video_capture = None
        self.timer = QTimer()
        self.is_playing = False

        # 初始化视频显示标签
        self.original_video_label = QLabel(self.ui.vedio_ori_person)
        self.original_video_label.setAlignment(Qt.AlignCenter)
        self.original_video_label.setGeometry(self.ui.vedio_ori_person.rect())

        self.processed_video_label = QLabel(self.ui.vedio_pro_person)
        self.processed_video_label.setAlignment(Qt.AlignCenter)
        self.processed_video_label.setGeometry(self.ui.vedio_pro_person.rect())

        # 连接按钮事件
        self.ui.person_con.clicked.connect(self.toggle_play_pause)

        # 定时器连接到更新帧函数
        self.timer.timeout.connect(self.update_frames)

        # 加载视频
        self.load_videos()

    def load_videos(self):
        """
        加载原始视频和处理后的视频
        """
        # 加载原始视频
        self.original_video_capture = cv2.VideoCapture('videos/person.mp4')
        # 加载处理后的视频
        self.processed_video_capture = cv2.VideoCapture('videos/person_result.mp4')

        # 检查视频是否成功加载
        if not self.original_video_capture.isOpened():
            print("无法打开原始视频文件: videos/person.mp4")
            return False

        if not self.processed_video_capture.isOpened():
            print("无法打开处理后的视频文件: videos/person_result.mp4")
            return False

        self.is_playing = False
        return True

    def update_frames(self):
        """
        更新两个视频的帧显示
        """
        if not self.original_video_capture or not self.processed_video_capture:
            return

        # 读取原始视频帧
        ret1, original_frame = self.original_video_capture.read()
        # 读取处理后的视频帧
        ret2, processed_frame = self.processed_video_capture.read()

        # 如果任一视频播放结束，重置到开始位置
        if not ret1 or not ret2:
            self.original_video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.processed_video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        # 显示原始视频帧
        self.display_frame(original_frame, self.original_video_label)

        # 显示处理后的视频帧
        self.display_frame(processed_frame, self.processed_video_label)

    def display_frame(self, frame, label):
        """
        在指定标签上显示视频帧
        """
        if frame is not None:
            # 转换颜色空间 BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 创建 QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # 缩放以适应显示区域
            pixmap = QPixmap.fromImage(q_img)
            scaled_pixmap = pixmap.scaled(
                label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # 显示图像
            label.setPixmap(scaled_pixmap)

    def toggle_play_pause(self):
        """
        切换播放和暂停状态
        """
        if self.is_playing:
            self.pause_videos()
        else:
            self.play_videos()

    def play_videos(self):
        """
        开始播放视频
        """
        if not self.original_video_capture or not self.processed_video_capture:
            self.load_videos()

        self.is_playing = True
        # 设置定时器约30fps (1000ms/30 ≈ 33ms)
        self.timer.start(33)

    def pause_videos(self):
        """
        暂停视频播放
        """
        self.is_playing = False
        self.timer.stop()

    def stop_videos(self):
        """
        停止视频播放并释放资源
        """
        self.pause_videos()
        if self.original_video_capture:
            self.original_video_capture.release()
            self.original_video_capture = None
        if self.processed_video_capture:
            self.processed_video_capture.release()
            self.processed_video_capture = None
