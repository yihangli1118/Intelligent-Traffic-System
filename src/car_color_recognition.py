import cv2
import numpy as np
from sklearn.cluster import KMeans
import os

def extract_car_region(image_path):
    """从图像中提取可能的车身区域"""
    img = cv2.imread(image_path) if isinstance(image_path, str) else image_path

    # 将图像转换为HSV颜色空间
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 简单的方法：取图像中间部分作为车身区域
    h, w = img.shape[:2]
    center_x, center_y = w // 2, h // 2

    # 取中心区域，避开车牌和背景
    roi_width, roi_height = int(w * 0.5), int(h * 0.5)
    roi_x = center_x - roi_width // 2
    roi_y = center_y - roi_height // 2

    # 确保ROI在图像范围内
    roi_x = max(0, roi_x)
    roi_y = max(0, roi_y)
    roi_width = min(w - roi_x, roi_width)
    roi_height = min(h - roi_y, roi_height)

    car_region = img[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
    return car_region

def get_dominant_color(image):
    """获取图像中的主要颜色"""
    # 将图像重塑为二维数组
    pixels = image.reshape(-1, 3)

    # 使用K-means聚类找到主要颜色
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(pixels)

    # 找出最大的聚类
    counts = np.bincount(kmeans.labels_)
    dominant_cluster = np.argmax(counts)

    # 返回主要颜色
    dominant_color = kmeans.cluster_centers_[dominant_cluster].astype(int)
    return dominant_color

def color_name_mapping(bgr_color):
    """将BGR颜色映射到颜色名称"""
    # 转换为HSV颜色空间以更好地处理颜色
    hsv_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)[0][0]
    h, s, v = hsv_color

    # 定义颜色范围
    color_ranges = {
        "黑色": (h, s < 50, v < 100),
        "白色": (h, s < 30, v > 200),
        "灰色": (h, s < 30, 100 <= v <= 200),
        "红色": ((h < 10 or h > 170), s > 100, v > 100),
        "蓝色": (100 < h < 140, s > 50, v > 50),
        "绿色": (40 < h < 80, s > 50, v > 50),
        "黄色": (20 < h < 40, s > 100, v > 100),
        "棕色": (10 < h < 20, s > 100, v < 150),
        "橙色": (10 < h < 25, s > 100, v > 150),
        "紫色": (140 < h < 170, s > 50, v > 50),
    }

    # 检查颜色是否在各个范围内
    for color_name, (h_condition, s_condition, v_condition) in color_ranges.items():
        if s_condition and v_condition:
            if isinstance(h_condition, bool) or h_condition:
                return color_name

    # 如果没有匹配的颜色
    # 简单区分
    if v < 100:
        return "黑色"
    elif s < 50 and v > 180:
        return "白色"
    elif s < 50:
        return "灰色"
    else:
        return "未知颜色"

def recognize_car_color(image_path):
    """识别车辆颜色"""
    try:
        # 提取车身区域
        car_region = extract_car_region(image_path)

        # 应用高斯模糊以减少噪声
        blurred = cv2.GaussianBlur(car_region, (5, 5), 0)

        # 获取主要颜色
        dominant_color = get_dominant_color(blurred)

        # 映射到颜色名称
        color_name = color_name_mapping(dominant_color)

        return color_name
    except Exception as e:
        print(f"车身颜色识别错误: {str(e)}")
        return "未知颜色"

# 如果作为独立脚本运行，可以进行测试
if __name__ == "__main__":
    test_image = "imgs/test.jpg"  # 测试图像路径
    if os.path.exists(test_image):
        color = recognize_car_color(test_image)
        print(f"识别到的车身颜色: {color}")
    else:
        print(f"测试图像 {test_image} 不存在")