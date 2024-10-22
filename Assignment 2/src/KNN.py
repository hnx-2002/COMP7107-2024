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

def savetxt(method, results, time, avg_count, param_name=None, param_value=None):

    method_dict = {1: 'Naive', 2: 'Pivots', 3: 'iDistance'}
    Method = method_dict.get(method, 'Unknown')


    file_name = f"../data/{Method}_KNN"
    if param_name and param_value is not None:
        file_name += f"_{param_name}_{param_value}"
    file_name += ".txt"


    try:
        with open(file_name, 'w') as file:
            file.write(f"Method: {Method}, Using time: {time: .6f}s, Average number of calculations: {avg_count}\n")
            for idx, result in enumerate(results):
                file.write(f"Query {idx + 1} Result: {result}\n")
    except Exception as e:
        print(f"An error occurred while saving results: {e}")


def savehtml(method, results, time, avg_count, param_name=None, param_value=None):

    method_dict = {1: 'Naive', 2: 'Pivots', 3: 'iDistance'}
    Method = method_dict.get(method, 'Unknown')


    file_name = f"../data/{Method}_KNN"
    if param_name and param_value is not None:
        file_name += f"_{param_name}_{param_value}"
    file_name += ".html"


    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write("<html><body>\n")
            file.write(f"<h2>Method: {Method}, K: {param_value}</h2>\n")
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
        # Actually minheap
        max_heap = []

        for oid, obj in enumerate(data):
            dist = euclidean_distance(query, obj)
            totalcount += 1

            if len(max_heap) < k:
                # heap push
                heapq.heappush(max_heap, (-dist, oid))
            else:
                # replace heap top element
                if dist < -max_heap[0][0]:
                    heapq.heapreplace(max_heap, (-dist, oid))

        # sort so that knn
        knn_result = sorted([(-dist, oid) for dist, oid in max_heap])
        results.append(knn_result)

    avg_count = totalcount / len(queries)
    return results, avg_count

def pivot_kNN(data, queries, pivots, distances, k):
    totalcount = 0
    results = []
    # traverse query
    for query_idx, query in enumerate(queries):
        max_heap = []

        # query to pivot distance
        query_to_pivot_distances = [euclidean_distance(query, data[p]) for p in pivots]
        totalcount += len(pivots)

        for oid, obj in enumerate(data):
            # prune
            skip = False
            for pivot_idx, pivot_dist in enumerate(query_to_pivot_distances):
                # dynamic epsilon
                if len(max_heap) == k:
                    epsilon = -max_heap[0][0]  # search epsilon
                    if abs(distances[oid][pivot_idx] - pivot_dist) > epsilon:
                        skip = True
                        break

            # not pruned
            if not skip:
                dist = euclidean_distance(query, obj)
                totalcount += 1

                if len(max_heap) < k:
                    heapq.heappush(max_heap, (-dist, oid))
                elif dist < -max_heap[0][0]:
                    heapq.heapreplace(max_heap, (-dist, oid))

        # sort KNN
        knn_result = sorted([(-dist, oid) for dist, oid in max_heap])
        results.append(knn_result)

    avg_count = totalcount / len(queries)
    return results, avg_count

def iDistance_kNN(data, queries, pivots, iDistance_array, k, global_maxd, maxd_per_pivot, distances):
    totalcount = 0
    results = []

    # traverse query
    for query_idx, query in enumerate(queries):
        max_heap = []

        # query to pivot distance
        query_to_pivot_distances = [euclidean_distance(query, data[p]) for p in pivots]
        totalcount += len(pivots)

        # nearest pivot
        nearest_pivot_idx = np.argmin(query_to_pivot_distances)
        nearest_pivot_dist = query_to_pivot_distances[nearest_pivot_idx]

        # dynamic scan for the nearest pivot
        lower_bound = nearest_pivot_idx * global_maxd
        upper_bound = nearest_pivot_idx * global_maxd + maxd_per_pivot[nearest_pivot_idx]

        # binary search
        iDist_values = [item[0] for item in iDistance_array]
        start_idx = bisect.bisect_left(iDist_values, lower_bound)
        end_idx = bisect.bisect_right(iDist_values, upper_bound)

        # initial epsilon and dynamic update
        epsilon = float('inf')

        # scan from lower to upper
        for i in range(start_idx, end_idx):
            iDist, oid, pivot_idx_in_array, pivot_id = iDistance_array[i]

            # prune obj
            if abs(distances[oid][nearest_pivot_idx] - nearest_pivot_dist) > epsilon:
                continue

            # secondary validate
            if pivot_idx_in_array == nearest_pivot_idx:
                dist = euclidean_distance(query, data[oid])
                totalcount += 1

                if len(max_heap) < k:
                    heapq.heappush(max_heap, (-dist, oid))
                    epsilon = -max_heap[0][0] if len(max_heap) == k else float('inf')
                elif dist < -max_heap[0][0]:
                    heapq.heapreplace(max_heap, (-dist, oid))
                    epsilon = -max_heap[0][0]

        # update epsilon
        epsilon = -max_heap[0][0] if len(max_heap) == k else float('inf')

        # scan and prune pivot
        for pivot_idx, pivot_dist in enumerate(query_to_pivot_distances):

            if pivot_idx == nearest_pivot_idx:
                continue  # already scaned the nearest

            # prune pivots
            if pivot_dist - maxd_per_pivot[pivot_idx] <= epsilon:
                # not pruned
                lower_bound = pivot_idx * global_maxd + max(0, pivot_dist - epsilon)
                upper_bound = pivot_idx * global_maxd + min(maxd_per_pivot[pivot_idx], pivot_dist + epsilon)

                start_idx = bisect.bisect_left(iDist_values, lower_bound)
                end_idx = bisect.bisect_right(iDist_values, upper_bound)

                for i in range(start_idx, end_idx):
                    iDist, oid, pivot_idx_in_array, pivot_id = iDistance_array[i]
                    # prune obj
                    if abs(distances[oid][pivot_idx] - pivot_dist) > epsilon:
                        continue

                    if pivot_idx_in_array == pivot_idx:

                        dist = euclidean_distance(query, data[oid])
                        totalcount += 1

                        if len(max_heap) < k:
                            heapq.heappush(max_heap, (-dist, oid))
                            epsilon = -max_heap[0][0] if len(max_heap) == k else float('inf')
                        elif dist < -max_heap[0][0]:
                            heapq.heapreplace(max_heap, (-dist, oid))
                            epsilon = -max_heap[0][0]


        # sort to KNN
        knn_result = sorted([(-dist, oid) for dist, oid in max_heap])
        results.append(knn_result)

    avg_count = totalcount / len(queries)
    return results, avg_count


def save_time(timing_data, file_name=None):
    try:
        with open(file_name, 'w') as file:
            for entry in timing_data:
                method_name = entry['method_name']
                K = entry['K']
                total_time = entry['total_time']
                avg_counts = entry['avg_counts']
                file.write(f"{method_name},{K},{total_time:.6f},{avg_counts}\n")
    except Exception as e:
        print(f"Error saving timing info: {e}")


def run_KNN(method, data, queries, pivots, distances, iDistance_array, global_maxd, maxd_per_pivot, k, time_info):
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
        results, avg_counts = iDistance_kNN(data, queries, pivots, iDistance_array, k, global_maxd, maxd_per_pivot, distances)
        total_time = time.time() - start_time
        method_name = "iDistance"

    else:
        raise ValueError("Invalid method")


    savehtml(method, results, total_time, avg_counts, param_name='K', param_value=k)

    time_info.append({
        'method_name': method_name,
        'K': k,
        'total_time': total_time,
        'avg_counts': avg_counts
    })

    # for idx, result in enumerate(results):
    #     print(f"Query {idx + 1} kNN Result:")
    #     for dist, oid in result:
    #         print(f"  Distance: {dist:.6f}, Object ID: {oid}")
    #
    print(f"Average distance computations per KNN_query ({method_name}) when K = {k} = {avg_counts}")
    print(f"Total time for {method_name} method when K = {k} = {total_time:.6f} seconds")


if __name__ == "__main__":

    data_file_path = '../data/iDistance.pkl'

    # 加载数据
    pivots, distances, data, global_maxd, maxd_per_pivot, iDistance_array, queries = load_iDistance_info(data_file_path)

    method = int(input("enter method (0 for all methods): "))


    time_info = []

    if method == 0:


        for k in [1, 5, 10, 50, 100]:
            for m in range(1, 4):
                run_KNN(m, data, queries, pivots, distances, iDistance_array, global_maxd, maxd_per_pivot, k, time_info)

        save_time(time_info, file_name='../data/KNN_Timeinfo.txt')

    elif method in [1, 2, 3]:

        k = int(input("Enter number of nearest neighbors (k): "))

        run_KNN(method, data, queries, pivots, distances, iDistance_array, global_maxd, maxd_per_pivot, k, time_info)

    else:
        print("Invalid method")
