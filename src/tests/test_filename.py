# filename.py
from datetime import datetime

def parse_video_filename(filename):
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
        # 提取路口名称（从索引1到倒数第3个元素）
        road_name_parts = parts[1:-2]  # 除去路口序号和两个时间部分
        road_name = '_'.join(road_name_parts)

        # 解析开始时间和结束时间
        start_time_str = parts[-2]  # 倒数第二个是开始时间
        end_time_str = parts[-1]    # 最后一个是结束时间
        print(start_time_str)
        print(end_time_str)
        try:
            # 将 2022-09-29-16-02-41 转换为 2022-09-29 16:02:41
            # 正确的字符串替换方法
            # start_time_formatted = start_time_str.replace('-', ' ', 2).replace('-', ':', 3)
            # start_time = datetime.strptime(start_time_formatted, '%Y %m %d %H:%M:%S')
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d-%H-%M-%S").strftime("%Y %m %d %H:%M:%S")

            # 解析结束时间
            # end_time_formatted = end_time_str.replace('-', ' ', 2).replace('-', ':', 3)
            # end_time = datetime.strptime(end_time_formatted, '%Y %m %d %H:%M:%S')
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d-%H-%M-%S").strftime("%Y %m %d %H:%M:%S")

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
            'start_time': start_time,
            'end_time': end_time
        }

    return None

def main():
    # 测试用例
    test_filenames = [
        "001_大成路与斗门路西口_2022-09-29-16-02-41_2022-09-29-16-03-41",
        "002_中山路与解放路交叉口_2023-05-15-08-30-00_2023-05-15-08-35-00",
        "003_人民路与建设路东口_2023-12-01-17-45-30_2023-12-01-17-46-30.mp4",
    ]

    for filename in test_filenames:
        print(f"\n测试文件名: {filename}")
        result = parse_video_filename(filename)
        if result:
            print(f"解析结果:")
            print(f"  路口序号: {result['road_id']}")
            print(f"  路口名称: {result['road_name']}")
            print(f"  开始时间: {result['start_time']}")
            print(f"  结束时间: {result['end_time']}")
        else:
            print("解析失败")

if __name__ == "__main__":
    main()
