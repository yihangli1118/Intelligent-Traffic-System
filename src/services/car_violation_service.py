# file: src/services/car_violation_service.py
import cv2
import os
from PyQt5.QtCore import QObject, pyqtSignal
from services.violation import TrafficViolationDetector

class CarViolationService(QObject):
    # 定义信号，用于向控制器发送处理后的帧和进度信息
    frame_processed = pyqtSignal(object, object)  # 原始帧, 处理后帧
    progress_updated = pyqtSignal(int)  # 进度百分比
    video_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        try:
            self.detector = TrafficViolationDetector()
        except Exception as e:
            print(f"初始化违规检测器时出错: {e}")
            self.detector = None
        self.cap = None
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30

    def open_video(self, video_path):
        """打开视频文件"""
        if self.cap is not None:
            self.cap.release()

        if os.path.exists(video_path):
            self.cap = cv2.VideoCapture(video_path)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 30
            self.current_frame = 0
            return True
        return False

    def start_detection(self):
        """开始检测"""
        if self.cap is None:
            return

        self.is_playing = True

        while self.is_playing and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                self.is_playing = False
                self.video_finished.emit()
                break

            # 处理帧
            processed_frame = frame.copy()
            if self.detector is not None:
                try:
                    processed_frame = self.detector.process_frame(frame.copy(), self.fps)
                except Exception as e:
                    print(f"处理帧时出错: {e}")

            # 发送信号
            self.frame_processed.emit(frame, processed_frame)

            # 更新进度
            self.current_frame += 1
            if self.total_frames > 0:
                progress = int((self.current_frame / self.total_frames) * 100)
                self.progress_updated.emit(progress)

            # 控制播放速度
            cv2.waitKey(int(1000 / self.fps))

    def pause_detection(self):
        """暂停检测"""
        self.is_playing = False

    def stop_detection(self):
        """停止检测"""
        self.is_playing = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def set_position(self, position):
        """设置视频播放位置"""
        if self.cap is not None and self.total_frames > 0:
            frame_number = int((position / 100) * self.total_frames)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.current_frame = frame_number
