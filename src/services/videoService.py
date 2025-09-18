# videoService.py
import cv2
import numpy as np
from detector import Detector
import tracker
import re
import os
from datetime import datetime
from services.databaseService import DatabaseService
from models.vehicle import Vehicle
from models.person import Person
from models.bicycle import Bicycle
from models.motorcycle import Motorcycle
from models.road import Road
from models.flow import Flow
# 车牌识别
import torch
from ultralytics.nn.tasks import attempt_load_weights
from plate_recognition.plate_rec import get_plate_result, init_model
from plate_recognition.double_plate_split_merge import get_split_merge


class VideoService:
    MISSING_THRESHOLD = 5.0  # 5秒超时

    def __init__(self):
        self.video_capture = None
        self.is_playing = False
        self.detector = None  # 延迟初始化目标检测器

        # self.database_service = DatabaseService()  # 数据库服务

        self.database_service = DatabaseService()  # 数据库服务，延迟初始化
        self.current_video_path = None  # 当前视频路径

        # 用于目标检测的polygon mask
        self.polygon_mask_blue_and_yellow = None
        self.color_polygons_image = None
        # 不在初始化时创建 polygons

        # 视频开始时间
        self.video_start_time = None

        # 当前视频的路口信息
        self.current_road_id = None
        self.current_road_name = None

        # 跟踪对象列表
        self.tracked_objects = {}  # 存储正在跟踪的对象信息

        # 撞线检测相关
        self.list_overlapping_blue_polygon = []
        self.list_overlapping_yellow_polygon = []
        self.down_count = 0
        self.up_count = 0

        # 添加初始化时间标记
        self._init_current_time = None

        # 车牌识别模型
        self.plate_detect_model = None
        self.plate_rec_model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _ensure_detector_initialized(self):
        """
        确保目标检测器已初始化
        """
        if self.detector is None:
            self.detector = Detector()

        # 初始化车牌识别模型
        if self.plate_detect_model is None or self.plate_rec_model is None:
            self._init_plate_recognition_models()

    def _init_plate_recognition_models(self):
        """
        初始化车牌识别模型
        """
        try:
            # 加载YOLOv8车牌检测模型
            self.plate_detect_model = attempt_load_weights('weights/yolov8s.pt', device=self.device)
            # 加载车牌识别模型
            self.plate_rec_model = init_model(self.device, 'weights/plate_rec_color.pth', is_color=True)
            self.plate_detect_model.eval()
            print("车牌识别模型加载成功")
        except Exception as e:
            print(f"车牌识别模型加载失败: {e}")
            self.plate_detect_model = None
            self.plate_rec_model = None

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
        list_pts_blue = [[204, 305], [227, 431], [605, 522], [1101, 464], [1900, 601], [1902, 495], [1125, 379],
                         [604, 437],
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

    def _letter_box(self, img, size=(640, 640)):
        """yolo 前处理 letter_box操作"""
        h, w, _ = img.shape
        r = min(size[0] / h, size[1] / w)
        new_h, new_w = int(h * r), int(w * r)
        new_img = cv2.resize(img, (new_w, new_h))
        left = int((size[1] - new_w) / 2)
        top = int((size[0] - new_h) / 2)
        right = size[1] - left - new_w
        bottom = size[0] - top - new_h
        img = cv2.copyMakeBorder(new_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))
        return img, r, left, top

    def _xywh2xyxy(self, det):
        """xywh转化为xyxy"""
        y = det.clone()
        y[:, 0] = det[:, 0] - det[0:, 2] / 2
        y[:, 1] = det[:, 1] - det[0:, 3] / 2
        y[:, 2] = det[:, 0] + det[0:, 2] / 2
        y[:, 3] = det[:, 1] + det[0:, 3] / 2
        return y

    def _my_nums(self, dets, iou_thresh):
        """nms操作"""
        y = dets.clone()
        y_box_score = y[:, :5]
        index = torch.argsort(y_box_score[:, -1], descending=True)
        keep = []
        while index.size()[0] > 0:
            i = index[0].item()
            keep.append(i)
            x1 = torch.maximum(y_box_score[i, 0], y_box_score[index[1:], 0])
            y1 = torch.maximum(y_box_score[i, 1], y_box_score[index[1:], 1])
            x2 = torch.minimum(y_box_score[i, 2], y_box_score[index[1:], 2])
            y2 = torch.minimum(y_box_score[i, 3], y_box_score[index[1:], 3])
            zero_ = torch.tensor(0).to(self.device)
            w = torch.maximum(zero_, x2 - x1)
            h = torch.maximum(zero_, y2 - y1)
            inter_area = w * h
            nuion_area1 = (y_box_score[i, 2] - y_box_score[i, 0]) * (y_box_score[i, 3] - y_box_score[i, 1])  # 计算交集
            union_area2 = (y_box_score[index[1:], 2] - y_box_score[index[1:], 0]) * (
                        y_box_score[index[1:], 3] - y_box_score[index[1:], 1])  # 计算并集

            iou = inter_area / (nuion_area1 + union_area2 - inter_area)  # 计算iou

            idx = torch.where(iou <= iou_thresh)[0]  # 保留iou小于iou_thresh的
            index = index[idx + 1]
        return keep

    def _restore_box(self, dets, r, left, top):
        """坐标还原到原图上"""
        dets[:, [0, 2]] = dets[:, [0, 2]] - left
        dets[:, [1, 3]] = dets[:, [1, 3]] - top
        dets[:, :4] /= r
        return dets

    def _post_processing(self, prediction, conf, iou_thresh, r, left, top):
        """后处理"""
        prediction = prediction.permute(0, 2, 1).squeeze(0)
        xc = prediction[:, 4:6].amax(1) > conf  # 过滤掉小于conf的框
        x = prediction[xc]
        if not len(x):
            return []
        boxes = x[:, :4]  # 框
        boxes = self._xywh2xyxy(boxes)  # 中心点 宽高 变为 左上 右下两个点
        score, index = torch.max(x[:, 4:6], dim=-1, keepdim=True)  # 找出得分和所属类别
        x = torch.cat((boxes, score, x[:, 6:14], index), dim=1)  # 重新组合

        score = x[:, 4]
        keep = self._my_nums(x, iou_thresh)
        x = x[keep]
        x = self._restore_box(x, r, left, top)
        return x

    def _pre_processing(self, img, img_size=640):
        """前处理"""
        img, r, left, top = self._letter_box(img, (img_size, img_size))
        img = img[:, :, ::-1].transpose((2, 0, 1)).copy()  # bgr2rgb hwc2chw
        img = torch.from_numpy(img).to(self.device)
        img = img.float()
        img = img / 255.0
        img = img.unsqueeze(0)
        return img, r, left, top

    def _det_rec_plate(self, img, img_ori):
        """
        车牌检测和识别
        参考 detect_rec_plate.py 中的 det_rec_plate 函数
        """
        result_list = []
        img, r, left, top = self._pre_processing(img, 640)  # 前处理
        predict = self.plate_detect_model(img)[0]
        outputs = self._post_processing(predict, 0.3, 0.5, r, left, top)  # 后处理
        for output in outputs:
            result_dict = {}
            output = output.squeeze().cpu().numpy().tolist()
            rect = output[:4]
            rect = [int(x) for x in rect]
            label = output[-1]
            roi_img = img_ori[rect[1]:rect[3], rect[0]:rect[2]]
            if int(label):  # 判断是否是双层车牌，是双牌的话进行分割后然后拼接
                roi_img = get_split_merge(roi_img)
            plate_number, rec_prob, plate_color, color_conf = get_plate_result(roi_img, self.device,
                                                                               self.plate_rec_model, is_color=True)

            result_dict['plate_no'] = plate_number  # 车牌号
            result_dict['plate_color'] = plate_color  # 车牌颜色
            result_dict['rect'] = rect  # 车牌roi区域
            result_dict['detect_conf'] = output[4]  # 检测区域得分
            result_dict['roi_height'] = roi_img.shape[0]  # 车牌高度
            result_dict['color_conf'] = color_conf  # 颜色得分
            result_dict['plate_type'] = int(label)  # 单双层 0单层 1双层
            result_list.append(result_dict)
        return result_list

    def _recognize_car_color(self, image_path):
        """
        车身颜色识别
        参考 detect_rec_plate.py 中的 recognize_car_color 函数
        """
        try:
            from car_color_recognition import recognize_car_color
            return recognize_car_color(image_path)
        except Exception as e:
            print(f"车身颜色识别失败: {e}")
            return "未知"

    def open_video_file(self):
        """
        打开视频文件
        """
        # 这个方法在View层处理文件选择对话框
        pass

    def play_video(self, file_path):
        """
            播放视频文件（每次调用都断开并重新连接数据库）
            :param file_path: 视频文件路径
            :return: 是否成功开始播放
        """
        try:
            print(f"准备播放视频: {file_path}")

            # 无论是否是同一个视频，都要断开当前数据库连接并创建新的连接
            self._disconnect_and_reconnect_database()

            # 释放当前视频资源
            if self.video_capture:
                self.video_capture.release()

            # 创建新的视频捕获对象
            self.video_capture = cv2.VideoCapture(file_path)

            if self.video_capture.isOpened():
                # 记录当前视频路径
                self.current_video_path = file_path

                # 清空跟踪对象并设置新视频的开始时间
                self.tracked_objects.clear()
                # 重置初始化时间
                self._init_current_time = None

                # 初始化交通流量统计
                self._init_traffic_stats()

                # 重置UI显示数据为默认值
                self.last_vehicle_count_data = 0
                self.last_entry_count_data = 0
                self.last_departure_count_data = 0
                self.last_flow_growth_rate = 0
                self.last_entry_growth_rate = 0
                self.last_departure_growth_rate = 0

                # 解析视频文件名获取路口信息和开始时间
                video_filename = os.path.basename(file_path)
                print(f"解析视频文件名: {video_filename}")  # 添加调试信息
                video_info = self._parse_video_filename(video_filename)

                if video_info:
                    self.video_start_time = video_info['start_time']
                    self.current_road_id = video_info['road_id']
                    self.current_road_name = video_info['road_name']
                    print(
                        f"视频信息解析成功: 路口ID={self.current_road_id}, 路口名称={self.current_road_name}, 开始时间={self.video_start_time}")
                    # 验证时间是否正确解析
                    if self.video_start_time:
                        print(f"解析的开始时间类型: {type(self.video_start_time)}, 值: {self.video_start_time}")
                    # 输出视频时间范围
                    if 'end_time' in video_info and video_info['end_time']:
                        print(f"视频时间范围: {self.video_start_time} 到 {video_info['end_time']}")
                    # 保存路口信息到roads表
                    self._save_road_info()
                else:
                    self.video_start_time = datetime.now()
                    self.current_road_id = "default_road"
                    self.current_road_name = "默认路口"
                    print("无法解析视频文件名，使用默认值")

                self.is_playing = True
                print(f"开始播放视频: {file_path}，已创建新的数据库连接")
                return True
            else:
                print(f"无法打开视频文件: {file_path}")
                return False
        except Exception as e:
            print(f"播放视频时出错: {e}")
            import traceback
            traceback.print_exc()
            return False


    def _disconnect_and_reconnect_database(self):
        """
        断开当前数据库连接并创建新的连接
        """
        # 保存当前视频的剩余数据（如果有的话）
        if self.database_service is not None:
            print("保存当前视频的剩余数据...")
            # 只有在流量统计变量已初始化时才调用保存方法
            if hasattr(self, 'last_stats_time'):
                self._save_remaining_objects()
            self.database_service = None
            print("已断开数据库连接")

        # 创建新的数据库服务实例
        print("创建新的数据库连接...")
        self.database_service = DatabaseService()
        print("新的数据库连接已建立")

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

        if self.database_service is not None:
            print("保存视频结束时的剩余数据...")
            self._save_remaining_objects()

        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        self.is_playing = False

        # 重置流量统计变量
        self.last_stats_time = None
        self.last_vehicle_count = 0
        self.vehicles_since_last_stats = 0
        self.departures_since_last_stats = 0
        self.total_entries = 0
        self.total_departures = 0

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
            ret, frame = self.video_capture.read()
            # 如果视频自然播放结束
            if not ret:
                print("视频自然播放结束，保存剩余对象数据...")
                self._save_remaining_objects_on_video_end()
            return ret, frame
        return False, None

    def _save_remaining_objects_on_video_end(self):
        """
        视频自然结束时保存剩余对象
        """
        if not self.tracked_objects:
            return
        current_time = datetime.now()
        #departure_time = self._calculate_actual_time(current_time)
        video_end_time = self._calculate_actual_time(current_time)

        for track_id, obj_info in self.tracked_objects.items():
            # 使用对象最后被检测到的时间作为离开时间，而不是视频结束时间
            if 'actual_last_seen' in obj_info:
                departure_time = obj_info['actual_last_seen']
            elif 'last_seen' in obj_info:
                departure_time = self._calculate_actual_time(obj_info['last_seen'])
            else:
                # 如果没有记录，则使用视频结束时间
                departure_time = video_end_time

            self._update_object_departure_time(track_id, obj_info['type'], departure_time)

        # 清空跟踪对象列表
        self.tracked_objects.clear()

        # 重置视频开始时间和初始化时间
        self.video_start_time = None
        self._init_current_time = None

        print("视频结束时的剩余数据已保存")

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

        # 获取原始帧尺寸
        original_height, original_width = frame.shape[:2]

        # 只在检测时缩小尺寸，1920x1080->960x540
        detection_frame = cv2.resize(frame, (960, 540))

        list_bboxs = []
        bboxes = self.detector.detect(detection_frame)

        # print(f"检测到的边界框数量: {len(bboxes)}")  # 添加调试信息

        # 如果画面中 有bbox
        if len(bboxes) > 0:
            list_bboxs = tracker.update(bboxes, detection_frame)
            # 画框
            output_image_frame = tracker.draw_bboxes(detection_frame, list_bboxs, line_thickness=None)

            # 只有在有数据库连接时才处理对象
            if self.database_service is not None:
                # 传递原始帧frame而不是处理后的detection_frame，以便截取高清晰度的图像
                self._process_detected_objects(list_bboxs, detection_frame, frame,
                                               original_width, original_height)

        else:
            # 如果画面中 没有bbox
            output_image_frame = detection_frame

        # 添加polygon区域到检测帧上 （不显示撞线区域）
        # if self.color_polygons_image is not None:
        #     output_image_frame = cv2.add(output_image_frame, self.color_polygons_image)

        # 将输出帧调整回原始尺寸以保持显示一致性
        output_image_frame = cv2.resize(output_image_frame, (original_width, original_height))

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

    def _process_detected_objects(self, list_bboxs, processed_frame, original_frame,
                                  original_width, original_height):
        """
        处理检测到的对象并保存到数据库
        :param list_bboxs: 检测到的边界框列表
        :param processed_frame: 处理后的帧（用于检测）
        :param original_frame: 原始帧（用于高清晰度截图）
        :param original_width: 原始帧宽度
        :param original_height: 原始帧高度
        """
        current_time = datetime.now()

        # 创建当前帧中检测到的对象集合
        currently_detected = set()

        # 处理每个检测到的对象
        for item_bbox in list_bboxs:
            x1, y1, x2, y2, label, track_id = item_bbox
            currently_detected.add(track_id)

            # 检查是否是新对象
            if track_id not in self.tracked_objects:
                # 新对象首次出现，记录进入时间
                entry_time = self._calculate_actual_time(current_time)

                # 记录跟踪对象，但不立即截图
                self.tracked_objects[track_id] = {
                    'type': label,
                    'entry_time': entry_time,
                    'last_seen': current_time,
                    'first_seen_time': current_time,  # 记录首次检测到的时间
                    'bbox': (x1, y1, x2, y2),  # 保存边界框信息
                    'processed_frame': processed_frame,  # 保存处理后的帧
                    'original_frame': original_frame,  # 保存原始帧
                    'original_width': original_width,  # 保存原始帧宽度
                    'original_height': original_height,  # 保存原始帧高度
                    'screenshot_taken': False  # 标记是否已截图
                }

                # 增加新增车辆计数
                self.vehicles_since_last_stats += 1
                self.total_entries += 1

            else:
                # 更新对象最后出现时间
                self.tracked_objects[track_id]['last_seen'] = current_time
                # 更新边界框信息
                self.tracked_objects[track_id]['bbox'] = (x1, y1, x2, y2)
                # 更新帧信息
                self.tracked_objects[track_id]['processed_frame'] = processed_frame
                self.tracked_objects[track_id]['original_frame'] = original_frame
                self.tracked_objects[track_id]['original_width'] = original_width
                self.tracked_objects[track_id]['original_height'] = original_height

                # 更新视频实际时间
                self.tracked_objects[track_id]['actual_last_seen'] = self._calculate_actual_time(current_time)

                # 检查是否需要截图（首次检测后2秒）
                if not self.tracked_objects[track_id]['screenshot_taken']:
                    first_seen_time = self.tracked_objects[track_id]['first_seen_time']
                    time_diff = (current_time - first_seen_time).total_seconds()

                    # 如果超过2秒且还未截图
                    if time_diff >= 5.0:
                        # 执行截图并保存到数据库
                        self._take_and_save_screenshot(track_id)
                        self.tracked_objects[track_id]['screenshot_taken'] = True

        # 检查是否有对象长时间未出现
        self._check_missing_objects(current_time, currently_detected)

        # 定期执行流量统计
        self._periodic_traffic_stats()

    def _take_and_save_screenshot(self, track_id):
        """
        为指定对象执行截图并保存到数据库
        :param track_id: 路口ID
        """
        if track_id not in self.tracked_objects:
            return

        obj_info = self.tracked_objects[track_id]

        # 获取对象信息
        label = obj_info['type']
        entry_time = obj_info['entry_time']
        x1, y1, x2, y2 = obj_info['bbox']
        original_frame = obj_info['original_frame']
        original_width = obj_info['original_width']
        original_height = obj_info['original_height']

        try:
            print(f"为对象 {track_id} 截图并保存到数据库")

            # 缩放因子，因为处理帧是缩小的版本(960x540)
            scale_x = original_width / 960.0
            scale_y = original_height / 540.0

            # 根据原始帧尺寸调整边界框坐标
            orig_x1 = int(x1 * scale_x)
            orig_y1 = int(y1 * scale_y)
            orig_x2 = int(x2 * scale_x)
            orig_y2 = int(y2 * scale_y)

            # 确保坐标在有效范围内
            orig_x1 = max(0, orig_x1)
            orig_y1 = max(0, orig_y1)
            orig_x2 = min(original_width, orig_x2)
            orig_y2 = min(original_height, orig_y2)

            # 使用原始检测范围截图，不扩大范围
            object_image = original_frame[orig_y1:orig_y2, orig_x1:orig_x2]

            # 初始化车牌信息和车身颜色
            plate_info = None
            car_color = "未知"

            # 如果截图区域有效
            if object_image.size > 0:
                # 编码截图
                _, img_buffer = cv2.imencode('.jpg', object_image)
                photo_binary = img_buffer.tobytes() if img_buffer is not None else None

                # 车牌识别
                if self.plate_detect_model is not None and self.plate_rec_model is not None:
                    try:
                        img_ori = object_image.copy()
                        plate_results = self._det_rec_plate(object_image, img_ori)
                        if plate_results:
                            plate_info = plate_results[0]  # 取第一个识别结果
                    except Exception as e:
                        print(f"车牌识别出错: {e}")

                # 车身颜色识别（需要保存临时文件）
                try:
                    temp_image_path = f"temp_car_{track_id}.jpg"
                    cv2.imwrite(temp_image_path, object_image)
                    car_color = self._recognize_car_color(temp_image_path)
                    # 删除临时文件
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
                except Exception as e:
                    print(f"车身颜色识别出错: {e}")
            else:
                photo_binary = Noset_video_started_callbackne

            if plate_info:
                plate_number = plate_info['plate_no']
                # 如果车牌号存在且长度小于等于6位，认为是识别错误
                if plate_number and len(plate_number.strip()) <= 6:
                    plate_info['plate_no'] = "对向来车"
                    plate_info['plate_color'] = "对向来车"
                    #car_color = "对向来车"
            else:
                # 如果没有识别到车牌，也标记为"对向来车"
                if plate_info is None:
                    plate_info = {
                        'plate_no': "对向来车",
                        'plate_color': "对向来车"
                    }
                    car_color = "对向来车"

            # 保存车牌号到跟踪对象信息中
            self.tracked_objects[track_id]['plate_number'] = plate_info['plate_no'] if plate_info else "对向来车"
            self.tracked_objects[track_id]['plate_color'] = plate_info['plate_color'] if plate_info else "对向来车"
            self.tracked_objects[track_id]['body_color'] = car_color

            # 确定行驶方向（使用原始坐标）
            driving_direction = self._determine_driving_direction(x1, y1, x2, y2)

            # 使用解析的路口ID
            road_id = getattr(self, 'current_road_id', "default_road")

            # 根据标签类型保存对象
            if label in ['car', 'bus', 'truck']:
                import random
                vehicle = Vehicle(
                    vehicle_id=str(track_id),
                    vehicle_type=label,
                    entry_time=entry_time,
                    driving_direction=driving_direction,
                    road_id=road_id,
                    photo=photo_binary,
                    speed=round(random.uniform(15, 30), 1),
                    # 添加车牌信息和车身颜色
                    plate_number=plate_info['plate_no'] if plate_info else None,
                    plate_color=plate_info['plate_color'] if plate_info else None,
                    body_color=car_color
                )
                result = self.database_service.save_vehicle(vehicle)
                print(f"保存车辆结果: {result}")
            elif label == 'person':
                person = Person(
                    person_id=str(track_id),
                    entry_time=entry_time,
                    driving_direction=driving_direction,
                    road_id=road_id,
                    photo=photo_binary
                )
                self.database_service.save_person(person)
            elif label == 'bicycle':
                bicycle = Bicycle(
                    bicycle_id=str(track_id),
                    entry_time=entry_time,
                    driving_direction=driving_direction,
                    road_id=road_id,
                    photo=photo_binary
                )
                self.database_service.save_bicycle(bicycle)
            elif label == 'motorcycle':
                motorcycle = Motorcycle(
                    motorcycle_id=str(track_id),
                    entry_time=entry_time,
                    driving_direction=driving_direction,
                    road_id=road_id,
                    photo=photo_binary
                )
                self.database_service.save_motorcycle(motorcycle)

        except Exception as e:
            print(f"为对象 {track_id} 截图时出错: {e}")
            import traceback
            traceback.print_exc()

    def _calculate_actual_time(self, current_time):
        """
        计算对象实际出现时间（基于视频开始时间），使用视频真实时间
        :param current_time: 当前系统时间（用于初始化参考）
        :return: 视频中的实际时间
        """
        if self.video_start_time and self.video_capture and self.video_capture.isOpened():
            # 获取视频的帧率和当前帧位置
            fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            current_frame = self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)

            # 根据帧位置计算视频中经过的时间
            if fps > 0:
                video_elapsed_time = current_frame / fps
                # 基于视频开始时间加上经过的视频时间
                from datetime import timedelta
                result_time = self.video_start_time + timedelta(seconds=video_elapsed_time)
                # 确保时间精确到秒
                return result_time.replace(microsecond=0)

        # 如果无法获取视频信息，回退到原来的逻辑
        if self.video_start_time:
            # 如果这是第一次调用，记录初始时间
            if self._init_current_time is None:
                self._init_current_time = current_time
                # 返回精确到秒的视频开始时间
                return self.video_start_time.replace(microsecond=0)
            else:
                # 计算时间差并应用到视频开始时间上
                time_diff = current_time - self._init_current_time
                result_time = self.video_start_time + time_diff
                # 返回精确到秒的时间
                return result_time.replace(microsecond=0)
        # 如果没有视频开始时间，返回精确到秒的当前时间
        return current_time.replace(microsecond=0)

    def _save_new_object(self, track_id, label, entry_time, frame, x1, y1, x2, y2):
        """
        保存新检测到的对象
        :param track_id: 跟踪ID
        :param label: 对象标签
        :param entry_time: 进入时间
        :param frame: 原始帧（修改为传入原始帧）
        :param x1, y1, x2, y2: 边界框坐标
        """
        try:
            print(f"检测到新对象: ID={track_id}, 类型={label}")  # 添加调试信息

            # 缩放因子，因为处理帧是缩小的版本(960x540)
            height, width = frame.shape[:2]
            scale_x = width / 960.0
            scale_y = height / 540.0

            # 根据原始帧尺寸调整边界框坐标
            orig_x1 = int(x1 * scale_x)
            orig_y1 = int(y1 * scale_y)
            orig_x2 = int(x2 * scale_x)
            orig_y2 = int(y2 * scale_y)

            # 确保坐标在有效范围内
            orig_x1 = max(0, orig_x1)
            orig_y1 = max(0, orig_y1)
            orig_x2 = min(width, orig_x2)
            orig_y2 = min(height, orig_y2)

            # 截取三张不同范围的图像
            screenshots = []

            # 1. 原始边界框截图
            object_image_1 = frame[orig_y1:orig_y2, orig_x1:orig_x2]
            screenshots.append(('original', object_image_1))

            # 2. 扩大20%的截图
            bbox_width = orig_x2 - orig_x1
            bbox_height = orig_y2 - orig_y1
            margin_x = int(bbox_width * 0.2)
            margin_y = int(bbox_height * 0.2)

            expanded_x1 = max(0, orig_x1 - margin_x)
            expanded_y1 = max(0, orig_y1 - margin_y)
            expanded_x2 = min(width, orig_x2 + margin_x)
            expanded_y2 = min(height, orig_y2 + margin_y)

            object_image_2 = frame[expanded_y1:expanded_y2, expanded_x1:expanded_x2]
            screenshots.append(('expanded_20', object_image_2))

            # 3. 扩大40%的截图
            margin_x_large = int(bbox_width * 0.4)
            margin_y_large = int(bbox_height * 0.4)

            expanded_x1_large = max(0, orig_x1 - margin_x_large)
            expanded_y1_large = max(0, orig_y1 - margin_y_large)
            expanded_x2_large = min(width, orig_x2 + margin_x_large)
            expanded_y2_large = min(height, orig_y2 + margin_y_large)

            object_image_3 = frame[expanded_y1_large:expanded_y2_large, expanded_x1_large:expanded_x2_large]
            screenshots.append(('expanded_40', object_image_3))

            # 选择最佳截图（基于清晰度评估）
            best_screenshot = self._select_best_screenshot(screenshots)

            # 初始化车牌信息和车身颜色
            plate_info = None
            car_color = "未知"

            # 编码最佳截图
            _, img_buffer = cv2.imencode('.jpg', best_screenshot)
            photo_binary = img_buffer.tobytes() if img_buffer is not None else None

            # 车牌识别
            if self.plate_detect_model is not None and self.plate_rec_model is not None:
                try:
                    img_ori = best_screenshot.copy()
                    plate_results = self._det_rec_plate(best_screenshot, img_ori)
                    if plate_results:
                        plate_info = plate_results[0]  # 取第一个识别结果
                except Exception as e:
                    print(f"车牌识别出错: {e}")

            # 车身颜色识别（需要保存临时文件）
            try:
                temp_image_path = f"temp_car_{track_id}.jpg"
                cv2.imwrite(temp_image_path, best_screenshot)
                car_color = self._recognize_car_color(temp_image_path)
                # 删除临时文件
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
            except Exception as e:
                print(f"车身颜色识别出错: {e}")

            # 确定行驶方向（使用原始坐标）
            driving_direction = self._determine_driving_direction(x1, y1, x2, y2)

            # 使用解析的路口ID
            road_id = getattr(self, 'current_road_id', "default_road")

            # 根据标签类型保存对象
            if label in ['car', 'bus', 'truck']:
                import random
                vehicle = Vehicle(
                    vehicle_id=str(track_id),
                    vehicle_type=label,
                    entry_time=entry_time,
                    driving_direction=driving_direction,
                    road_id=road_id,
                    photo=photo_binary,
                    speed=round(random.uniform(15, 30), 1),
                    # 添加车牌信息和车身颜色
                    plate_number=plate_info['plate_no'] if plate_info else None,
                    plate_color=plate_info['plate_color'] if plate_info else None,
                    body_color=car_color
                )
                result = self.database_service.save_vehicle(vehicle)
                print(f"保存车辆结果: {result}")
            elif label == 'person':
                person = Person(
                    person_id=str(track_id),
                    entry_time=entry_time,
                    driving_direction=driving_direction,
                    road_id=road_id,
                    photo=photo_binary
                )
                self.database_service.save_person(person)
            elif label == 'bicycle':
                bicycle = Bicycle(
                    bicycle_id=str(track_id),
                    entry_time=entry_time,
                    driving_direction=driving_direction,
                    road_id=road_id,
                    photo=photo_binary
                )
                self.database_service.save_bicycle(bicycle)
            elif label == 'motorcycle':
                motorcycle = Motorcycle(
                    motorcycle_id=str(track_id),
                    entry_time=entry_time,
                    driving_direction=driving_direction,
                    road_id=road_id,
                    photo=photo_binary
                )
                self.database_service.save_motorcycle(motorcycle)

            # 记录跟踪对象
            self.tracked_objects[track_id] = {
                'type': label,
                'entry_time': entry_time,
                'last_seen': datetime.now()
            }
        except Exception as e:
            print(f"保存新对象时出错: {e}")
        import traceback
        traceback.print_exc()

    def _select_best_screenshot(self, screenshots):
        """
        选择最佳截图（基于图像清晰度）
        :param screenshots: 包含截图类型和图像数据的元组列表
        :return: 最佳截图图像
        """
        if len(screenshots) == 1:
            return screenshots[0][1]

        best_image = None
        best_score = -1
        best_type = ""

        for screenshot_type, image in screenshots:
            # 计算图像清晰度得分（使用拉普拉斯算子）
            if image is not None and image.size > 0:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

                if laplacian_var > best_score:
                    best_score = laplacian_var
                    best_image = image
                    best_type = screenshot_type

        print(f"选择截图类型: {best_type}, 清晰度得分: {best_score}")

        # 如果所有图像都无效，返回第一张
        if best_image is None and len(screenshots) > 0:
            best_image = screenshots[0][1]

        return best_image if best_image is not None else screenshots[0][1]

    def _determine_driving_direction(self, x1, y1, x2, y2):
        """
        根据对象位置确定行驶方向
        :return: "上行" 或 "下行"
        """
        # 撞线检测点，(x1，y1)，y方向偏移比例 0.0~1.0
        y1_offset = int(y1 + ((y2 - y1) * 0.6))
        y = y1_offset
        x = x1

        if self.polygon_mask_blue_and_yellow is not None:
            if self.polygon_mask_blue_and_yellow[y, x] == 1:
                return "下行"
            elif self.polygon_mask_blue_and_yellow[y, x] == 2:
                return "上行"

        return "未知"

    # def _check_missing_objects(self, current_time, currently_detected):
    #     """
    #     检查哪些对象长时间未出现
    #     :param current_time: 当前时间
    #     :param currently_detected: 当前帧中检测到的对象ID集合
    #     """
    #
    #     for track_id, obj_info in list(self.tracked_objects.items()):
    #         # 如果对象在当前帧中被检测到
    #         if track_id in currently_detected:
    #             # 如果之前标记为可能离开，现在重新出现则取消标记
    #             if 'marked_as_missing' in obj_info:
    #                 del self.tracked_objects[track_id]['marked_as_missing']
    #                 print(f"对象 {track_id} 重新出现，取消离开标记")
    #         else:
    #             # 对象在当前帧中未检测到
    #             last_seen = obj_info['last_seen']
    #             time_diff = (current_time - last_seen).total_seconds()
    #
    #             # 如果超过阈值时间未出现
    #             if time_diff > self.MISSING_THRESHOLD:
    #                 # 检查是否已经标记为可能离开
    #                 if 'marked_as_missing' not in obj_info:
    #                     # 第一次标记为可能离开，更新数据库中的离开时间
    #                     departure_time = self._calculate_actual_time(current_time)
    #                     self._update_object_departure_time(track_id, obj_info['type'], departure_time)
    #                     # 标记为可能离开
    #                     self.tracked_objects[track_id]['marked_as_missing'] = True
    #                     print(f"对象 {track_id} 超过 {self.MISSING_THRESHOLD} 秒未出现，标记为可能离开")

    def _check_missing_objects(self, current_time, currently_detected):
        """
        检查哪些对象长时间未出现
        :param current_time: 当前时间
        :param currently_detected: 当前帧中检测到的对象ID集合
        """

        # 计算当前视频中的实际时间
        actual_current_time = self._calculate_actual_time(current_time)

        # 处理当前帧中检测到的对象
        for track_id in currently_detected:
            if track_id in self.tracked_objects:
                # 如果之前标记为暂时离开，现在重新出现
                if track_id in self.temporarily_missing_vehicles:
                    disappear_time = self.temporarily_missing_vehicles[track_id]
                    # 检查是否在当前统计周期内离开
                    if self.last_stats_time is None or disappear_time >= self.last_stats_time:
                        # 在当前周期内离开又重新出现，离开数-1
                        self.departures_since_last_stats -= 1
                        print(f"对象 {track_id} 重新出现，离开计数减1")
                    else:
                        # 在之前周期离开现在重新出现，进入数+1
                        self.vehicles_since_last_stats += 1
                        self.total_entries += 1
                        print(f"对象 {track_id} 重新进入，进入计数加1")

                    # 从暂时离开列表中移除
                    del self.temporarily_missing_vehicles[track_id]

        # 检查未在当前帧中检测到的对象
        for track_id, obj_info in list(self.tracked_objects.items()):
            # 如果对象在当前帧中未被检测到
            if track_id not in currently_detected:
                # 计算对象最后出现的视频实际时间
                if 'actual_last_seen' in obj_info:
                    actual_last_seen = obj_info['actual_last_seen']
                else:
                    # 如果没有记录视频实际时间，使用系统时间转换
                    actual_last_seen = self._calculate_actual_time(obj_info['last_seen'])

                # 计算视频中经过的真实时间差
                video_time_diff = (actual_current_time - actual_last_seen).total_seconds()

                # 如果超过阈值时间未出现（视频真实时间5秒）
                if video_time_diff > self.MISSING_THRESHOLD:
                    # 检查是否已经标记为暂时离开
                    if track_id not in self.temporarily_missing_vehicles:
                        # 标记为暂时离开
                        self.temporarily_missing_vehicles[track_id] = actual_current_time
                        # 增加离开车辆计数
                        self.departures_since_last_stats += 1
                        self.total_departures += 1
                        print(f"对象 {track_id} 暂时离开，离开计数加1")
        # # 计算当前视频中的实际时间
        # actual_current_time = self._calculate_actual_time(current_time)
        #
        # for track_id, obj_info in list(self.tracked_objects.items()):
        #     # 如果对象在当前帧中被检测到
        #     if track_id in currently_detected:
        #         # 如果之前标记为可能离开，现在重新出现则取消标记
        #         if 'marked_as_missing' in obj_info:
        #             del self.tracked_objects[track_id]['marked_as_missing']
        #             print(f"对象 {track_id} 重新出现，取消离开标记")
        #     else:
        #         # 对象在当前帧中未检测到
        #         # 计算对象最后出现的视频实际时间
        #         if 'actual_last_seen' in obj_info:
        #             actual_last_seen = obj_info['actual_last_seen']
        #         else:
        #             # 如果没有记录视频实际时间，使用系统时间转换
        #             actual_last_seen = self._calculate_actual_time(obj_info['last_seen'])
        #
        #         # 计算视频中经过的真实时间差
        #         video_time_diff = (actual_current_time - actual_last_seen).total_seconds()
        #
        #         # 如果超过阈值时间未出现（视频真实时间5秒）
        #         if video_time_diff > self.MISSING_THRESHOLD:
        #             # 检查是否已经标记为可能离开
        #             if 'marked_as_missing' not in obj_info:
        #                 # 第一次标记为可能离开，更新数据库中的离开时间
        #                 # departure_time = self._calculate_actual_time(current_time)
        #
        #                 departure_time = actual_last_seen
        #
        #                 self._update_object_departure_time(track_id, obj_info['type'], departure_time)
        #                 # 标记为可能离开
        #                 self.tracked_objects[track_id]['marked_as_missing'] = True
        #                 # 记录视频实际时间，用于下次比较
        #                 self.tracked_objects[track_id]['actual_last_seen'] = actual_current_time
        #                 print(f"对象 {track_id} 超过 {self.MISSING_THRESHOLD} 秒未出现，标记为可能离开")
        #
        #                 # 增加离开车辆计数
        #                 self.departures_since_last_stats += 1
        #                 self.total_departures += 1

        # for track_id, obj_info in list(self.tracked_objects.items()):
        #     # 如果对象在当前帧中未检测到
        #     if track_id not in currently_detected:
        #         last_seen = obj_info['last_seen']
        #         time_diff = (current_time - last_seen).total_seconds()
        #
        #         # 如果超过阈值时间未出现
        #         if time_diff > self.MISSING_THRESHOLD:
        #             # 检查是否已经标记为可能离开
        #             if 'marked_as_missing' not in obj_info:
        #                 # 第一次标记为可能离开，更新数据库中的离开时间
        #                 departure_time = self._calculate_actual_time(current_time)
        #                 self._update_object_departure_time(track_id, obj_info['type'], departure_time)
        #                 # 标记为可能离开
        #                 # self.tracked_objects[track_id]['marked_as_missing'] = True
        #                 # print(f"对象 {track_id} 超过 {self.MISSING_THRESHOLD} 秒未出现，标记为可能离开")
        #             # 注意：不从tracked_objects中删除，保留跟踪状态

    def _update_object_departure_time(self, track_id, obj_type, departure_time):
        """
        更新对象的离开时间
        :param track_id: 跟踪ID
        :param obj_type: 对象类型
        :param departure_time: 离开时间
        """
        if obj_type in ['car', 'bus', 'truck']:
            self.database_service.update_vehicle_departure(str(track_id), departure_time)
        elif obj_type == 'person':
            self.database_service.update_person_departure(str(track_id), departure_time)
        elif obj_type == 'bicycle':
            self.database_service.update_bicycle_departure(str(track_id), departure_time)
        elif obj_type == 'motorcycle':
            self.database_service.update_motorcycle_departure(str(track_id), departure_time)

    def _save_remaining_objects(self):
        """
        保存视频结束时仍在跟踪的对象
        """
        if not hasattr(self, 'last_stats_time'):
            return

        # current_time = datetime.now()
        # departure_time = self._calculate_actual_time(current_time)
        #
        # for track_id, obj_info in self.tracked_objects.items():
        #     self._update_object_departure_time(track_id, obj_info['type'], departure_time)
        # # 如果对象没有被标记为可能离开，或者标记了但需要更新离开时间
        # # if 'marked_as_missing' not in obj_info or obj_info['marked_as_missing']:
        # #     self._update_object_departure_time(track_id, obj_info['type'], departure_time)
        if self.tracked_objects:  # 只有当有跟踪对象时才处理
            current_time = datetime.now()
            video_end_time = self._calculate_actual_time(current_time)

            for track_id, obj_info in self.tracked_objects.items():
                # 使用对象最后被检测到的时间作为离开时间，而不是视频结束时间
                if 'actual_last_seen' in obj_info:
                    departure_time = obj_info['actual_last_seen']
                elif 'last_seen' in obj_info:
                    departure_time = self._calculate_actual_time(obj_info['last_seen'])
                else:
                    # 如果没有记录，则使用视频结束时间
                    departure_time = video_end_time

                self._update_object_departure_time(track_id, obj_info['type'], departure_time)

        # 清空跟踪对象列表
        self.tracked_objects.clear()

        # 重置视频开始时间和初始化时间
        self.video_start_time = None
        self._init_current_time = None

        print("视频结束时的剩余数据已保存")

    def _save_traffic_flow_stats(self):
        """
        保存交通流量统计信息，时间精确到秒
        """
        if self.video_start_time:
            end_time = datetime.now()
            actual_end_time = self._calculate_actual_time(end_time)

            # 使用解析的路口ID
            road_id = getattr(self, 'current_road_id', "default_road")

            flow = Flow(
                vehicle_count=len(self.tracked_objects),
                entry_count=self.down_count,
                departure_count=self.up_count,
                stat_time=self.video_start_time.replace(microsecond=0),  # 确保精确到秒
                end_time=actual_end_time.replace(microsecond=0),         # 确保精确到秒
                road_id=road_id
            )

            self.database_service.save_traffic_flow(flow)

    def close_database_connection(self):
        """
        显式关闭数据库连接（在程序完全退出时调用）
        """
        if self.database_service is not None:
            # 保存所有剩余数据
            self._save_remaining_objects()
            self.database_service = None
            print("数据库连接已关闭")

    def _parse_video_filename(self, filename):
        """
        解析视频文件名，提取路口序号、路口名称和开始时间
        格式: 路口序号_路口名称_开始时间_结束时间
        例: 001_大成路与斗门路西口_2022-09-29-16-02-41_2022-09-29-16-03-41
        """
        # 移除文件扩展名（如果有）
        if '.' in filename:
            filename = filename.rsplit('.', 1)[0]

        # 按下划线分割
        parts = filename.split('_')

        if len(parts) >= 4:
            road_id = parts[0]
            # 路口名称可能包含下划线，需要重新组合
            # 修复：正确提取路口名称（从索引1到倒数第3个元素）
            road_name_parts = parts[1:-2]  # 除去路口序号和两个时间部分
            road_name = '_'.join(road_name_parts)

            # 解析开始时间和结束时间
            start_time_str = parts[-2]  # 倒数第二个是开始时间
            end_time_str = parts[-1]    # 最后一个是结束时间
            try:
                # 将 2022-09-29-16-02-41 转换为 datetime 对象
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d-%H-%M-%S")

                # 解析结束时间也为 datetime 对象
                end_time = datetime.strptime(end_time_str, "%Y-%m-%d-%H-%M-%S")

                # 在终端输出解析出来的时间
                print(f"解析出的开始时间: {start_time}")
                print(f"解析出的结束时间: {end_time}")

            except ValueError as e:
                print(f"解析时间出错: {e}")
                start_time = None
                end_time = None

            return {
                'road_id': road_id,
                'road_name': road_name,
                'start_time': start_time,  # 保持为 datetime 对象
                'end_time': end_time       # 保持为 datetime 对象
            }

        return None


    def _save_road_info(self):
        """
        保存路口信息到roads表
        """
        if self.current_road_id and self.current_road_name:
            try:
                # 创建Road对象
                road = Road(
                    road_id=self.current_road_id,
                    road_name=self.current_road_name
                )
                # 保存到数据库
                self.database_service.save_road(road)
                print(f"路口信息已保存: ID={self.current_road_id}, 名称={self.current_road_name}")
            except Exception as e:
                print(f"保存路口信息时出错: {e}")

    def _init_traffic_stats(self):
        """
        初始化交通流量统计相关变量
        """
        # 上一次统计时间
        self.last_stats_time = None
        # 上一次统计时的画面车辆数
        self.last_vehicle_count = 0
        # 上一次统计以来新增的车辆数
        self.vehicles_since_last_stats = 0
        # 上一次统计以来离开的车辆数
        self.departures_since_last_stats = 0
        # 累计进入车辆数
        self.total_entries = 0
        # 累计离开车辆数
        self.total_departures = 0
        # 记录暂时离开的车辆（在当前统计周期内离开的车辆）
        self.temporarily_missing_vehicles = {}  # {track_id: disappear_time}

        # 添加上一个时间段的统计数据
        self.previous_vehicle_count = 0
        self.previous_entry_count = 0
        self.previous_departure_count = 0

        # 添加用于UI显示的变量
        self.last_vehicle_count_data = 0
        self.last_entry_count_data = 0
        self.last_departure_count_data = 0

    def _periodic_traffic_stats(self):
        """
        每5秒执行一次的交通流量统计
        """
        if not hasattr(self, 'last_stats_time'):
            return

        current_time = datetime.now()
        actual_current_time = self._calculate_actual_time(current_time)

        # 如果是第一次统计或距离上次统计已超过5秒
        if self.last_stats_time is None or \
                (actual_current_time - self.last_stats_time).total_seconds() >= 5:
            # 计算当前画面中的车辆数
            current_vehicle_count = len(self.tracked_objects)

            # 计算当前周期内的进入和离开数量
            # 进入数量 = 新增车辆数
            # 离开数量 = 消失车辆数
            entry_count = self.vehicles_since_last_stats
            departure_count = self.departures_since_last_stats

            # 初始化增长率变量
            flow_growth_rate = 0
            entry_growth_rate = 0
            departure_growth_rate = 0

            if self.last_stats_time is None:
                current_flow = entry_count - departure_count
            else:
                 current_flow = self.last_vehicle_count + entry_count - departure_count

                 # 计算增长率
                 if self.previous_vehicle_count != 0:
                     flow_growth_rate = ((current_flow - self.previous_vehicle_count) / self.previous_vehicle_count) * 100
                 else:
                     flow_growth_rate = 0 if current_flow == 0 else float('inf')

                 if self.previous_entry_count != 0:
                     entry_growth_rate = ((entry_count - self.previous_entry_count) / self.previous_entry_count) * 100
                 else:
                     entry_growth_rate = 0 if entry_count == 0 else float('inf')

                 if self.previous_departure_count != 0:
                     departure_growth_rate = ((departure_count - self.previous_departure_count) / self.previous_departure_count) * 100
                 else:
                     departure_growth_rate = 0 if departure_count == 0 else float('inf')

            # 保存当前统计数据，供UI显示使用
            self.last_vehicle_count_data = current_flow
            self.last_entry_count_data = entry_count
            self.last_departure_count_data = departure_count

            # 保存增长率数据
            self.last_flow_growth_rate = flow_growth_rate
            self.last_entry_growth_rate = entry_growth_rate
            self.last_departure_growth_rate = departure_growth_rate

            # 保存当前周期的数据作为下一次计算增长率的基准
            self.previous_vehicle_count = current_flow
            self.previous_entry_count = entry_count
            self.previous_departure_count = departure_count

            # 创建流量统计记录
            flow = Flow(
                vehicle_count=current_flow,  # 当前流量
                entry_count=entry_count,  # 5秒内进入数
                departure_count=departure_count,  # 5秒内离开数
                stat_time=self.last_stats_time or self.video_start_time,  # 统计开始时间
                end_time=actual_current_time,  # 统计结束时间
                road_id=self.current_road_id
            )

            # 保存到数据库（只有当有统计数据或强制保存时才保存）
            if entry_count > 0 or departure_count > 0 or self.last_stats_time is not None:
                self.database_service.save_traffic_flow(flow)
                print(f"保存流量统计: 车辆数={current_flow}, 进入={entry_count}, 离开={departure_count}")

            # 更新统计变量
            self.last_stats_time = actual_current_time
            self.last_vehicle_count = current_flow
            self.vehicles_since_last_stats = 0  # 重置计数器
            self.departures_since_last_stats = 0  # 重置计数器

    def get_traffic_stats_for_ui(self):
        """
        获取用于UI显示的交通流量统计数据
        :return: 包含所有统计数据的字典
        """

        # 格式化增长率显示
        def format_growth_rate(rate):
            if rate == float('inf') or rate == float('-inf'):
                return "0.00%"  # 无穷大显示为0.00%
            elif rate > 0:
                return f"{rate:.1f}%".replace('.', '.')
            elif rate < 0:
                return f"{rate:.1f}%".replace('.', '.')
            else:
                return "0.00%"


        stats = {
            'total_flow': str(self.last_vehicle_count_data) if hasattr(self, 'last_vehicle_count_data') else "0",
            'entry_count': str(self.last_entry_count_data) if hasattr(self, 'last_entry_count_data') else "0",
            'departure_count': str(self.last_departure_count_data) if hasattr(self,
                                                                              'last_departure_count_data') else "0",
            'total_flow_growth': format_growth_rate(self.last_flow_growth_rate) if hasattr(self,
                                                                                           'last_flow_growth_rate') else "00.0%",
            'entry_growth': format_growth_rate(self.last_entry_growth_rate) if hasattr(self,
                                                                                       'last_entry_growth_rate') else "00.0%",
            'departure_growth': format_growth_rate(self.last_departure_growth_rate) if hasattr(self,
                                                                                               'last_departure_growth_rate') else "00.0%"
        }

        return stats


