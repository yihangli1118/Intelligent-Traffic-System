# videoService.py
import cv2
import numpy as np
from detector import Detector
import tracker

class VideoService:
    def __init__(self):
        self.video_capture = None
        self.is_playing = False
        self.detector = None  # 延迟初始化目标检测器

        # 用于目标检测的polygon mask
        self.polygon_mask_blue_and_yellow = None
        self.color_polygons_image = None
        # 不在初始化时创建 polygons

    def _ensure_detector_initialized(self):
        """
        确保目标检测器已初始化
        """
        if self.detector is None:
            self.detector = Detector()

    def _ensure_detection_polygons_initialized(self):
        """
        确保检测 polygons 已初始化
        """
        if self.polygon_mask_blue_and_yellow is None or self.color_polygons_image is None:
            self._init_detection_polygons()

    def _init_detection_polygons(self):
        """
        初始化目标检测用的polygon区域
        """
        # 根据视频尺寸，填充一个polygon，供撞线计算使用
        mask_image_temp = np.zeros((1080, 1920), dtype=np.uint8)

        # 初始化2个撞线polygon
        list_pts_blue = [[204, 305], [227, 431], [605, 522], [1101, 464], [1900, 601], [1902, 495], [1125, 379], [604, 437],
                         [299, 375], [267, 289]]
        ndarray_pts_blue = np.array(list_pts_blue, np.int32)
        polygon_blue_value_1 = cv2.fillPoly(mask_image_temp, [ndarray_pts_blue], color=1)
        polygon_blue_value_1 = polygon_blue_value_1[:, :, np.newaxis]

        # 填充第二个polygon
        mask_image_temp = np.zeros((1080, 1920), dtype=np.uint8)
        list_pts_yellow = [[181, 305], [207, 442], [603, 544], [1107, 485], [1898, 625], [1893, 701], [1101, 568],
                           [594, 637], [118, 483], [109, 303]]
        ndarray_pts_yellow = np.array(list_pts_yellow, np.int32)
        polygon_yellow_value_2 = cv2.fillPoly(mask_image_temp, [ndarray_pts_yellow], color=2)
        polygon_yellow_value_2 = polygon_yellow_value_2[:, :, np.newaxis]

        # 撞线检测用mask，包含2个polygon，（值范围 0、1、2），供撞线计算使用
        self.polygon_mask_blue_and_yellow = polygon_blue_value_1 + polygon_yellow_value_2

        # 缩小尺寸，1920x1080->960x540
        self.polygon_mask_blue_and_yellow = cv2.resize(self.polygon_mask_blue_and_yellow, (960, 540))

        # 蓝 色盘 b,g,r
        blue_color_plate = [255, 0, 0]
        # 蓝 polygon图片
        blue_image = np.array(polygon_blue_value_1 * blue_color_plate, np.uint8)

        # 黄 色盘
        yellow_color_plate = [0, 255, 255]
        # 黄 polygon图片
        yellow_image = np.array(polygon_yellow_value_2 * yellow_color_plate, np.uint8)

        # 彩色图片（值范围 0-255）
        self.color_polygons_image = blue_image + yellow_image
        # 缩小尺寸，1920x1080->960x540
        self.color_polygons_image = cv2.resize(self.color_polygons_image, (960, 540))

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

    def process_frame_for_detection(self, frame):
        """
        对帧进行目标检测处理
        :param frame: 原始帧
        :return: 处理后的帧
        """
        if frame is None:
            return None

        # 确保检测器和 polygons 已初始化
        self._ensure_detector_initialized()
        self._ensure_detection_polygons_initialized()

        # 缩小尺寸，1920x1080->960x540
        im = cv2.resize(frame, (960, 540))

        list_bboxs = []
        bboxes = self.detector.detect(im)

        # 如果画面中 有bbox
        if len(bboxes) > 0:
            list_bboxs = tracker.update(bboxes, im)
            # 画框
            output_image_frame = tracker.draw_bboxes(im, list_bboxs, line_thickness=None)
        else:
            # 如果画面中 没有bbox
            output_image_frame = im

        # 添加polygon区域到检测帧上 （不显示撞线区域）
        # if self.color_polygons_image is not None:
        #     output_image_frame = cv2.add(output_image_frame, self.color_polygons_image)

        return output_image_frame

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
