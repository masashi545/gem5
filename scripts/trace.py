import sys
import pandas as pd

trace_path = sys.argv[1]
df = pd.read_csv(trace_path, encoding='utf-8')

time_list = []
src_list = []
dest_list = []
size_list = []
type_list = []

t = -1
now_time = -1

for row in df.itertuples():
    time = row[1]
    src = row[2]
    dest = row[3]
    size = row[4]
    typee = row[5]

    if src == dest:
        continue

    if now_time < time:
        t += 1
    now_time = time
    time_list.append(t)
    src_list.append(src)
    dest_list.append(dest)
    size_list.append(size)
    type_list.append(typee)

new_df = pd.DataFrame({'time':time_list, 'src':src_list, 'dest':dest_list, 'size':size_list, 'type':type_list})
output_path = trace_path.replace("./m5out", "../booksim2")
new_df.to_csv(output_path, index=False, header=False)