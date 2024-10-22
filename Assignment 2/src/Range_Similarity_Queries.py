import numpy as np
import time
import pickle
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

def euclidean_distance(a, b):

    return np.sqrt(np.sum((a - b) ** 2))


def naive_range_query(data, queries, epsilon):
    totalcount = 0
    results = []

    for query in queries:
        result = []
        for oid, obj in enumerate(data):
            dist = euclidean_distance(query, obj)
            if dist <= epsilon:
                result.append(oid)
        result.sort()
        results.append(result)
        totalcount += len(data)

    avg_count = totalcount / len(queries)
    return results, avg_count


def pivot_range_query(data, queries, pivots, distances, epsilon):
    totalcount = 0
    results = []

    for query in queries:
        result = []

        # calculate the distance between pivots and query
        query_to_pivot_distances = [euclidean_distance(query, data[p]) for p in pivots]
        totalcount += len(pivots)

        for oid, obj in enumerate(data):
            # prune criteria
            skip = False
            for p_idx, pivot_dist in enumerate(query_to_pivot_distances):
                if abs(distances[oid][p_idx] - pivot_dist) > epsilon:
                    skip = True
                    break

            # calculate real distance
            if not skip:
                dist = euclidean_distance(query, obj)
                totalcount += 1
                if dist <= epsilon:
                    result.append(oid)

        result.sort()
        results.append(result)
    avg_count = totalcount / len(queries)
    return results, avg_count


def iDistance_range_query(data, queries, pivots, iDistance_array, epsilon, global_maxd, maxd_per_pivot):
    results = []
    totalcount = 0

    for query in queries:
        result = []
        # traverse pivots
        for pivot_idx, pivot in enumerate(pivots):
            # query to pivot
            dist_to_pivot = euclidean_distance(query, data[pivot])
            totalcount += 1

            # prune
            if dist_to_pivot - maxd_per_pivot[pivot_idx] > epsilon:
                continue

            # not pruned
            lower_bound = pivot_idx * global_maxd + max(0, dist_to_pivot - epsilon)
            upper_bound = pivot_idx * global_maxd + min(maxd_per_pivot[pivot_idx], dist_to_pivot + epsilon)

            # binary search
            iDist_values = [item[0] for item in iDistance_array]
            start_idx = bisect.bisect_left(iDist_values, lower_bound)
            end_idx = bisect.bisect_right(iDist_values, upper_bound)

            # scan from lower to upper
            for i in range(start_idx, end_idx):
                iDist, oid, pivot_idx_in_array, pivot_id = iDistance_array[i]

                # avoid distances mistakes
                if pivot_idx_in_array == pivot_idx:
                    dist = euclidean_distance(query, data[oid])
                    totalcount += 1
                    if dist <= epsilon:
                        result.append(oid)
        result.sort()
        results.append(result)

    avg_count = totalcount / len(queries)
    return results, avg_count



def savetxt(method, results, time, avg_count, param_name=None, param_value=None):

    method_dict = {1: 'Naive', 2: 'Pivots', 3: 'iDistance'}
    Method = method_dict.get(method, 'Unknown')


    file_name = f"../data/{Method}_query"
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


    file_name = f"../data/{Method}_query"
    if param_name and param_value is not None:
        file_name += f"_{param_name}_{param_value}"
    file_name += ".html"


    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write("<html><body>\n")
            file.write(f"<h2>Method: {Method}, ɛ: {param_value}</h2>\n")
            file.write(f"<p><b>Using time:</b> {time:.6f} seconds</p>\n")
            file.write(f"<p><b>Average number of calculations:</b> {avg_count}</p>\n")
            file.write("<hr>\n")
            for idx, result in enumerate(results):
                file.write(f"<p>Query {idx + 1} Result: {result}</p>\n")
            file.write("</body></html>")
    except Exception as e:
        print(f"An error occurred while saving results: {e}")

def save_time(timing_data, file_name='time_info.txt'):
    try:
        with open(file_name, 'w') as file:
            for entry in timing_data:
                method_name = entry['method_name']
                epsilon = entry['epsilon']
                total_time = entry['total_time']
                avg_counts = entry['avg_counts']
                file.write(f"{method_name},{epsilon},{total_time:.6f},{avg_counts}\n")
    except Exception as e:
        print(f"Error saving timing info: {e}")


def run_query(method, data, queries, pivots, distances, iDistance_array, global_maxd, maxd_per_pivot, epsilon, time_info):

    if method == 1:
        start_time = time.time()
        results, avg_counts = naive_range_query(data, queries, epsilon)
        total_time = time.time() - start_time
        method_name = "Naive"

    elif method == 2:
        start_time = time.time()
        results, avg_counts = pivot_range_query(data, queries, pivots, distances, epsilon)
        total_time = time.time() - start_time
        method_name = "Pivots"

    elif method == 3:
        start_time = time.time()
        results, avg_counts = iDistance_range_query(data, queries, pivots, iDistance_array, epsilon, global_maxd, maxd_per_pivot)
        total_time = time.time() - start_time
        method_name = "iDistance"

    else:
        raise ValueError("Invalid method")

    # save file
    savehtml(method, results, total_time, avg_counts, param_name='ɛ', param_value=epsilon)

    # print info
    print(f"Average distance computations per query ({method_name}) (ɛ = {epsilon})= {avg_counts}")
    print(f"Total time for {method_name} method (ɛ = {epsilon}) = {total_time:.6f} seconds")

    time_info.append({
        'method_name': method_name,
        'epsilon': epsilon,
        'total_time': total_time,
        'avg_counts': avg_counts
    })


if __name__ == "__main__":

    data_file_path = '../data/iDistance.pkl'
    query_file_path = '../data/queries10.txt'

    # load data
    pivots, distances, data, global_maxd, maxd_per_pivot, iDistance_array, queries = load_iDistance_info(data_file_path)

    # capture input
    method = int(input("enter method (0 for all methods): "))

    time_info = []

    if method == 0:

        # do all
        for epsilon in [0.1, 0.2, 0.4, 0.8]:
            for m in range(1, 4):
                run_query(m, data, queries, pivots, distances, iDistance_array, global_maxd, maxd_per_pivot, epsilon, time_info)

        save_time(time_info, file_name='../data/Range_Query_Timeinfo.txt')

    elif method in [1, 2, 3]:

        epsilon = float(input("enter ɛ: "))
        # do certain
        run_query(method, data, queries, pivots, distances, iDistance_array, global_maxd, maxd_per_pivot, epsilon, time_info)

    else:
        print("Invalid method")





