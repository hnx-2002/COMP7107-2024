import pandas as pd
from datetime import datetime
from rtree import index
import time

# 设置 pandas 显示选项，确保显示所有列
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.expand_frame_repr', False)  # 防止换行显示
pd.set_option('display.max_rows', 50)  # 如果你想显示更多行，可以修改这里


def load_grid_from_file(filename):
    grid = {}  # dictionary
    min_lon, max_lon = None, None
    min_lat, max_lat = None, None
    min_time, max_time = None, None

    with open(filename, 'r') as f:
        lines = f.readlines()

        # get the global min and max
        min_lon, max_lon = map(float, lines[0].strip().split(','))
        min_lat, max_lat = map(float, lines[1].strip().split(','))
        min_time, max_time = map(float, lines[2].strip().split(','))

        # Parse the remaining grid data line by line
        i = 3
        while i < len(lines):
            # Read the coordinates (x, y, t) of the grid cells
            cell_coords = lines[i].strip()
            cell_x, cell_y, cell_t = map(int, cell_coords.strip('()').split(','))
            cell_key = (cell_x, cell_y, cell_t)

            # Read the total amount of the cell
            total_amt_in_cell = int(lines[i + 1].strip())

            # Initialize the record list for THIS grid cell
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

    # Read queries.txt
    with open(query_file, 'r') as f:
        queries = f.readlines()

    for query in queries:
        # Analyze query conditions: low_x, up_x, low_y, up_y, low_datetime, up_datetime
        query_parts = query.strip().split(',')
        low_x, up_x = float(query_parts[0]), float(query_parts[1])
        low_y, up_y = float(query_parts[2]), float(query_parts[3])
        low_time = datetime.strptime(query_parts[4], "%Y-%m-%d %H:%M:%S").timestamp()
        up_time = datetime.strptime(query_parts[5], "%Y-%m-%d %H:%M:%S").timestamp()

        # total amount = 0
        total_amount = 0

        # Traverse grid cells
        for cell_key, cell_data in grid.items():
            lon_partition, lat_partition, time_partition = cell_key

            # Check if the grid cells intersect with the geographic and temporal range of the query
            cell_status = get_cell_status(cell_key, low_x, up_x, low_y, up_y, low_time, up_time,
                                          min_lon, max_lon, min_lat, max_lat, min_time, max_time)

            if cell_status == "fully_inside":
                # If the grid cells are completely included in the query range, use Total_Smt_in_cell directly
                total_amount += cell_data['count']
            elif cell_status == "partially_inside":
                # If it is partially included, it is necessary to check the records item by item
                for record in cell_data['records']:
                    lon, lat, timestamp, amount = record
                    # Check if each record meets the query criteria
                    if low_x <= lon <= up_x and low_y <= lat <= up_y and low_time <= timestamp <= up_time:
                        total_amount += 1

        # Save the results of each query
        exact_results.append(total_amount)

    return exact_results


def get_cell_status(cell_key, low_x, up_x, low_y, up_y, low_time, up_time,
                    min_lon, max_lon, min_lat, max_lat, min_time, max_time):
    lon_partition, lat_partition, time_partition = cell_key

    # Calculate the longitude, latitude, and time range of the unit based on the number of partitions
    cell_min_lon = min_lon + (lon_partition / 100) * (max_lon - min_lon)
    cell_max_lon = min_lon + ((lon_partition + 1) / 100) * (max_lon - min_lon)

    cell_min_lat = min_lat + (lat_partition / 100) * (max_lat - min_lat)
    cell_max_lat = min_lat + ((lat_partition + 1) / 100) * (max_lat - min_lat)

    cell_min_time = min_time + (time_partition / 100) * (max_time - min_time)
    cell_max_time = min_time + ((time_partition + 1) / 100) * (max_time - min_time)

    # fully included in the query scope
    if (low_x <= cell_min_lon and cell_max_lon <= up_x and
            low_y <= cell_min_lat and cell_max_lat <= up_y and
            low_time <= cell_min_time and cell_max_time <= up_time):
        return "fully_inside"

    # partially included in the query scope
    if (cell_max_lon >= low_x and cell_min_lon <= up_x and
            cell_max_lat >= low_y and cell_min_lat <= up_y and
            cell_max_time >= low_time and cell_min_time <= up_time):
        return "partially_inside"

    # not within the query range
    return "outside"


# approximate query
def approximate_query_processing(grid, query_file, min_lon, max_lon, min_lat, max_lat, min_time, max_time):
    approximate_results = []  # Used to store the results of each query

    # read
    with open(query_file, 'r') as f:
        queries = f.readlines()

    for query in queries:
        # Analyze query conditions: low_x, up_x, low_y, up_y, low_datetime, up_datetime
        query_parts = query.strip().split(',')
        low_x, up_x = float(query_parts[0]), float(query_parts[1])
        low_y, up_y = float(query_parts[2]), float(query_parts[3])
        low_time = datetime.strptime(query_parts[4], "%Y-%m-%d %H:%M:%S").timestamp()
        up_time = datetime.strptime(query_parts[5], "%Y-%m-%d %H:%M:%S").timestamp()

        # total amount = 0
        total_amount = 0

        # traverse
        for cell_key, cell_data in grid.items():
            lon_partition, lat_partition, time_partition = cell_key

            # check if the grid cells intersect with the geographic and temporal range of the query
            cell_status, f = get_cell_status_and_fraction(cell_key, low_x, up_x, low_y, up_y, low_time, up_time,
                                                          min_lon, max_lon, min_lat, max_lat, min_time, max_time)

            if cell_status == "fully_inside":
                # completely included in the query range add Total_Smt_in_cell directly
                total_amount += cell_data['count']
            elif cell_status == "partially_inside":
                # partially included, add f * Total_Amt_in_cell
                total_amount += f * cell_data['count']
        total_amount = round(total_amount)
        # save
        approximate_results.append(total_amount)

    return approximate_results


def get_cell_status_and_fraction(cell_key, low_x, up_x, low_y, up_y, low_time, up_time,
                                 min_lon, max_lon, min_lat, max_lat, min_time, max_time):
    lon_partition, lat_partition, time_partition = cell_key

    # Calculate the longitude, latitude, and time range of the unit based on the number of partitions
    cell_min_lon = min_lon + (lon_partition / 100) * (max_lon - min_lon)
    cell_max_lon = min_lon + ((lon_partition + 1) / 100) * (max_lon - min_lon)

    cell_min_lat = min_lat + (lat_partition / 100) * (max_lat - min_lat)
    cell_max_lat = min_lat + ((lat_partition + 1) / 100) * (max_lat - min_lat)

    cell_min_time = min_time + (time_partition / 100) * (max_time - min_time)
    cell_max_time = min_time + ((time_partition + 1) / 100) * (max_time - min_time)

    # Calculate the overlap ratio of longitude, latitude, and time
    lon_overlap = max(0, min(cell_max_lon, up_x) - max(cell_min_lon, low_x)) / (cell_max_lon - cell_min_lon)
    lat_overlap = max(0, min(cell_max_lat, up_y) - max(cell_min_lat, low_y)) / (cell_max_lat - cell_min_lat)
    time_overlap = max(0, min(cell_max_time, up_time) - max(cell_min_time, low_time)) / (cell_max_time - cell_min_time)

    # Calculate the total overlap ratio f
    f = lon_overlap * lat_overlap * time_overlap

    # Check if it fully or partially includes
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
            f.write(f"Total Matching Records: {result}\n")
            f.write("\n\n")
        f.write(f"Total runtime: {total_runtime:.2f} seconds\n")


def main():
    # load grid cells
    grid, (min_lon, max_lon, min_lat, max_lat, min_time, max_time) = load_grid_from_file('../Datasets/grid.txt')

    # 0 -> exact query，1 -> approximate query
    user_input = input("Enter 1 for exact query processing or 0 for approximate query processing: ")

    # check the input
    if user_input == "1":
        print("Running exact query processing...")
        start_time = time.time()  # start time
        results = exact_query_processing(grid, '../Datasets/queries.txt', min_lon, max_lon, min_lat, max_lat, min_time,
                                         max_time)
        end_time = time.time()  # end time
        total_runtime = end_time - start_time
        # save the results
        output_file = '../Datasets/exact_query_results.txt'
        write_results_to_file(results, output_file, total_runtime)
    elif user_input == "0":
        print("Running approximate query processing...")
        start_time = time.time()  # start time
        results = approximate_query_processing(grid, '../Datasets/queries.txt', min_lon, max_lon, min_lat, max_lat,
                                               min_time, max_time)
        end_time = time.time()  # end time
        total_runtime = end_time - start_time
        # save the results
        output_file = '../Datasets/approximate_query_results.txt'
        write_results_to_file(results, output_file, total_runtime)
    else:
        print("Invalid input. Please enter 0 or 1.")


# main function
main()
