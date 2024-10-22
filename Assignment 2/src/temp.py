import numpy as np
import time
import pickle
import heapq
import bisect

def load_iDistance_info(file_path):

    with open(file_path, "rb") as file:
        details = pickle.load(file)

    pivots = details["pivots"]
    distances = details["distance"]
    data = details["data"]
    global_maxd = details["global_maxd"]
    maxd_per_pivot = details["maxd_per_pivot"]
    iDistance_array = details["iDistance"]
    queries = details["queries"]
    return pivots, distances, data, global_maxd, maxd_per_pivot, iDistance_array, queries

def savetxt(method, results, time, avg_count):
    # 根据方法选择合适的文件名
    if method == 1:
        Method = 'Naive'
        file_path = '../data/naive_KNN.txt'
    elif method == 2:
        Method = 'Pivots'
        file_path = '../data/pivots_KNN.txt'
    elif method == 3:
        Method = 'iDistance'
        file_path = '../data/iDistance_KNN.txt'
    else:
        print("Invalid method for saving results.")
        return

    # 保存结果到对应的文件
    try:
        with open(file_path, 'w') as file:  # 使用写入模式（'w'）打开文件，这样每次都会覆盖旧内容
            file.write(f"Method: {Method}, Using time: {time: .6f}s, Average number of calculations: {avg_count}\n")
            for idx, result in enumerate(results):
                file.write(f"Query {idx + 1} Result: {result}\n")
    except Exception as e:
        print(f"An error occurred while saving results: {e}")


def savehtml(method, results, time, avg_count):
    # 根据方法选择合适的文件名
    if method == 1:
        Method = 'Naive'
        file_path = '../data/naive_KNN.html'
    elif method == 2:
        Method = 'Pivots'
        file_path = '../data/pivots_KNN.html'
    elif method == 3:
        Method = 'iDistance'
        file_path = '../data/iDistance_KNN.html'
    else:
        print("Invalid method for saving results.")
        return

    # 保存结果到对应的文件 (HTML 格式)
    try:
        with open(file_path, 'w') as file:  # 使用写入模式（'w'）打开文件，这样每次都会覆盖旧内容
            file.write("<html><body>\n")
            file.write(f"<h2>Method: {Method}</h2>\n")
            file.write(f"<p><b>Using time:</b> {time:.6f} seconds</p>\n")
            file.write(f"<p><b>Average number of calculations:</b> {avg_count}</p>\n")
            file.write("<hr>\n")
            for idx, result in enumerate(results):
                file.write(f"<p>Query {idx + 1} Result: {result}</p>\n")
            file.write("</body></html>")
    except Exception as e:
        print(f"An error occurred while saving results: {e}")

def euclidean_distance(a, b):
    return np.sqrt(np.sum((a - b) ** 2))

def naive_kNN(data, queries, k):
    totalcount = 0
    results = []

    for query_idx, query in enumerate(queries):
        # 使用堆来维护距离最小的 k 个对象，(-distance, oid) 用于最大堆模拟最小 k 个元素
        max_heap = []

        for oid, obj in enumerate(data):
            dist = euclidean_distance(query, obj)
            totalcount += 1

            if len(max_heap) < k:
                # 如果堆中元素少于 k 个，直接将当前元素加入堆中
                heapq.heappush(max_heap, (-dist, oid))
            else:
                # 如果堆中元素等于 k 个，并且当前距离小于堆顶元素的距离，则替换堆顶元素
                if dist < -max_heap[0][0]:
                    heapq.heapreplace(max_heap, (-dist, oid))

        # 获取最终 k 个最近邻对象
        knn_result = sorted([(-dist, oid) for dist, oid in max_heap])
        results.append(knn_result)

    avg_count = totalcount / len(queries)
    return results, avg_count

def pivot_kNN(data, queries, pivots, distances, k):
    totalcount = 0
    results = []
    # 对每个查询点进行 kNN 查询
    for query_idx, query in enumerate(queries):
        max_heap = []

        # 计算查询点到每个枢轴的距离
        query_to_pivot_distances = [euclidean_distance(query, data[p]) for p in pivots]

        for oid, obj in enumerate(data):
            # 剪枝操作
            skip = False
            for pivot_idx, pivot_dist in enumerate(query_to_pivot_distances):
                # 如果当前对象与查询点的某个枢轴距离之差大于当前的最大阈值，则剪枝
                if len(max_heap) == k:
                    epsilon = -max_heap[0][0]  # 当前堆顶的距离作为阈值
                    if abs(distances[oid][pivot_idx] - pivot_dist) > epsilon:
                        skip = True
                        break

            # 如果没有被剪枝，计算距离并维护堆
            if not skip:
                dist = euclidean_distance(query, obj)
                totalcount += 1

                if len(max_heap) < k:
                    heapq.heappush(max_heap, (-dist, oid))
                elif dist < -max_heap[0][0]:
                    heapq.heapreplace(max_heap, (-dist, oid))

        # 获取最终 k 个最近邻对象
        knn_result = sorted([(-dist, oid) for dist, oid in max_heap])
        results.append(knn_result)

    avg_count = totalcount / len(queries)
    return results, avg_count

def iDistance_kNN(data, queries, pivots, iDistance_array, k, global_maxd, maxd_per_pivot):
    totalcount = 0
    results = []

    # 对每个查询点进行 kNN 查询
    for query_idx, query in enumerate(queries):
        max_heap = []

        # 计算查询点到每个枢轴的距离
        query_to_pivot_distances = [euclidean_distance(query, data[p]) for p in pivots]

        # 找到与查询点最近的枢轴
        nearest_pivot_idx = np.argmin(query_to_pivot_distances)
        nearest_pivot_dist = query_to_pivot_distances[nearest_pivot_idx]

        # 初步扫描属于最近枢轴的对象，增加剪枝条件
        lower_bound = nearest_pivot_idx * global_maxd
        upper_bound = (nearest_pivot_idx + 1) * global_maxd

        # 使用二分查找找到下界的起始位置
        iDist_values = [item[0] for item in iDistance_array]
        start_idx = bisect.bisect_left(iDist_values, lower_bound)
        end_idx = bisect.bisect_right(iDist_values, upper_bound)

        # 定义初始的 epsilon 为无穷大，表示一开始没有任何约束
        epsilon = float('inf')

        # 从 start_idx 到 end_idx 范围内查找初步的 k 个最近邻
        visited_oids = set()  # 记录已经访问过的对象，避免重复
        for i in range(start_idx, end_idx):
            iDist, oid, pivot_idx, pivot_id = iDistance_array[i]

            if oid in visited_oids:
                continue  # 如果对象已经访问过，则跳过
            visited_oids.add(oid)

            dist = euclidean_distance(query, data[oid])
            totalcount += 1

            if len(max_heap) < k:
                heapq.heappush(max_heap, (-dist, oid))
                # 更新距离阈值
                epsilon = -max_heap[0][0] if len(max_heap) == k else float('inf')
            elif dist < -max_heap[0][0]:
                heapq.heapreplace(max_heap, (-dist, oid))
                # 更新距离阈值
                epsilon = -max_heap[0][0]
            elif dist == -max_heap[0][0]:
                # 如果距离相等，也将其加入堆中，但需要去重
                heapq.heappush(max_heap, (-dist, oid))
                if len(max_heap) > k:
                    heapq.heappop(max_heap)
                epsilon = -max_heap[0][0]

        # 当前的距离阈值为堆顶元素的距离
        epsilon = -max_heap[0][0] if len(max_heap) == k else float('inf')

        # 对于其余枢轴，检查是否可以剪枝
        for pivot_idx, pivot_dist in enumerate(query_to_pivot_distances):
            if pivot_idx == nearest_pivot_idx:
                continue  # 跳过最近的枢轴

            # 使用距离阈值进行剪枝
            if abs(pivot_dist - nearest_pivot_dist) <= epsilon:
                # 如果未被剪枝，则扫描属于该枢轴的对象
                lower_bound = pivot_idx * global_maxd
                upper_bound = (pivot_idx + 1) * global_maxd

                start_idx = bisect.bisect_left(iDist_values, lower_bound)
                end_idx = bisect.bisect_right(iDist_values, upper_bound)

                for i in range(start_idx, end_idx):
                    iDist, oid, current_pivot_idx, pivot_id = iDistance_array[i]

                    if oid in visited_oids:
                        continue  # 如果对象已经访问过，则跳过
                    visited_oids.add(oid)

                    dist = euclidean_distance(query, data[oid])
                    totalcount += 1

                    if len(max_heap) < k:
                        heapq.heappush(max_heap, (-dist, oid))
                        # 更新距离阈值
                        epsilon = -max_heap[0][0] if len(max_heap) == k else float('inf')
                    elif dist < -max_heap[0][0]:
                        heapq.heapreplace(max_heap, (-dist, oid))
                        # 更新距离阈值
                        epsilon = -max_heap[0][0]
                    elif dist == -max_heap[0][0]:
                        # 如果距离相等，也将其加入堆中，但需要去重
                        heapq.heappush(max_heap, (-dist, oid))
                        if len(max_heap) > k:
                            heapq.heappop(max_heap)
                        epsilon = -max_heap[0][0]

        # 获取最终 k 个最近邻对象
        knn_result = sorted([(-dist, oid) for dist, oid in max_heap])
        results.append(knn_result)

    avg_count = totalcount / len(queries)
    return results, avg_count


def run_KNN(method, data, queries, pivots, distances, iDistance_array, global_maxd, maxd_per_pivot, k):
    if method == 1:
        start_time = time.time()
        results, avg_counts = naive_kNN(data, queries, k)
        total_time = time.time() - start_time
        method_name = "Naive"

    elif method == 2:
        start_time = time.time()
        results, avg_counts = pivot_kNN(data, queries, pivots, distances, k)
        total_time = time.time() - start_time
        method_name = "Pivots"

    elif method == 3:
        start_time = time.time()
        results, avg_counts = iDistance_kNN(data, queries, pivots, iDistance_array, k, global_maxd, maxd_per_pivot)
        total_time = time.time() - start_time
        method_name = "iDistance"

    else:
        raise ValueError("Invalid method")

    # 保存结果到文件
    savehtml(method, results, total_time, avg_counts)

    for idx, result in enumerate(results):
        print(f"Query {idx + 1} kNN Result:")
        for dist, oid in result:
            print(f"  Distance: {dist:.6f}, Object ID: {oid}")

    print(f"Average distance computations per KNN_query ({method_name}) = {avg_counts}")
    print(f"Total time for {method_name} method = {total_time:.6f} seconds")


if __name__ == "__main__":
    # 假设数据已经从文件中加载
    data_file_path = '../data/iDistance.pkl'

    # 加载数据
    pivots, distances, data, global_maxd, maxd_per_pivot, iDistance_array, queries = load_iDistance_info(data_file_path)

    method = int(input("enter method (0 for all methods): "))
    k = int(input("Enter number of nearest neighbors (k): "))

    if method == 0:

        # 执行所有方法
        for m in range(1, 4):
            run_KNN(m, data, queries, pivots, distances, iDistance_array, global_maxd, maxd_per_pivot, k)

    elif method in [1, 2, 3]:

        # 执行指定的方法
        run_KNN(method, data, queries, pivots, distances, iDistance_array, global_maxd, maxd_per_pivot, k)

    else:
        print("Invalid method")
