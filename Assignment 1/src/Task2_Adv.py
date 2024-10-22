import pandas as pd
from datetime import datetime
from rtree import index
import time

# 设置 pandas 显示选项，确保显示所有列
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.expand_frame_repr', False)  # 防止换行显示
pd.set_option('display.max_rows', 50)  # 如果你想显示更多行，可以修改这里


def load_grid_from_file(filename):
    grid = {}  # 用于存储所有非空的网格单元数据
    min_lon, max_lon = None, None
    min_lat, max_lat = None, None
    min_time, max_time = None, None

    with open(filename, 'r') as f:
        lines = f.readlines()

        # 读取全局的最小值和最大值
        min_lon, max_lon = map(float, lines[0].strip().split(','))
        min_lat, max_lat = map(float, lines[1].strip().split(','))
        min_time, max_time = map(float, lines[2].strip().split(','))

        # 逐行解析剩下的网格数据
        i = 3
        while i < len(lines):
            # 读取网格单元的坐标 (x, y, t)
            cell_coords = lines[i].strip()
            cell_x, cell_y, cell_t = map(int, cell_coords.strip('()').split(','))
            cell_key = (cell_x, cell_y, cell_t)

            # 读取该单元格的总金额
            total_amt_in_cell = int(lines[i + 1].strip())

            # 初始化该网格单元的记录列表
            grid[cell_key] = {
                'count': total_amt_in_cell,  # total amount
                'records': []
            }

            # 从 i + 2 开始读取所有属于该网格单元的记录
            i += 2
            while i < len(lines) and not lines[i].startswith('('):
                # 每一行是 x, y, timestamp, Total_Amt
                x, y, timestamp, total_amt = map(float, lines[i].strip().split(','))
                grid[cell_key]['records'].append((x, y, timestamp, total_amt))
                i += 1  # 继续读取下一行

            # 注意此时 i 指向下一个网格单元的坐标行，继续循环处理
        return grid, (min_lon, max_lon, min_lat, max_lat, min_time, max_time)


# exact query
def exact_query_processing(grid, query_file, min_lon, max_lon, min_lat, max_lat, min_time, max_time):
    exact_results = []  # 用于存储每次查询的结果

    # 读取查询文件
    with open(query_file, 'r') as f:
        queries = f.readlines()

    for query in queries:
        # 解析查询条件：low_x, up_x, low_y, up_y, low_datetime, up_datetime
        query_parts = query.strip().split(',')
        low_x, up_x = float(query_parts[0]), float(query_parts[1])
        low_y, up_y = float(query_parts[2]), float(query_parts[3])
        low_time = datetime.strptime(query_parts[4], "%Y-%m-%d %H:%M:%S").timestamp()
        up_time = datetime.strptime(query_parts[5], "%Y-%m-%d %H:%M:%S").timestamp()

        exact_query_result = {
            'count': 0,  # 符合条件的数据数目
            'records': []  # 符合条件的每条数据
        }

        # 查询的总金额初始化为 0
        total_amount = 0

        # 遍历网格单元
        for cell_key, cell_data in grid.items():
            lon_partition, lat_partition, time_partition = cell_key

            # 检查网格单元是否与查询的地理范围和时间范围相交
            cell_status = get_cell_status(cell_key, low_x, up_x, low_y, up_y, low_time, up_time,
                                          min_lon, max_lon, min_lat, max_lat, min_time, max_time)

            if cell_status == "fully_inside":
                # fully in
                exact_query_result['count'] += cell_data['count']
                exact_query_result['records'].extend(cell_data['records'])
            elif cell_status == "partially_inside":
                # partially in
                for record in cell_data['records']:
                    lon, lat, timestamp, amount = record
                    # check each
                    if low_x <= lon <= up_x and low_y <= lat <= up_y and low_time <= timestamp <= up_time:
                        exact_query_result['count'] += 1
                        exact_query_result['records'].append(record)

        # 保存每次查询的结果
        exact_results.append(exact_query_result)

    return exact_results


def get_cell_status(cell_key, low_x, up_x, low_y, up_y, low_time, up_time,
                    min_lon, max_lon, min_lat, max_lat, min_time, max_time):
    lon_partition, lat_partition, time_partition = cell_key

    # 根据分区数计算该单元的经度、纬度、时间范围
    cell_min_lon = min_lon + (lon_partition / 100) * (max_lon - min_lon)
    cell_max_lon = min_lon + ((lon_partition + 1) / 100) * (max_lon - min_lon)

    cell_min_lat = min_lat + (lat_partition / 100) * (max_lat - min_lat)
    cell_max_lat = min_lat + ((lat_partition + 1) / 100) * (max_lat - min_lat)

    cell_min_time = min_time + (time_partition / 100) * (max_time - min_time)
    cell_max_time = min_time + ((time_partition + 1) / 100) * (max_time - min_time)

    # 检查网格单元是否完全包含在查询范围内
    if (low_x <= cell_min_lon and cell_max_lon <= up_x and
            low_y <= cell_min_lat and cell_max_lat <= up_y and
            low_time <= cell_min_time and cell_max_time <= up_time):
        return "fully_inside"

    # 检查网格单元是否部分包含在查询范围内
    if (cell_max_lon >= low_x and cell_min_lon <= up_x and
            cell_max_lat >= low_y and cell_min_lat <= up_y and
            cell_max_time >= low_time and cell_min_time <= up_time):
        return "partially_inside"

    # 网格单元不在查询范围内
    return "outside"


# approximate query
def approximate_query_processing(grid, query_file, min_lon, max_lon, min_lat, max_lat, min_time, max_time):
    approximate_results = []  # 用于存储每次查询的结果

    # 读取查询文件
    with open(query_file, 'r') as f:
        queries = f.readlines()

    for query in queries:
        # 解析查询条件：low_x, up_x, low_y, up_y, low_datetime, up_datetime
        query_parts = query.strip().split(',')
        low_x, up_x = float(query_parts[0]), float(query_parts[1])
        low_y, up_y = float(query_parts[2]), float(query_parts[3])
        low_time = datetime.strptime(query_parts[4], "%Y-%m-%d %H:%M:%S").timestamp()
        up_time = datetime.strptime(query_parts[5], "%Y-%m-%d %H:%M:%S").timestamp()

        approximate_query_result = {
            'count': 0,  # 符合条件的数据数目
            'records': []  # 符合条件的每条数据
        }

        # 查询的总金额初始化为 0
        total_amount = 0

        # 遍历网格单元
        for cell_key, cell_data in grid.items():
            lon_partition, lat_partition, time_partition = cell_key

            # 检查网格单元是否与查询的地理范围和时间范围相交
            cell_status, f = get_cell_status_and_fraction(cell_key, low_x, up_x, low_y, up_y, low_time, up_time,
                                                          min_lon, max_lon, min_lat, max_lat, min_time, max_time)

            if cell_status == "fully_inside":
                # 如果网格单元完全包含在查询范围内，直接使用 Total_Amt_in_cell
                approximate_query_result['count'] += cell_data['count']
                approximate_query_result['records'].extend(cell_data['records'])
            elif cell_status == "partially_inside":
                # 如果部分包含，则将 f * Total_Amt_in_cell 加入结果
                approximate_query_result['count'] += f * cell_data['count']
                approximate_query_result['records'].append(f"This cell ({lon_partition}, {lat_partition}, {time_partition}) is partially_inside.")
        approximate_query_result['count'] = round(approximate_query_result['count'])
        # 保存每次查询的结果
        approximate_results.append(approximate_query_result)

    return approximate_results


def get_cell_status_and_fraction(cell_key, low_x, up_x, low_y, up_y, low_time, up_time,
                                 min_lon, max_lon, min_lat, max_lat, min_time, max_time):
    lon_partition, lat_partition, time_partition = cell_key

    # 根据分区数计算该单元的经度、纬度、时间范围
    cell_min_lon = min_lon + (lon_partition / 100) * (max_lon - min_lon)
    cell_max_lon = min_lon + ((lon_partition + 1) / 100) * (max_lon - min_lon)

    cell_min_lat = min_lat + (lat_partition / 100) * (max_lat - min_lat)
    cell_max_lat = min_lat + ((lat_partition + 1) / 100) * (max_lat - min_lat)

    cell_min_time = min_time + (time_partition / 100) * (max_time - min_time)
    cell_max_time = min_time + ((time_partition + 1) / 100) * (max_time - min_time)

    # 计算经度、纬度和时间的重叠比例
    lon_overlap = max(0, min(cell_max_lon, up_x) - max(cell_min_lon, low_x)) / (cell_max_lon - cell_min_lon)
    lat_overlap = max(0, min(cell_max_lat, up_y) - max(cell_min_lat, low_y)) / (cell_max_lat - cell_min_lat)
    time_overlap = max(0, min(cell_max_time, up_time) - max(cell_min_time, low_time)) / (cell_max_time - cell_min_time)

    # 计算总的重叠比例 f
    f = lon_overlap * lat_overlap * time_overlap

    # 检查是否完全包含或部分包含
    if f == 1:
        return "fully_inside", f
    elif f > 0:
        return "partially_inside", f
    else:
        return "outside", 0


def write_results_to_file(results, output_file, total_runtime):
    with open(output_file, 'w') as f:
        for i, result in enumerate(results):
            f.write(f"Query {i + 1} Results:\n")
            f.write(f"Total Matching Records: {result['count']}\n")
            f.write("Matching Records (lon, lat, timestamp, amount):\n")
            for record in result['records']:
                if isinstance(record, str):  # 如果是字符串类型，直接写入字符串（用于approximate query部分包含的情况）
                    f.write(f"{record}\n")
                else:
                    lon, lat, timestamp, amount = record
                    f.write(f"{lon}, {lat}, {datetime.fromtimestamp(timestamp)}, {amount}\n")
            f.write("\n")
        f.write(f"Total runtime: {total_runtime:.2f} seconds\n")


def main():
    # 使用函数从文件中加载数据
    grid, (min_lon, max_lon, min_lat, max_lat, min_time, max_time) = load_grid_from_file('../Datasets/grid.txt')

    # 让用户输入选择：0表示exact query，1表示approximate query
    user_input = input("Enter 1 for exact query processing or 0 for approximate query processing: ")

    # 检查用户输入并调用相应的处理函数
    if user_input == "1":
        print("Running exact query processing...")
        start_time = time.time()  # 记录开始时间
        results = exact_query_processing(grid, '../Datasets/queries.txt', min_lon, max_lon, min_lat, max_lat, min_time, max_time)
        end_time = time.time()  # 记录结束时间
        total_runtime = end_time - start_time
        # save查询结果
        output_file = '../Datasets/exact_query_results_Adv.txt'
        write_results_to_file(results, output_file, total_runtime)
    elif user_input == "0":
        print("Running approximate query processing...")
        start_time = time.time()  # 记录开始时间
        results = approximate_query_processing(grid, '../Datasets/queries.txt', min_lon, max_lon, min_lat, max_lat, min_time, max_time)
        end_time = time.time()  # 记录结束时间
        total_runtime = end_time - start_time
        # save查询结果
        output_file = '../Datasets/approximate_query_results_Adv.txt'
        write_results_to_file(results, output_file, total_runtime)
    else:
        print("Invalid input. Please enter 0 or 1.")


# 调用主函数
main()