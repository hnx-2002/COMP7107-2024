import pickle
import numpy as np

# 本来这里还想继续搞得像模像样的像个正经工程一样的，但是奈何文件要求一步一步来的，那还是直接面向过程写吧.....

def load_pivot_info(file_path):

    with open(file_path, "rb") as file:
        details = pickle.load(file)

    pivots = details["pivots"]
    distances = details["distances"]
    data = details["data"]
    return pivots, distances, data

def load_queries(file_path):

    queries = []
    with open(file_path, 'r') as file:
        for line in file:
            queries.append(list(map(float, line.strip().split())))
    return np.array(queries)

def compute_max_distances(data, pivots, distances):
    n = len(data)
    numpivots = len(pivots)
    maxd = np.zeros(numpivots)  # maxd_per_pivot

    # assign objects, calculate distances, and find global_maxd
    for oid in range(n):
        # nearest pivot
        nearest_pivot_idx = np.argmin(distances[oid])
        nearest_pivot_dist = distances[oid][nearest_pivot_idx]

        # refresh maxd_per_pivot
        if nearest_pivot_dist > maxd[nearest_pivot_idx]:
            maxd[nearest_pivot_idx] = nearest_pivot_dist

    # max(maxd) -> global_maxd
    return max(maxd), maxd

# 示例调用
def compute_iDistance(data, pivots, distances):
    n = len(data)
    iDist_array = []  # save (iDist, oid)

    global_maxd, maxd_per_pivot = compute_max_distances(data, pivots, distances)

    # traverse, calculate iDist and sort
    for oid in range(n):
        # nearest pivot
        nearest_pivot_idx = np.argmin(distances[oid])
        nearest_pivot_dist = distances[oid][nearest_pivot_idx]

        iDist = nearest_pivot_idx * global_maxd + nearest_pivot_dist

        pivot_id = pivots[nearest_pivot_idx]
        iDist_array.append((iDist, oid, nearest_pivot_idx, pivot_id))
        # iDist_array.append((iDist, oid))

    # sort
    iDist_array.sort()

    return iDist_array, global_maxd, maxd_per_pivot


file_path = "../data/pivots_info.pkl"
query_path = '../data/queries10.txt'
pivots, distances, data = load_pivot_info(file_path)
queries = load_queries(query_path)

print("Loaded Pivots:", pivots)
print("Loaded Distances Array:\n", distances)

iDist_array, global_maxd, maxd_per_pivot = compute_iDistance(data, pivots, distances)

with open("../data/iDistance.pkl", "wb") as file:
    pickle.dump({
        "pivots": pivots,
        "distance": distances,
        "global_maxd": global_maxd,
        "maxd_per_pivot": maxd_per_pivot,
        "iDistance": iDist_array,
        "data": data,
        "queries": queries
    }, file)
print("Pivot information saved to 'pivots_info.pkl'")

print("iDistance array:", iDist_array)
print("Global maxd:", global_maxd)
print("Maxd per pivot:", maxd_per_pivot)
