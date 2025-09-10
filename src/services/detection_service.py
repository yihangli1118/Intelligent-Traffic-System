# file: src/services/detection_service.py
import os
import sys
import numpy as np
import cv2

# 添加targetDetect到路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'targetDetect'))

from targetDetect.detector import Detector
import targetDetect.tracker as tracker

class DetectionService:
    def __init__(self):
        # 初始化检测器
        self.detector = Detector()

        # 创建撞线检测区域
        self._create_detection_areas()

        # 初始化跟踪列表
        self.list_overlapping_blue_polygon = []
        self.list_overlapping_yellow_polygon = []

        # 计数器
        self.down_count = 0
        self.up_count = 0

    def _create_detection_areas(self):
        """
        创建检测区域
        """
        # 根据视频尺寸，填充一个polygon，供撞线计算使用
        mask_image_temp = np.zeros((1080, 1920), dtype=np.uint8)

        # 初始化2个撞线polygon
        list_pts_blue = [[204, 305], [227, 431], [605, 522], [1101, 464], [1900, 601], [1902, 495], [1125, 379], [604, 437],
                         [299, 375], [267, 289]]
        ndarray_pts_blue = np.array(list_pts_blue, np.int32)
        self.polygon_blue_value_1 = cv2.fillPoly(mask_image_temp, [ndarray_pts_blue], color=1)
        self.polygon_blue_value_1 = self.polygon_blue_value_1[:, :, np.newaxis]

        # 填充第二个polygon
        mask_image_temp = np.zeros((1080, 1920), dtype=np.uint8)
        list_pts_yellow = [[181, 305], [207, 442], [603, 544], [1107, 485], [1898, 625], [1893, 701], [1101, 568],
                           [594, 637], [118, 483], [109, 303]]
        ndarray_pts_yellow = np.array(list_pts_yellow, np.int32)
        self.polygon_yellow_value_2 = cv2.fillPoly(mask_image_temp, [ndarray_pts_yellow], color=2)
        self.polygon_yellow_value_2 = self.polygon_yellow_value_2[:, :, np.newaxis]

        # 撞线检测用mask，包含2个polygon，（值范围 0、1、2），供撞线计算使用
        self.polygon_mask_blue_and_yellow = self.polygon_blue_value_1 + self.polygon_yellow_value_2

        # 缩小尺寸，1920x1080->960x540
        self.polygon_mask_blue_and_yellow = cv2.resize(self.polygon_mask_blue_and_yellow, (960, 540))

        # 蓝色盘 b,g,r
        blue_color_plate = [255, 0, 0]
        # 蓝 polygon图片
        blue_image = np.array(self.polygon_blue_value_1 * blue_color_plate, np.uint8)

        # 黄色盘
        yellow_color_plate = [0, 255, 255]
        # 黄 polygon图片
        yellow_image = np.array(self.polygon_yellow_value_2 * yellow_color_plate, np.uint8)

        # 彩色图片（值范围 0-255）
        self.color_polygons_image = blue_image + yellow_image
        # 缩小尺寸，1920x1080->960x540
        self.color_polygons_image = cv2.resize(self.color_polygons_image, (960, 540))

    def process_frame(self, frame):
        """
        处理单帧图像，进行目标检测和跟踪
        """
        # 缩小尺寸，1920x1080->960x540
        im = cv2.resize(frame, (960, 540))

        list_bboxs = []
        bboxes = self.detector.detect(im)

        # 如果画面中有bbox
        if len(bboxes) > 0:
            list_bboxs = tracker.update(bboxes, im)
            # 画框
            output_image_frame = tracker.draw_bboxes(im, list_bboxs, line_thickness=None)
        else:
            # 如果画面中没有bbox
            output_image_frame = im

        # 添加多边形区域到图像上
        output_image_frame = cv2.add(output_image_frame, self.color_polygons_image)

        if len(list_bboxs) > 0:
            # 判断撞线
            for item_bbox in list_bboxs:
                x1, y1, x2, y2, label, track_id = item_bbox

                # 撞线检测点，(x1，y1)，y方向偏移比例 0.0~1.0
                y1_offset = int(y1 + ((y2 - y1) * 0.6))

                # 撞线的点
                y = y1_offset
                x = x1

                if self.polygon_mask_blue_and_yellow[y, x] == 1:
                    # 如果撞蓝polygon
                    if track_id not in self.list_overlapping_blue_polygon:
                        self.list_overlapping_blue_polygon.append(track_id)

                    # 判断黄polygon list里是否有此track_id
                    if track_id in self.list_overlapping_yellow_polygon:
                        # 离开+1
                        self.up_count += 1
                        # 删除黄polygon list中的此id
                        self.list_overlapping_yellow_polygon.remove(track_id)

                elif self.polygon_mask_blue_and_yellow[y, x] == 2:
                    # 如果撞黄polygon
                    if track_id not in self.list_overlapping_yellow_polygon:
                        self.list_overlapping_yellow_polygon.append(track_id)

                    # 判断蓝polygon list里是否有此track_id
                    if track_id in self.list_overlapping_blue_polygon:
                        # 进入+1
                        self.down_count += 1
                        # 删除蓝polygon list中的此id
                        self.list_overlapping_blue_polygon.remove(track_id)

            # 清除无用id
            list_overlapping_all = self.list_overlapping_yellow_polygon + self.list_overlapping_blue_polygon
            for id1 in list_overlapping_all:
                is_found = False
                for _, _, _, _, _, bbox_id in list_bboxs:
                    if bbox_id == id1:
                        is_found = True
                        break
                if not is_found:
                    # 如果没找到，删除id
                    if id1 in self.list_overlapping_yellow_polygon:
                        self.list_overlapping_yellow_polygon.remove(id1)
                    if id1 in self.list_overlapping_blue_polygon:
                        self.list_overlapping_blue_polygon.remove(id1)

            # 清空list
            list_overlapping_all.clear()
            list_bboxs.clear()
        else:
            # 如果图像中没有任何的bbox，则清空list
            self.list_overlapping_blue_polygon.clear()
            self.list_overlapping_yellow_polygon.clear()

        # 在图像上显示计数
        font_draw_number = cv2.FONT_HERSHEY_SIMPLEX
        draw_text_postion = (int(960 * 0.01), int(540 * 0.05))
        text_draw = 'DOWN: ' + str(self.down_count) + ' , UP: ' + str(self.up_count)
        output_image_frame = cv2.putText(img=output_image_frame, text=text_draw,
                                         org=draw_text_postion,
                                         fontFace=font_draw_number,
                                         fontScale=1, color=(255, 255, 255), thickness=2)

        return output_image_frame

    def reset_counters(self):
        """
        重置计数器
        """
        self.down_count = 0
        self.up_count = 0
        self.list_overlapping_blue_polygon.clear()
        self.list_overlapping_yellow_polygon.clear()
