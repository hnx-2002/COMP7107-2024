import pickle

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



def find_oid_pivot(oid, iDist_array):
    for iDist, object_id, nearest_pivot_idx, pivot_id in iDist_array:
        if object_id == oid:
            return pivot_id, nearest_pivot_idx
    return None


def find_oid_index_in_iDistance_array(oid, iDist_array):
    for index, (iDist, object_id, nearest_pivot_idx, pivot_id) in enumerate(iDist_array):
        if object_id == oid:
            return index
    return None


def check_duplicate_oid(iDist_array):
    oid_set = set()
    duplicates = []

    for iDist, oid, nearest_pivot_idx, pivot_id in iDist_array:
        if oid in oid_set:
            duplicates.append(oid)
        else:
            oid_set.add(oid)

    return duplicates


def get_pivot_ranges_naive(iDistance_array, pivots):
    pivot_ranges = {}

    for pivot_id in pivots:
        min_iDist = float('inf')
        max_iDist = float('-inf')
        start_idx = None
        end_idx = None


        for idx, (iDist, oid, nearest_pivot_idx, current_pivot_id) in enumerate(iDistance_array):
            if current_pivot_id == pivot_id:

                if iDist < min_iDist:
                    min_iDist = iDist
                if iDist > max_iDist:
                    max_iDist = iDist


                if start_idx is None:
                    start_idx = idx


                end_idx = idx


        if start_idx is not None and end_idx is not None:
            pivot_ranges[pivot_id] = {
                'distance_range': (min_iDist, max_iDist),
                'index_range': (start_idx, end_idx)
            }

    return pivot_ranges




data_file_path = '../data/iDistance.pkl'
pivots, distances, data, global_maxd, maxd_per_pivot, iDistance_array, queries = load_iDistance_info(data_file_path)





oid = 5610
pivot_id, nearest_id = find_oid_pivot(oid, iDistance_array)
oid_index = find_oid_index_in_iDistance_array(oid, iDistance_array)

duplicates = check_duplicate_oid(iDistance_array)

pivot_ranges = get_pivot_ranges_naive(iDistance_array, pivots)


for pivot_id, info in pivot_ranges.items():
    distance_range = info['distance_range']
    index_range = info['index_range']
    print(f"Pivot {pivot_id}: 距离范围 {distance_range}, 索引范围 {index_range}")


if duplicates:
    print(f"重复的 oid: {duplicates}")
else:
    print("没有重复的")

if pivot_id is not None:
    print(f"{oid} 属于 pivot {pivot_id}, 索引: {nearest_id}")
else:
    print(f"没有找到对象 {oid} 对应的 pivot")

if oid_index is not None:
    print(f"{oid} iDistance_array 的索引为: {oid_index}")
    print(iDistance_array[oid_index])
else:
    print(f"在iDistance_array没有找到对象{oid}")
