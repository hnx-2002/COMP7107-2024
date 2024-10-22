import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import pickle


class PivotSelector:
    def __init__(self, file_path):
        self.data = self.load_data(file_path)
        self.pivots = []
        self.distances = None

    def load_data(self, file_path):
        # save the 10d data to list, split using 'space'
        data = []
        with open(file_path, 'r') as file:
            for line in file:
                data.append(list(map(float, line.strip().split())))
        return np.array(data)

    def euclidean_distance(self, a, b):
        return np.sqrt(np.sum((a - b) ** 2))

    def compute_pivots(self, numpivots):
        n = len(self.data)
        self.pivots = []
        self.distances = np.zeros((n, numpivots))

        # seed as data[0]
        seed = self.data[0]
        max_dist = -1
        first_pivot = 0
        for i in range(n):
            dist = self.euclidean_distance(seed, self.data[i])
            if dist > max_dist:
                max_dist = dist
                first_pivot = i
        self.pivots.append(first_pivot)

        # next pivots
        for k in range(1, numpivots):
            max_sum_dist = -1
            next_pivot = 0
            for i in range(n):
                sum_dist = sum(self.euclidean_distance(self.data[i], self.data[p]) for p in self.pivots)
                if sum_dist > max_sum_dist:
                    max_sum_dist = sum_dist
                    next_pivot = i
            self.pivots.append(next_pivot)

        # filling distances list
        for i in range(n):
            for j, pivot in enumerate(self.pivots):
                self.distances[i][j] = self.euclidean_distance(self.data[i], self.data[pivot])

        self.save_pivot_info()

        return self.pivots, self.distances

    def save_pivot_info(self):
        with open("../data/pivots_info.pkl", "wb") as file:
            pickle.dump({
                "pivots": self.pivots,
                "distances": self.distances,
                "data": self.data
            }, file)
        print("Pivot information saved to 'pivots_info.pkl'")

'''
    def visualize_pivots(self, method='pca'):
        if method == 'pca':
            reducer = PCA(n_components=2)
        elif method == 'tsne':
            reducer = TSNE(n_components=2, random_state=42)
        else:
            raise ValueError("Unsupported method. Choose 'pca' or 'tsne'.")

        data_2d = reducer.fit_transform(self.data)
        pivots_2d = data_2d[self.pivots]

        plt.scatter(data_2d[:, 0], data_2d[:, 1], color='blue', label='Data Points', alpha=0.5)
        plt.scatter(pivots_2d[:, 0], pivots_2d[:, 1], color='red', label='Pivots', s=100)
        plt.xlabel(f'{method.upper()} Component 1')
        plt.ylabel(f'{method.upper()} Component 2')
        plt.legend()
        plt.title(f'{method.upper()} Visualization of 10-Dimensional Data')
        plt.show()
'''


# 主函数
if __name__ == "__main__":
    file_path = '../data/data10K10.txt'
    numpivots = int(input())

    selector = PivotSelector(file_path)
    pivots, distances = selector.compute_pivots(numpivots)
    print("Pivots:", pivots)
    print("Distances array:\n", distances)

    # selector.visualize_pivots(method='pca')
