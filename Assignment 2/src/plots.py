import matplotlib.pyplot as plt
import numpy as np



def load_timeinfo(file_path):
    timing_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:

                method_name, param_value, total_time, avg_counts = line.strip().split(',')
                timing_data.append({
                    'method_name': method_name,
                    'param_value': float(param_value),
                    'total_time': float(total_time),
                    'avg_counts': float(avg_counts)
                })
    except Exception as e:
        print(f"An error occurred while reading the timing info: {e}")
    return timing_data


Range_Query_path = '../data/Range_Query_Timeinfo.txt'
KNN_path = '../data/KNN_Timeinfo.txt'

query_time = load_timeinfo(Range_Query_path)
KNN_time = load_timeinfo(KNN_path)



def range_query_timeplot(query_time, file_path = None):

    param_values_naive = [entry['param_value'] for entry in query_time if entry['method_name'] == 'Naive']
    times_naive = [entry['total_time'] for entry in query_time if entry['method_name'] == 'Naive']

    param_values_pivots = [entry['param_value'] for entry in query_time if entry['method_name'] == 'Pivots']
    times_pivots = [entry['total_time'] for entry in query_time if entry['method_name'] == 'Pivots']

    param_values_idistance = [entry['param_value'] for entry in query_time if entry['method_name'] == 'iDistance']
    times_idistance = [entry['total_time'] for entry in query_time if entry['method_name'] == 'iDistance']


    assert param_values_naive == param_values_pivots == param_values_idistance, "参数值必须匹配"

    param_values = param_values_naive
    x = np.arange(len(param_values))

    bar_width = 0.25
    plt.figure(figsize=(10, 6))


    bars_naive = plt.bar(x - bar_width, times_naive, width=bar_width, label='Naive', color='b')
    bars_pivots = plt.bar(x, times_pivots, width=bar_width, label='Pivots', color='g')
    bars_idistance = plt.bar(x + bar_width, times_idistance, width=bar_width, label='iDistance', color='r')


    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2f}', ha='center', va='bottom')


    add_value_labels(bars_naive)
    add_value_labels(bars_pivots)
    add_value_labels(bars_idistance)


    plt.xlabel('Parameter Value (ε)')
    plt.ylabel('Total Time (s)')
    plt.title('Comparison of Total Time (Range Query)')
    plt.xticks(x, param_values)
    plt.legend()

    if file_path:
        plt.savefig(file_path, format='png')


    plt.tight_layout()
    plt.show()

def KNN_query_timeplot(query_time, file_path = None):

    param_values_naive = [entry['param_value'] for entry in query_time if entry['method_name'] == 'Naive']
    times_naive = [entry['total_time'] for entry in query_time if entry['method_name'] == 'Naive']

    param_values_pivots = [entry['param_value'] for entry in query_time if entry['method_name'] == 'Pivots']
    times_pivots = [entry['total_time'] for entry in query_time if entry['method_name'] == 'Pivots']

    param_values_idistance = [entry['param_value'] for entry in query_time if entry['method_name'] == 'iDistance']
    times_idistance = [entry['total_time'] for entry in query_time if entry['method_name'] == 'iDistance']


    assert param_values_naive == param_values_pivots == param_values_idistance, "参数值必须匹配"

    param_values = param_values_naive
    x = np.arange(len(param_values))


    bar_width = 0.25
    plt.figure(figsize=(10, 6))


    bars_naive = plt.bar(x - bar_width, times_naive, width=bar_width, label='Naive', color='b')
    bars_pivots = plt.bar(x, times_pivots, width=bar_width, label='Pivots', color='g')
    bars_idistance = plt.bar(x + bar_width, times_idistance, width=bar_width, label='iDistance', color='r')


    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2f}', ha='center', va='bottom')


    add_value_labels(bars_naive)
    add_value_labels(bars_pivots)
    add_value_labels(bars_idistance)


    plt.xlabel('Parameter Value (K)')
    plt.ylabel('Total Time (s)')
    plt.title('Comparison of Total Time (KNN)')
    plt.xticks(x, param_values)
    plt.legend()

    if file_path:
        plt.savefig(file_path, format='png')

    plt.tight_layout()
    plt.show()

def range_query_avgcntplot(query_time, file_path = None):

    param_values_naive = [entry['param_value'] for entry in query_time if entry['method_name'] == 'Naive']
    times_naive = [entry['avg_counts'] for entry in query_time if entry['method_name'] == 'Naive']

    param_values_pivots = [entry['param_value'] for entry in query_time if entry['method_name'] == 'Pivots']
    times_pivots = [entry['avg_counts'] for entry in query_time if entry['method_name'] == 'Pivots']

    param_values_idistance = [entry['param_value'] for entry in query_time if entry['method_name'] == 'iDistance']
    times_idistance = [entry['avg_counts'] for entry in query_time if entry['method_name'] == 'iDistance']


    assert param_values_naive == param_values_pivots == param_values_idistance, "参数值必须匹配"

    param_values = param_values_naive
    x = np.arange(len(param_values))


    bar_width = 0.25
    plt.figure(figsize=(10, 6))


    bars_naive = plt.bar(x - bar_width, times_naive, width=bar_width, label='Naive', color='b')
    bars_pivots = plt.bar(x, times_pivots, width=bar_width, label='Pivots', color='g')
    bars_idistance = plt.bar(x + bar_width, times_idistance, width=bar_width, label='iDistance', color='r')


    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2f}', ha='center', va='bottom')


    add_value_labels(bars_naive)
    add_value_labels(bars_pivots)
    add_value_labels(bars_idistance)


    plt.xlabel('Parameter Value (ε)')
    plt.ylabel('Average number of calculations (s)')
    plt.title('Comparison of Total Average number of calculations (Range Query)')
    plt.xticks(x, param_values)
    plt.legend()

    if file_path:
        plt.savefig(file_path, format='png')


    plt.tight_layout()
    plt.show()

def KNN_query_avgcntplot(query_time, file_path = None):

    param_values_naive = [entry['param_value'] for entry in query_time if entry['method_name'] == 'Naive']
    times_naive = [entry['avg_counts'] for entry in query_time if entry['method_name'] == 'Naive']

    param_values_pivots = [entry['param_value'] for entry in query_time if entry['method_name'] == 'Pivots']
    times_pivots = [entry['avg_counts'] for entry in query_time if entry['method_name'] == 'Pivots']

    param_values_idistance = [entry['param_value'] for entry in query_time if entry['method_name'] == 'iDistance']
    times_idistance = [entry['avg_counts'] for entry in query_time if entry['method_name'] == 'iDistance']


    assert param_values_naive == param_values_pivots == param_values_idistance, "参数值必须匹配"

    param_values = param_values_naive
    x = np.arange(len(param_values))


    bar_width = 0.25
    plt.figure(figsize=(10, 6))


    bars_naive = plt.bar(x - bar_width, times_naive, width=bar_width, label='Naive', color='b')
    bars_pivots = plt.bar(x, times_pivots, width=bar_width, label='Pivots', color='g')
    bars_idistance = plt.bar(x + bar_width, times_idistance, width=bar_width, label='iDistance', color='r')


    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2f}', ha='center', va='bottom')


    add_value_labels(bars_naive)
    add_value_labels(bars_pivots)
    add_value_labels(bars_idistance)


    plt.xlabel('Parameter Value (K)')
    plt.ylabel('Average number of calculations (s)')
    plt.title('Comparison of Total Average number of calculations (KNN)')
    plt.xticks(x, param_values)
    plt.legend()

    if file_path:
        plt.savefig(file_path, format='png')


    plt.tight_layout()
    plt.show()



range_query_timeplot(query_time, '../plots/range_query_timeplot.png')
KNN_query_timeplot(KNN_time, '../plots/KNN_query_timeplot.png')
range_query_avgcntplot(query_time, '../plots/range_query_avgcntplot.png')
KNN_query_avgcntplot(KNN_time, '../plots/KNN_query_avgcntplot.png')
