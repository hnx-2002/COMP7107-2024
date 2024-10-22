import pandas as pd

# reset the Pandas
pd.set_option('display.max_columns', None)  # All lines
pd.set_option('display.expand_frame_repr', False)  # not \n
pd.set_option('display.max_rows', 50)  # rows number (able to modify)

# load data
df = pd.read_parquet('../Datasets/subset.parquet')

# Step 1.1
# longitude
min_lon = df['Start_Lon'].min()
max_lon = df['Start_Lon'].max()

# latitude
min_lat = df['Start_Lat'].min()
max_lat = df['Start_Lat'].max()

# datetime
df['Trip_Pickup_DateTime'] = pd.to_datetime(df['Trip_Pickup_DateTime'])

min_time = df['Trip_Pickup_DateTime'].min().timestamp()
max_time = df['Trip_Pickup_DateTime'].max().timestamp()

# # print and save
# df.info()
# print(df.head(20))

print(min_lon, max_lon, min_lat, max_lat, min_time, max_time, "\n\n\n\n")

# df.to_parquet('subset.parquet')
# df.to_csv('subset.csv')


# Step 1.2
# grid with 100x100x100

grid_size = 100


# # step int(100 * ((x-min_x) / (max_x-min_x+0.000001))
# lon_step = (max_lon - min_lon) / grid_size
# lat_step = (max_lat - min_lat) / grid_size
# time_step = (max_time - min_time) / grid_size

# which grid
def get_partition(value, min_value, max_value):
    return int(100 * (value - min_value) / (max_value - min_value + 1e-6))  # protect from overflow


# allocate
df['lon_partition'] = df['Start_Lon'].apply(lambda lon: get_partition(lon, min_lon, max_lon))
df['lat_partition'] = df['Start_Lat'].apply(lambda lat: get_partition(lat, min_lat, max_lat))
df['time_partition'] = df['Trip_Pickup_DateTime'].apply(
    lambda time: get_partition(time.timestamp(), min_time, max_time))

df.info()
print(df.head(20), "\n\n\n\n")

df.to_parquet('../Datasets/data_select.parquet', index=False)

# Step 1.3
# dictionary store the grids info
grid = {}

# Traverse every line
for _, row in df.iterrows():
    # Grid coordinates
    cell_key = (row['lon_partition'], row['lat_partition'], row['time_partition'])

    # creat new list if not exist
    if cell_key not in grid:
        grid[cell_key] = []

    # insert
    grid[cell_key].append(
        (row['Start_Lon'], row['Start_Lat'], row['Trip_Pickup_DateTime'].timestamp(), row['Total_Amt']))

# output file to grid.txt
with open('../Datasets/grid.txt', 'w') as f:
    # write min and max
    f.write(f"{min_lon}, {max_lon}\n")
    f.write(f"{min_lat}, {max_lat}\n")
    f.write(f"{min_time}, {max_time}\n")

    # sort
    sorted_cells = sorted(grid.keys())

    # Traverse
    for cell_key in sorted_cells:
        cell_x, cell_y, cell_t = cell_key

        # Total_Amount
        num_records_in_cell = len(grid[cell_key])

        # write in
        f.write(f"({cell_x},{cell_y},{cell_t})\n")
        f.write(f"{num_records_in_cell}\n")

        # write details
        for record in grid[cell_key]:
            f.write(f"{record[0]},{record[1]},{record[2]},{record[3]}\n")
