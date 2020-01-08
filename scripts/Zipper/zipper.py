import os
import shutil
from pathlib import Path
import math

GB = 1073741824

def group_files(path):
    global GB

    # get dictionary of (paths, file size) and sort in decreasing order
    files = dict((str(f), f.stat().st_size) for f in path.glob('**/*') if f.is_file())
    files = {k: v for k, v in sorted(files.items(), key=lambda item: item[1], reverse=True)}
    file_list = list(files.keys())

    # calculate total size of all dir
    total_size = sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())

    # calculate total num of files in all levels at and below dir
    num_files = sum(f.stat().st_size * 0 + 1 for f in path.glob('**/*') if f.is_file())

    # calculate approx num of groups of 1GB
    num_groups = int(math.ceil(total_size / GB))

    # calculate approx avg file size
    avg_size_file = total_size / num_files

    # calculate approx file count per group
    file_per_group = math.floor(num_files / num_groups)

    print(file_list)
    print('Approximate total size: {} BYTES'.format(total_size))
    print('Approximate num of files: {}'.format(num_files))
    print('Approximate size per files: {} BYTES'.format(avg_size_file))
    print('Approximate number of groups: {}'.format(num_groups))
    print('Approximate number of files per group: {}'.format(file_per_group))

    groups = []
    for x in range(0, num_groups):
        current_group = []
        remaining_space = GB
        while len(file_list) > 0 and remaining_space > files[file_list[0]]:
            current_group.append(file_list[0])
            print(len(current_group))
            remaining_space = remaining_space - files[file_list[0]]
            file_list.pop(0)
        
        for i,f in enumerate(file_list):
            if files[f] == remaining_space:
                current_group.append(file_list[i])
                remaining_space = 0
                file_list.pop(i)
                break
            elif files[f] < remaining_space:
                current_group.append(file_list[i])
                remaining_space = remaining_space - files[f]
                file_list.pop(i)
            else: continue
        groups.append(current_group)

    print(groups)





def main():
    group_files(Path(input()))


if __name__ == '__main__':
    main()


    """
    Find the target group size. This is the sum of all sizes divided by n.
    Create a list of sizes.
    Sort the files decreasing in size. 
    for each group
        while the remaining space in your group is bigger than the first element of the list
            take the first element of the list and move it to the group
        for each element
            find the elemnet for which the difference between group size and target group size is minimal
        move this elemnt to the group
    """