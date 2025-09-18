# file: src/services/violation.py
import sqlite3
import os
import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.solutions import speed_estimation
from collections import defaultdict, deque
import time
from shapely.geometry import LineString, Point
from tqdm import tqdm
from datetime import datetime

# 交通违规检测器：闯红灯，超速，逆行，
class TrafficViolationDetector:
    def __init__(self):

        # 初始化YOLO模型 - 修复路径问题
        model_path = os.path.join(os.path.dirname(__file__), "yolov10-main", "yolov10l.pt")
        if not os.path.exists(model_path):
            # 如果模型文件不存在，使用相对路径
            model_path = "yolov10-main/yolov10l.pt"
        self.model = YOLO(model_path)

        # 初始化交通类别映射
        self.class_map = {
            0: 'person',
            2: 'car', 3: 'motorcycle',
            5: 'bus', 7: 'truck',
            9: 'traffic_light'
        }

        # 初始化数据记录结构
        self.track_history = defaultdict(lambda: deque(maxlen=30))
        self.violation_records = []
        self.frame_count = 0
        self.fps = 30  # 默认帧率为30

        # 初始化车道方向(逆行)
        self.lane_directions = [1, 0]

        # 初始化停止线、信号灯状态（闯红灯）
        self.stop_line = [(0, 370), (600,380)]
        self.signal_state = "Unknown"  # 当前帧即时判定
        self.signal_state_history = deque(maxlen=7)  # TL状态平滑
        self.stable_signal_state = "Unknown"  # 稳定后的TL状态

        # 初始化速度估算器、最大速度(km/h)（超速）
        self.speed_estimator = speed_estimation.SpeedEstimator()
        self.max_speed = 60

        # 违规截图输出目录
        self.run_red_light_dir = os.path.join(os.path.dirname(__file__), "yolov10-main", "running_red_light")
        os.makedirs(self.run_red_light_dir, exist_ok=True)

    def classify_traffic_light_color(self, frame, box):
        # 获取信号灯区域
        x1, y1, x2, y2 = box
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame.shape[1] - 1, x2)
        y2 = min(frame.shape[0] - 1, y2)
        # 转换为HSV颜色空间
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        roi_hsv = frame_hsv[y1:y2, x1:x2]
        if roi_hsv.size == 0:
            return "Unknown", (255, 255, 255)
        # HSV 阈值
        minRedHSV1 = np.array([0, 80, 80])
        maxRedHSV1 = np.array([10, 255, 255])
        minRedHSV2 = np.array([160, 80, 80])
        maxRedHSV2 = np.array([180, 255, 255])
        minGreenHSV = np.array([45, 60, 60])
        maxGreenHSV = np.array([90, 255, 255])
        minYellowHSV = np.array([15, 80, 80])
        maxYellowHSV = np.array([35, 255, 255])
        mask_red = cv2.inRange(roi_hsv, minRedHSV1, maxRedHSV1) | cv2.inRange(roi_hsv, minRedHSV2, maxRedHSV2)
        mask_green = cv2.inRange(roi_hsv, minGreenHSV, maxGreenHSV)
        mask_yellow = cv2.inRange(roi_hsv, minYellowHSV, maxYellowHSV)
        num_red_pixels = cv2.countNonZero(mask_red)
        num_green_pixels = cv2.countNonZero(mask_green)
        num_yellow_pixels = cv2.countNonZero(mask_yellow)

        # 使用面积占比，避免框大小变化导致抖动
        roi_area = max(1, (y2 - y1) * (x2 - x1))
        red_ratio = num_red_pixels / roi_area
        green_ratio = num_green_pixels / roi_area
        yellow_ratio = num_yellow_pixels / roi_area

        state = "Unknown"
        box_color = (255, 255, 255)

        # 动态阈值与相对比较，要求一定优势
        min_ratio = 0.01  # 1% 面积阈值，防止微小噪声
        dominance = 1.3   # 主导比例

        if red_ratio > min_ratio and red_ratio > green_ratio * dominance and red_ratio > yellow_ratio * dominance:
            state = "Red"
            box_color = (0, 0, 255)
        elif green_ratio > min_ratio and green_ratio > red_ratio * dominance and green_ratio > yellow_ratio * dominance:
            state = "Green"
            box_color = (0, 255, 0)
        elif yellow_ratio > min_ratio and yellow_ratio > red_ratio * dominance and yellow_ratio > green_ratio * dominance:
            state = "Yellow"
            box_color = (0, 255, 255)

        return state, box_color

    def check_run_red_light(self, frame, signal_box, track_id, current_pos):

        # 当前帧信号灯颜色
        state, box_color = self.classify_traffic_light_color(frame, signal_box)

        # TL状态平滑：加入历史并取多数表决
        self.signal_state = state
        self.signal_state_history.append(state)
        if len(self.signal_state_history) >= 3:
            counts = {
                "Red": sum(s == "Red" for s in self.signal_state_history),
                "Green": sum(s == "Green" for s in self.signal_state_history),
                "Yellow": sum(s == "Yellow" for s in self.signal_state_history),
                "Unknown": sum(s == "Unknown" for s in self.signal_state_history),
            }
            self.stable_signal_state = max(counts, key=counts.get)
        else:
            self.stable_signal_state = state

        # 绘制信号灯边界框和状态（使用稳定状态）
        x1, y1, x2, y2 = signal_box
        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
        cv2.putText(frame, f"TL: {self.stable_signal_state}",
                    (x1, max(0, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

        # 判断车辆是否在红灯时穿过停止线(若为黄绿灯、车辆为静止则不判定)
        if self.stable_signal_state != "Red":
            return False
        track = self.track_history[track_id]
        if len(track) < 10:
            return False
        stop_line = LineString(self.stop_line)
        vehicle_path = LineString([Point(track[-10]), Point(current_pos)])
        if stop_line.intersects(vehicle_path):
            return True
        return False

    def check_speeding(self, frame, track_id, results):
        # 估算车辆速度，判断是否超速
        track = self.track_history[track_id]
        if len(track) < 10:
            return False, 0
        # 估算速度
        im, speed = self.speed_estimator.estimate_speed(frame, results)
        if speed > self.max_speed:
            return True, speed
        return False, speed

    def _vector_angle(self, v1, v2):
        # 计算两个向量的夹角
        unit_v1 = v1 / np.linalg.norm(v1)
        unit_v2 = v2 / np.linalg.norm(v2)
        degree = np.degrees(np.arccos(np.clip(np.dot(unit_v1, unit_v2), -1.0, 1.0)))
        return degree

    def  check_reverse_driving(self, track_id):
        # 判断车辆是否逆行
        track = self.track_history[track_id]
        # 若车辆为静止则不判定
        if len(track) < 10:
            return False
        # 计算车辆运动方向
        start_point = np.array(track[-10])
        end_point = np.array(track[-1])
        direction = end_point - start_point
        # 与道路方向对比
        lane_direction = np.array(self.lane_directions)
        angle = self._vector_angle(direction, lane_direction)
        if angle > 120:
            return True
        return False

    def save_violation(self, violation_type, frame, bbox):
        """
        保存违规记录到 SQLite 数据库
        :param violation_type: 违规类型
        :param frame: 当前帧图像
        :param bbox: 车辆的边界框 (x1, y1, x2, y2)
        """
        # 仅对闯红灯进行截图保存
        if violation_type != "run_red_light":
            return

        h, w = frame.shape[:2]
        x1, y1, x2, y2 = bbox
        # 边界裁剪与有效性检查
        x1 = max(0, min(w - 1, x1))
        y1 = max(0, min(h - 1, y1))
        x2 = max(0, min(w, x2))
        y2 = max(0, min(h, y2))
        if x2 <= x1 or y2 <= y1:
            return

        vehicle_image = frame[y1:y2, x1:x2]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"run_red_{ts}_{x1}-{y1}-{x2}-{y2}.jpg"
        save_path = os.path.join(self.run_red_light_dir, filename)
        cv2.imwrite(save_path, vehicle_image)

        # 记录到内存，用于结束时汇总打印（若有）
        self.violation_records.append({
            "type": violation_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bbox": (x1, y1, x2, y2),
            "path": save_path
        })

    def process_frame(self, frame, fps):
        ###
        # 核心帧处理：跟踪、检测与可视化
        self.frame_count += 1
        self.fps = fps if fps > 0 else self.fps

        # 目标检测与跟踪（仅车辆与信号灯类）
        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=list(self.class_map.keys())
        )

        current_violations = []

        # 解析检测结果并更新轨迹
        if results and results[0].boxes is not None and results[0].boxes.id is not None:
            for box in results[0].boxes:
                if box.id is None:
                    continue
                track_id = int(box.id)
                class_id = int(box.cls)
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                center = (center_x, center_y)

                # 更新轨迹
                self.track_history[track_id].append(center)

                # 闯红灯检测：若当前帧存在交通灯框
                if class_id in [2, 3, 5, 7]:
                    # 在结果中查找任意交通灯框以判定信号
                    signal_box = None
                    for sb in results[0].boxes:
                        if int(sb.cls) == 9:
                            sx1, sy1, sx2, sy2 = map(int, sb.xyxy[0].cpu().numpy())
                            signal_box = (sx1, sy1, sx2, sy2)
                            break

                    if signal_box is not None:
                        if self.check_run_red_light(frame, signal_box, track_id, center):
                            current_violations.append(("run_red_light", track_id))

                    # 逆行检测
                    if self.check_reverse_driving(track_id):
                        current_violations.append(("reverse_drive", track_id))

                # 绘制结果
                color = (0, 255, 0)
                violation_label = None
                for violation_type, v_id in current_violations:
                    if v_id == track_id:
                        color = (0, 0, 255)
                        violation_label = violation_type
                        # 保存违规记录
                        self.save_violation(violation_label, frame, (x1, y1, x2, y2))
                        break

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                if violation_label:
                    cv2.putText(frame, violation_label, (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # 轨迹可视化
                if len(self.track_history[track_id]) > 1:
                    pts = np.array(self.track_history[track_id], dtype=np.int32)
                    cv2.polylines(frame, [pts], False, (0, 255, 255), 2)

        # 绘制停止线
        cv2.line(frame, tuple(self.stop_line[0]), tuple(self.stop_line[1]), (255, 0, 0), 2)

        # 显示全局信号灯状态文字（使用稳定状态）
        cv2.putText(frame, f"TL: {self.stable_signal_state}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 0, 255) if self.stable_signal_state == "Red" else (0, 255, 0), 2)

        return frame
        ###

def main():
    # 初始化检测器
    detector = TrafficViolationDetector()

    # 视频输入源
    cap = cv2.VideoCapture("../videos/car2.mp4")
    # 初始化视频写入器（延迟到读取到第一帧后设置尺寸和FPS）
    writer = None
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    # 进度信息
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        total_frames = None
    # 创建单个进度条
    pbar = tqdm(total=total_frames, desc="Processing", unit="frame") if total_frames else tqdm(desc="Processing", unit="frame")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:
                fps = 30
        # 处理帧并检测违规
        result_frame = detector.process_frame(frame, fps)

        # 初始化并写入输出视频
        if writer is None:
            height, width = result_frame.shape[:2]
            writer = cv2.VideoWriter("yolov10-main/result.mp4", fourcc, fps, (width, height))
        writer.write(result_frame)

        # 显示结果
        cv2.imshow("Traffic Violation Detection", result_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 更新进度条
        pbar.update(1)

    cap.release()
    if writer is not None:
        writer.release()
    # 关闭进度条
    pbar.close()
    # 打印闯红灯违规信息汇总
    red_violations = [v for v in detector.violation_records if v.get("type") == "run_red_light"]
    if red_violations:
        print("\n闯红灯违规汇总:")
        for i, v in enumerate(red_violations, 1):
            x1, y1, x2, y2 = v.get("bbox", (0, 0, 0, 0))
            path = v.get("path", "")
            print(f"{i}. 时间: {v.get('timestamp')}  车辆框: ({x1},{y1},{x2},{y2})  截图: {path}")
    else:
        print("\n本次处理未检测到闯红灯违规。")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
