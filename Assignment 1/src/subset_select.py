import pandas as pd

# reset the Pandas
pd.set_option('display.max_columns', None)  # All lines
pd.set_option('display.expand_frame_repr', False)  # not \n
pd.set_option('display.max_rows', 50)  # rows number (able to modify)

# 13300000 lines
df = pd.read_parquet('../Datasets/yellow_tripdata_2009-02.parquet')

# print some lines
Rows, Columns = df.shape
print(f"行数: {Rows}")
print(f"列数: {Columns}")
print(df.head(30), "\n\n\n")

# select interest
df_interest = df[['Trip_Pickup_DateTime', 'Start_Lon', 'Start_Lat', 'Total_Amt']]

# detect time error
df_interest['Trip_Pickup_DateTime'] = pd.to_datetime(df_interest['Trip_Pickup_DateTime'], errors='coerce')

start_date = '2009-02-01'
end_date = '2009-03-01'
df_out_of_range = df_interest[
    (df_interest['Trip_Pickup_DateTime'] < start_date) |
    (df_interest['Trip_Pickup_DateTime'] > end_date)
]
print(f"out of range: {df_out_of_range.shape[0]}")
print(df_out_of_range)



# find outliers
df_lon_outliers = df_interest[~df_interest['Start_Lon'].between(-180, 180)]
df_lat_outliers = df_interest[~df_interest['Start_Lat'].between(-90, 90)]

# merge
df_outliers = pd.concat([df_lon_outliers, df_lat_outliers]).drop_duplicates()

# print the outliers
print(f"Lon and Lat outliers rows: {df_outliers.shape[0]}")
print(df_outliers)

# save to file
df_outliers.to_csv('../Datasets/outliers.csv', index=False)

df_interest = df_interest[(df_interest['Start_Lon'].between(-180, 180)) &
                          (df_interest['Start_Lat'].between(-90, 90))]

# 10%
# df_select = df_interest.head(1330000)

df_interest.info()
rows, columns = df_interest.shape
print(f"rows: {rows}\n")
print(f"columns: {columns}\n")
print(df_interest.head(50), "\n\n\n")

# df_interest.to_parquet('../Datasets/subset.parquet', index=False)
# df_interest.to_csv('../Datasets/subset.csv', index=False)
