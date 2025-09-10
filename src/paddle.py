import os
import subprocess
import re
import cv2
import numpy as np
from ultralytics import YOLO
from tqdm import tqdm

# 运行时自动检测交通灯和斑马线位置
DEFAULT_TL_BOX = None  # (x1, y1, x2, y2)
DEFAULT_ZEBRA_BOX = None  # (x1, y1, x2, y2)

def classify_traffic_light_color(frame, box):
    x1, y1, x2, y2 = box
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(frame.shape[1] - 1, x2)
    y2 = min(frame.shape[0] - 1, y2)
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
    color_detected = "Unknown"
    box_color = (0, 255, 0)
    if num_red_pixels > num_green_pixels * 1.5 and num_red_pixels > num_yellow_pixels * 1.5 and num_red_pixels > 20:
        color_detected = "Red"
        box_color = (0, 0, 255)
    elif num_green_pixels > num_red_pixels * 1.5 and num_green_pixels > num_yellow_pixels * 1.5 and num_green_pixels > 20:
        color_detected = "Green"
        box_color = (0, 255, 0)
    elif num_yellow_pixels > num_red_pixels * 1.5 and num_yellow_pixels > num_green_pixels * 1.5 and num_yellow_pixels > 20:
        color_detected = "Yellow"
        box_color = (0, 255, 255)
    return color_detected, box_color

def detect_traffic_lights(frame):
    # 使用YOLO检测交通灯（COCO 类别 9）
    global yolo_model
    if 'yolo_model' not in globals() or yolo_model is None:
        yolo_model = YOLO("./weights/yolov10n.pt")
    results = yolo_model.predict(frame, conf=0.25, verbose=False)
    boxes = []
    confs = []
    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            cls_id = int(box.cls[0]) if hasattr(box, 'cls') else -1
            if cls_id == 9:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                boxes.append((int(x1), int(y1), int(x2), int(y2)))
                confs.append(float(box.conf[0]) if hasattr(box, 'conf') else 0.0)
    return boxes, confs

def detect_zebra_crossing(frame):
    # 基于边缘和直线的启发式斑马线检测，返回一个大致区域框
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=int(0.15 * frame.shape[1]), maxLineGap=20)
    if lines is None:
        return None
    horizontal_lines = []
    for l in lines[:, 0, :]:
        x1, y1, x2, y2 = l
        if x2 == x1:
            continue
        slope = (y2 - y1) / (x2 - x1 + 1e-6)
        if abs(slope) < 0.2:  # 近似水平
            horizontal_lines.append((x1, y1, x2, y2))
    if len(horizontal_lines) < 5:
        return None
    # 按y聚类
    horizontal_lines.sort(key=lambda p: (p[1] + p[3]) / 2)
    clusters = []
    current = [horizontal_lines[0]]
    for line in horizontal_lines[1:]:
        y_prev = (current[-1][1] + current[-1][3]) / 2
        y_curr = (line[1] + line[3]) / 2
        if abs(y_curr - y_prev) <= 15:
            current.append(line)
        else:
            clusters.append(current)
            current = [line]
    clusters.append(current)
    # 选择包含线段最多且跨度较大的簇
    best = max(clusters, key=lambda c: len(c))
    if len(best) < 5:
        return None
    min_x = min(min(p[0], p[2]) for p in best)
    max_x = max(max(p[0], p[2]) for p in best)
    min_y = int(min(min(p[1], p[3]) for p in best))
    max_y = int(max(max(p[1], p[3]) for p in best))
    if (max_x - min_x) < 0.4 * frame.shape[1]:
        return None
    pad_y = 20
    min_y = max(0, min_y - pad_y)
    max_y = min(frame.shape[0] - 1, max_y + pad_y)
    return (min_x, min_y, max_x, max_y)

def detect_pedestrians(frame_path, temp_folder):
    # 兼容旧签名，忽略不再需要的参数，使用YOLOv10n直接推理
    # 加载全局模型
    global yolo_model
    if 'yolo_model' not in globals() or yolo_model is None:
        yolo_model = YOLO("yolov10l.pt")
    # 读取帧（支持传入路径或已经是图像数组的情况）
    if isinstance(frame_path, str):
        frame = cv2.imread(frame_path)
    else:
        frame = frame_path
    # 推理，仅保留person类别（COCO中为0）
    results = yolo_model.predict(frame, conf=0.25, verbose=False)
    bboxes = []
    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            cls_id = int(box.cls[0]) if hasattr(box, 'cls') else -1
            if cls_id == 0:  # person 类别
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                bboxes.append((int(x1), int(y1), int(x2), int(y2)))
    return bboxes

def process_uploaded_video(input_video, output_video):
    # 输出视频路径处理
    output_video_path = os.path.dirname(output_video)
    if output_video_path:
        if not os.path.exists(output_video_path):
            os.makedirs(output_video_path, exist_ok=True)
    # 输入视频存在性检查
    if not os.path.exists(input_video):
        print(f"Error: Input video not found: {input_video}")
        return
    # 初始化YOLOv10n模型（仅初始化一次）
    global yolo_model
    if 'yolo_model' not in globals() or yolo_model is None:
        yolo_model = YOLO("./weights/yolov10n.pt")
    # 打开视频文件
    cap = cv2.VideoCapture(input_video)
    # 检查视频是否成功打开
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()
    # 获取视频的帧率和尺寸
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1e-3:
        fps = 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 定义视频编码器和创建 VideoWriter 对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    frame_count = 0
    # 打印进度条
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) > 0 else None
    pbar = tqdm(total=total_frames, desc="Processing", unit="frame")
    # 每隔一秒钟进行一次行人检测
    pedestrian_detection_frame_interval = int(fps)  # 每隔一秒钟进行一次行人检测
    last_pedestrians = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # 动态检测交通灯框
        tl_boxes, tl_confs = detect_traffic_lights(frame)
        traffic_light_color = "Unknown"
        if tl_boxes:
            # 选择置信度最高的交通灯
            best_idx = int(np.argmax(np.array(tl_confs))) if len(tl_confs) == len(tl_boxes) else 0
            tl_box = tl_boxes[best_idx]
            traffic_light_color, box_color = classify_traffic_light_color(frame, tl_box)
            cv2.rectangle(frame, (tl_box[0], tl_box[1]), (tl_box[2], tl_box[3]), box_color, 2)
            cv2.putText(frame, traffic_light_color, (tl_box[0], max(0, tl_box[1] - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, box_color, 2)
        else:
            box_color = (255, 255, 255)
        # 检测斑马线区域
        zebra_box = detect_zebra_crossing(frame)
        if zebra_box is not None:
            zx1, zy1, zx2, zy2 = zebra_box
            cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (255, 255, 0), 2)
        # 每隔一定帧进行一次行人检测
        if frame_count % pedestrian_detection_frame_interval == 0:
            last_pedestrians = detect_pedestrians(frame, None)
        # 标注行人框：默认绿色；若红灯且在斑马线则标注红色并提示
        for (x1, y1, x2, y2) in last_pedestrians:
            draw_color = (0, 255, 0)
            label_text = "person"
            if traffic_light_color == "Red" and zebra_box is not None:
                zx1, zy1, zx2, zy2 = zebra_box
                left_bottom_in_zebra = zx1 <= x1 < zx2 and zy1 <= y2 < zy2
                right_bottom_in_zebra = zx1 <= x2 < zx2 and zy1 <= y2 < zy2
                if left_bottom_in_zebra or right_bottom_in_zebra:
                    draw_color = (0, 0, 255)
                    label_text = "Running Red Light!"
                    print(f"Frame {frame_count}: Running Red Light! Pedestrian detected at ({x1}, {y2}) or ({x2}, {y2}).")
            cv2.rectangle(frame, (x1, y1), (x2, y2), draw_color, 2)
            cv2.putText(frame, label_text, (x1, max(0, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, draw_color, 2)
        # 写入所有帧到输出视频（包括绘制了边框的帧）
        out.write(frame)
        frame_count += 1
        pbar.update(1)
    # 释放一切资源
    cap.release()
    out.release()
    pbar.close()
    # 结束

if __name__ == "__main__":
    input_video = "./video/paddle_in.mp4"
    output_video = "paddle_out.mp4"
    process_uploaded_video(input_video, output_video)