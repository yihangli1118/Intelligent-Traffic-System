# file: src/controllers/car_violation_controller.py
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QFileDialog, QMessageBox
from services.car_violation_service import CarViolationService
import cv2
import os

class CarViolationController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.service = None
        self.thread = None

        # 连接UI组件
        self.main_window.open_car.clicked.connect(self.open_video)
        self.main_window.start_car.clicked.connect(self.toggle_play_pause)
        self.main_window.horizontalSlider_2.sliderMoved.connect(self.set_video_position)

        # 初始化视频显示标签
        self.init_video_labels()

    def init_video_labels(self):
        """初始化视频显示标签"""
        # 原始视频显示标签
        self.original_video_label = QLabel(self.main_window.vedio_ori_car)
        self.original_video_label.setAlignment(Qt.AlignCenter)
        self.original_video_label.setGeometry(0, 0,
                                              self.main_window.vedio_ori_car.width(),
                                              self.main_window.vedio_ori_car.height())
        self.original_video_label.setStyleSheet("background-color: black;")

        # 处理后视频显示标签
        self.processed_video_label = QLabel(self.main_window.vedio_pro_car)
        self.processed_video_label.setAlignment(Qt.AlignCenter)
        self.processed_video_label.setGeometry(0, 0,
                                               self.main_window.vedio_pro_car.width(),
                                               self.main_window.vedio_pro_car.height())
        self.processed_video_label.setStyleSheet("background-color: black;")

    def open_video(self):
        """打开视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, "打开视频文件", "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv)")

        if file_path:
            # 创建新的服务实例
            if self.service:
                self.service.stop_detection()

            try:
                self.service = CarViolationService()
                self.service.moveToThread(self.thread) if self.thread else None
                self.service.frame_processed.connect(self.update_video_frames)
                self.service.progress_updated.connect(self.update_progress)
                self.service.video_finished.connect(self.on_video_finished)

                if self.service.open_video(file_path):
                    # 重置UI状态
                    self.main_window.start_car.setEnabled(True)
                    self.main_window.horizontalSlider_2.setValue(0)
                else:
                    QMessageBox.warning(self.main_window, "错误", "无法打开视频文件")
            except Exception as e:
                QMessageBox.critical(self.main_window, "错误", f"初始化检测服务时出错:\n{str(e)}")

    def toggle_play_pause(self):
        """切换播放/暂停状态"""
        if not self.service or not self.service.cap:
            return

        if self.service.is_playing:
            self.service.pause_detection()
            # 更改按钮图标为播放
            from PyQt5.QtWidgets import QStyle
            self.main_window.start_car.setIcon(
                self.main_window.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            # 在新线程中开始播放
            self.thread = QThread()
            self.service.moveToThread(self.thread)
            self.thread.started.connect(self.service.start_detection)
            self.service.video_finished.connect(self.thread.quit)
            self.service.video_finished.connect(self.service.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(lambda: setattr(self, 'thread', None))
            self.thread.start()

            # 更改按钮图标为暂停
            from PyQt5.QtWidgets import QStyle
            self.main_window.start_car.setIcon(
                self.main_window.style().standardIcon(QStyle.SP_MediaPause))

    def set_video_position(self, position):
        """设置视频位置"""
        if self.service:
            self.service.set_position(position)

    def update_video_frames(self, original_frame, processed_frame):
        """更新视频帧显示"""
        # 显示原始视频帧
        if original_frame is not None and original_frame.size != 0:
            self.display_frame(original_frame, self.original_video_label)

        # 显示处理后的视频帧
        if processed_frame is not None and processed_frame.size != 0:
            self.display_frame(processed_frame, self.processed_video_label)

    def display_frame(self, frame, label):
        """在指定标签上显示视频帧"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # 缩放图像以适应标签
            pixmap = QPixmap.fromImage(q_img)
            pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
        except Exception as e:
            print(f"显示帧时出错: {e}")

    def update_progress(self, progress):
        """更新进度条"""
        self.main_window.horizontalSlider_2.setValue(progress)

    def on_video_finished(self):
        """视频播放完成时的处理"""
        from PyQt5.QtWidgets import QStyle
        self.main_window.start_car.setIcon(
            self.main_window.style().standardIcon(QStyle.SP_MediaPlay))
        self.main_window.horizontalSlider_2.setValue(0)

    def stop_video(self):
        """停止视频播放"""
        if self.service:
            self.service.stop_detection()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
