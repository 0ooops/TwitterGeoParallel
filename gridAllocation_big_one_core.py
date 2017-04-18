# coding: utf-8
# This is a one-node-one-core program used for processing Twitter geodata.

import json
import time
from mpi4py import MPI

# MPI Initialization
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# Only one process, no need to scatter the job
start_time = time.time()
file_name = "./bigTwitter.json"

with open('melbGrid.json', encoding="utf-8") as grid_file:
    grid_all = json.load(grid_file)

len_grid = len(grid_all["features"])
count_matrix = []
all_matrix = []
grid_list = [(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3),(2,0),(2,1),(2,2),(2,3),(2,4),(3,2),(3,3),(3,4)]
y_list = [2,6,10,13]

for m in range(4):
    count_matrix.append([])
    for n in range(5):
        count_matrix[m].append(0)

# Operations on each process
with open(file_name, encoding="utf-8") as twitter_file:
    for line in twitter_file:
        if len(line) > 2:
            if line[-2] == ",":
                item = json.loads(line[:-2])
                x_twitter = item["json"]["coordinates"]["coordinates"][0]
                y_twitter = item["json"]["coordinates"]["coordinates"][1]
                x_grid = -1
                y_grid = -1
                for p in range(8, 13):
                    if grid_all["features"][p]["properties"]["xmin"] <= x_twitter <= \
                            grid_all["features"][p]["properties"]["xmax"]:
                        x_grid = p - 8
                        break
                for q in y_list:
                    if grid_all["features"][q]["properties"]["ymin"] <= y_twitter <= \
                            grid_all["features"][q]["properties"]["ymax"]:
                        y_grid = y_list.index(q)
                        break
                if (y_grid, x_grid) in grid_list:
                    count_matrix[y_grid][x_grid] += 1
    all_matrix = count_matrix
twitter_file.close()

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
    print("The time for processing is: %r" % (end_time - start_time))