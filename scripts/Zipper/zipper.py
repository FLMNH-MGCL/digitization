import os
import shutil
from pathlib import Path
import math

GB = 1073741824

def group_files(path):
    global GB
    # all_files = sorted(os.listdir(path))
    # proposed = []
    # total_size = 0
    # for f in all_files:
    #     print('{} Size: {}'.format(f, os.stat(path + f).st_size))
    total_size = sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())
    num_files = sum(f.stat().st_size * 0 + 1 for f in path.glob('**/*') if f.is_file())
    num_groups = int(math.ceil(total_size / GB))
    avg_size_file = total_size / num_files
    file_per_group = math.floor(num_files / num_groups)


    print('Approximate total size: {} BYTES'.format(total_size))
    print('Approximate num of files: {}'.format(num_files))
    print('Approximate size per files: {} BYTES'.format(avg_size_file))
    print('Approximate number of groups: {}'.format(num_groups))
    print('Approximate number of files per group: {}'.format(file_per_group))



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