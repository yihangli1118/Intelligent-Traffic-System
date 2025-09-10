# file: src/views/videoView.py
import cv2
from PyQt5.QtWidgets import QFileDialog, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from services.detection_service import DetectionService

class VideoView:
    def __init__(self, ui):
        self.ui = ui
        self.video_capture = None
        self.timer = QTimer()
        self.is_playing = False
        self.total_frames = 0
        self.current_frame = 0
        self.is_slider_pressed = False

        # 初始化目标检测服务
        self.detection_service = DetectionService()

        # 初始化UI组件
        self.setup_ui()

    def setup_ui(self):
        # 连接按钮事件
        self.ui.pushButton_3.clicked.connect(self.open_video_file)
        self.ui.pushButton_5.clicked.connect(self.toggle_play_pause)
        self.ui.horizontalSlider.sliderPressed.connect(self.slider_pressed)
        self.ui.horizontalSlider.sliderReleased.connect(self.slider_released)

        # 初始化视频显示区域
        self.original_video_label = QLabel(self.ui.vedio_ori)
        self.original_video_label.setAlignment(Qt.AlignCenter)
        self.original_video_label.setGeometry(self.ui.vedio_ori.rect())

        self.processed_video_label = QLabel(self.ui.vedio_pro)
        self.processed_video_label.setAlignment(Qt.AlignCenter)
        self.processed_video_label.setGeometry(self.ui.vedio_pro.rect())

        # 定时器连接到更新帧函数
        self.timer.timeout.connect(self.update_frame)

    def open_video_file(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            None, "选择视频文件", "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.flv *.wmv)"
        )

        if file_path:
            self.load_video(file_path)

    def load_video(self, file_path):
        # 释放之前的视频资源
        if self.video_capture:
            self.video_capture.release()

        # 加载新视频
        self.video_capture = cv2.VideoCapture(file_path)
        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        # 设置滑动条范围
        self.ui.horizontalSlider.setMinimum(0)
        self.ui.horizontalSlider.setMaximum(self.total_frames - 1)

        # 重置计数器
        self.detection_service.reset_counters()

        # 开始播放
        self.is_playing = True
        self.timer.start(30)  # 约33fps

    def update_frame(self):
        if self.video_capture and self.is_playing and not self.is_slider_pressed:
            ret, frame = self.video_capture.read()
            if ret:
                self.current_frame = int(self.video_capture.get(cv2.CAP_PROP_POS_FRAMES))
                self.ui.horizontalSlider.setValue(self.current_frame)

                # 显示原始视频
                self.display_original_frame(frame)

                # 显示处理后的视频
                self.display_processed_frame(frame)
            else:
                # 视频播放结束
                self.timer.stop()
                self.is_playing = False

    def display_original_frame(self, frame):
        """
        显示原始视频帧
        """
        # 转换颜色空间 BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 创建 QImage
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # 缩放以适应显示区域
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(
            self.original_video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # 显示图像
        self.original_video_label.setPixmap(scaled_pixmap)

    def display_processed_frame(self, frame):
        """
        显示处理后的视频帧
        """
        # 处理帧
        processed_frame = self.detection_service.process_frame(frame)

        # 转换颜色空间 BGR to RGB
        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

        # 创建 QImage
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # 缩放以适应显示区域
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(
            self.processed_video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # 显示图像
        self.processed_video_label.setPixmap(scaled_pixmap)

    def toggle_play_pause(self):
        if self.video_capture:
            self.is_playing = not self.is_playing
            if self.is_playing:
                self.timer.start(30)
            else:
                self.timer.stop()

    def slider_pressed(self):
        self.is_slider_pressed = True
        if self.video_capture:
            self.timer.stop()

    def slider_released(self):
        self.is_slider_pressed = False
        if self.video_capture:
            # 获取滑动条位置并跳转到对应帧
            position = self.ui.horizontalSlider.value()
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, position)
            if self.is_playing:
                self.timer.start(30)
