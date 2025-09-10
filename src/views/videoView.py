# videoView.py
import cv2
from PyQt5.QtWidgets import QFileDialog, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

class VideoView:
    def __init__(self, ui):
        self.ui = ui
        self.video_controller = None  # 将在MainWindow中设置
        self.timer = QTimer()
        self.is_playing = False
        self.total_frames = 0
        self.current_frame = 0
        self.is_slider_pressed = False

        # 初始化UI组件
        self.setup_ui()

    def set_controller(self, controller):
        """
        设置视频控制器
        """
        self.video_controller = controller

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
        self.original_video_label.setMinimumSize(1, 1)  # 设置最小尺寸

        self.processed_video_label = QLabel(self.ui.vedio_pro)
        self.processed_video_label.setAlignment(Qt.AlignCenter)
        self.processed_video_label.setGeometry(self.ui.vedio_pro.rect())
        self.processed_video_label.setMinimumSize(1, 1)  # 设置最小尺寸

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
        # 加载新视频
        if self.video_controller and self.video_controller.play_video(file_path):
            # 获取视频信息
            self.total_frames = self.video_controller.video_service.get_total_frames()

            # 设置滑动条范围
            self.ui.horizontalSlider.setMinimum(0)
            self.ui.horizontalSlider.setMaximum(self.total_frames - 1)

            # 开始播放
            self.is_playing = True
            self.timer.start(33)  # 约30fps (1000ms/30 ≈ 33ms)

    def update_frame(self):
        if self.video_controller and self.is_playing and not self.is_slider_pressed:
            ret, frame = self.video_controller.get_frame()
            if ret:
                self.current_frame = self.video_controller.video_service.get_current_frame_position()
                self.ui.horizontalSlider.setValue(self.current_frame)

                # 显示原始视频帧
                self.display_frame(frame, self.original_video_label)

                # 处理并显示目标检测后的帧
                processed_frame = self.video_controller.process_frame_for_detection(frame)
                self.display_frame(processed_frame, self.processed_video_label)
            else:
                # 视频播放结束
                self.timer.stop()
                self.is_playing = False

    def display_frame(self, frame, label):
        """
        在指定的标签上显示帧
        """
        if frame is not None:
            # 转换颜色空间 BGR to RGB
            if len(frame.shape) == 3:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

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
        if self.video_controller:
            if self.is_playing:
                self.is_playing = False
                self.timer.stop()
            else:
                self.is_playing = True
                self.timer.start(33)

    def slider_pressed(self):
        self.is_slider_pressed = True
        if self.is_playing:
            self.timer.stop()

    def slider_released(self):
        if self.video_controller:
            # 获取滑动条位置并跳转到对应帧
            position = self.ui.horizontalSlider.value()
            self.video_controller.seek_video(position)
            self.is_slider_pressed = False
            if self.is_playing:
                self.timer.start(33)
