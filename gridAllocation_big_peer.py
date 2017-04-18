# coding: utf-8
# This is a peer-based parallel computing program used for processing Twitter geodata.

import json
from mpi4py import MPI
import time

# MPI Initialization
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# Preprocessing - Decompose big json file
arr_job = []
if rank == 0:
    start_time = time.time()
    file_name = "./bigTwitter.json"
    num_process = size
    count = 0
    len_twitter = 3218504 - 2 #The 'magic number' 3218504 was got by commond 'wc -l filename'. There are other ways, but this is simple and fast.
    len_local = int(len_twitter / num_process) + 1
    arr_json = []

    with open(file_name, encoding="utf-8") as twitter_file:
        for line in twitter_file:
            if len(line) > 2:
                if line[-2] == ",":
                    item = json.loads(line[:-2])
                    if count % len_local == 0:
                        file_name_new = "./big_twitter_" + str(int(count/len_local)) + ".json"
                        arr_job.append(file_name_new)
                        file = open(file_name_new, 'w')
                        arr_json = [item["json"]["coordinates"]]
                    elif count % len_local == len_local - 1 or count == len_twitter - 1:
                        arr_json.append(item["json"]["coordinates"])
                        file.write(json.dumps(arr_json))
                        file.close()
                    else:
                        arr_json.append(item["json"]["coordinates"])

                count += 1
    twitter_file.close()
    process_time = time.time()
# Scatter work units to all processes
unit = comm.scatter(arr_job, root=0)

# Operations on each process
with open(unit, encoding="utf-8") as local_file:
    twitter_local = json.load(local_file)

with open('melbGrid.json', encoding="utf-8") as grid_file:
    grid_all = json.load(grid_file)

len_grid = len(grid_all["features"])
count_matrix = []
grid_list = [(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3),(2,0),(2,1),(2,2),(2,3),(2,4),(3,2),(3,3),(3,4)]
y_list = [2,6,10,13]

for m in range(4):
    count_matrix.append([])
    for n in range(5):
        count_matrix[m].append(0)

for i in range(len(twitter_local)):
    x_twitter = twitter_local[i]["coordinates"][0]
    y_twitter = twitter_local[i]["coordinates"][1]
    x_grid = -1
    y_grid = -1
    for p in range(8, 13):
        if grid_all["features"][p]["properties"]["xmin"] <= x_twitter <= grid_all["features"][p]["properties"]["xmax"]:
            x_grid = p - 8
            break
    for q in y_list:
        if grid_all["features"][q]["properties"]["ymin"] <= y_twitter <= grid_all["features"][q]["properties"]["ymax"]:
            y_grid = y_list.index(q)
            break

    if (y_grid, x_grid) in grid_list:
        count_matrix[y_grid][x_grid] += 1

# Prepare for reduce
all_matrix = []
all_sum = []
for m in range(4):
    all_sum.append([])
    for n in range(5):
        all_sum[m].append(0)

# Reduce
for i in range(4):
    for j in range(5):
        all_sum[i][j] = comm.reduce(count_matrix[i][j], root=0, op=MPI.SUM)
all_matrix = all_sum

# Process and show the result
if rank == 0:

    # Grid Rank
    grid_dict = {}
    for k in grid_list:
        str_grid = chr(ord('A') + k[0]) + str(k[1] + 1)
        grid_dict[str_grid] = all_matrix[k[0]][k[1]]
    sorted_list = sorted(grid_dict.items(), key=lambda d:d[1], reverse = True)
    print(sorted_list)

    # Row Rank
    row = []
    row_dict = {}
    for i in range(4):
        row.append(0)
        for j in range(5):
            row[i] += all_matrix[i][j]
    for k in range(4):
        str_row = chr(ord('A') + k) + "-Row"
        row_dict[str_row] = row[k]
    sorted_row = sorted(row_dict.items(), key=lambda d:d[1], reverse = True)
    print(sorted_row)

    # Column Rank
    col = []
    col_dict = {}
    for j in range(5):
        col.append(0)
        for i in range(4):
            col[j] += all_matrix[i][j]

    for k in range(5):
        str_col = "Column " + str(k + 1)
        col_dict[str_col] = col[k]
    sorted_col = sorted(col_dict.items(), key=lambda d:d[1], reverse = True)
    print(sorted_col)
    end_time = time.time()

    # Time
    print("The time for preprocessing is: %r" % (process_time - start_time))
    print("The time for parallel computing is: %r" %(end_time - process_time))