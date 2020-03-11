import os
from shutil import make_archive
from shutil import copyfile
from shutil import rmtree
from pathlib import Path
import math

GB = 1073741824

class Zipper:
    def __init__(self):
        pass

    def run(self):
        pass

def dir_prompt(destination):
    parent_directory = ''
    if not destination:
        parent_directory = input('\nPlease input the path to the directory that contains the files: \n --> ')
    else:
        parent_directory = input('\nPlease input the path to the directory you would like the archive(s) to go: \n --> ')

    parent_directory = parent_directory.strip()

    if not parent_directory.endswith('/') or not parent_directory.endswith('\\'):
        parent_directory += '/'

    while not os.path.exists(parent_directory) or not os.path.isdir(parent_directory):
        print("\nCould not find path in filesystem or is not a directory...")
        parent_directory = input('\nPlease input an appropriate path: \n --> ')
        parent_directory = parent_directory.strip()

        if not parent_directory.endswith('/') or not parent_directory.endswith('\\'):
            parent_directory += '/'

    return parent_directory

def zip(path, destination, groups):
    # shutil.copyFile()
    for group in groups:
        archive_name = get_name(destination)
        os.mkdir(destination + archive_name + '/')
        for f in group:
            f_name = ''
            if '/' in f:
                f_name = f.split('/').pop()
            else:
                f_name = f.split('\\').pop()
            # print(f_name)
            copyfile(f, destination + archive_name + '/' + f_name)
    
    dirs = [f for f in os.listdir(destination) if os.path.isdir(destination + f + '/')]
    for dir in sorted(dirs):
        print('Current archive: {}'.format(destination + dir))
        make_archive(base_name=destination + dir, format='zip', root_dir=destination + dir + '/')
        print('Completed. Removing temporary directory.\n')
        rmtree(destination + dir + '/', ignore_errors=True)


def get_name(path):
    i = 0
    while os.path.exists(path + 'archive_' + str(i) + '.zip') or os.path.exists(path + 'archive_' + str(i) + '/'):
        i += 1
    
    return 'archive_' + str(i)


def group_files(path, destination):
    global GB

    # get dictionary of (paths, file size) and sort in decreasing order
    files = dict((str(f), f.stat().st_size) for f in path.glob('**/*') if f.is_file() and 'LOW-RES' in str(f))

    # print(files)

    files = {k: v for k, v in sorted(files.items(), key=lambda item: item[1], reverse=True)}
    file_list = list(files.keys())

    # calculate total size of all dir
    total_size = sum(f.stat().st_size for f in path.glob('**/*') if f.is_file() and 'LOW-RES' in str(f))

    # calculate total num of files in all levels at and below dir
    num_files = sum(f.stat().st_size * 0 + 1 for f in path.glob('**/*') if f.is_file() and 'LOW-RES' in str(f))

    # calculate approx num of groups of 1GB
    num_groups = int(math.ceil(total_size / GB))

    # calculate approx avg file size
    avg_size_file = total_size / num_files

    # calculate approx file count per group
    file_per_group = math.floor(num_files / num_groups)

    # print(file_list)
    print('\nApproximate total size: {} BYTES'.format(total_size))
    print('Approximate num of files: {}'.format(num_files))
    print('Approximate size per files: {} BYTES'.format(avg_size_file))
    print('Approximate number of groups: {}'.format(num_groups))
    print('Approximate number of files per group: {}\n'.format(file_per_group))

    # if num_groups == 1:
    #     # no need to sort for one group
    #     # zip_single(path)
    #     os.chdir(path)
    #     name = get_name(destination)
    #     shutil.make_archive(base_name=destination + name, format='zip', root_dir=path)
    #     return

    groups = []
    for x in range(0, num_groups):
        current_group = []
        remaining_space = GB
        while len(file_list) > 0 and remaining_space > files[file_list[0]]:
            current_group.append(file_list[0])
            # print(len(current_group))
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

    zip(path, destination, groups)

    # print(groups)





def main():
    group_files(Path(dir_prompt(False)), dir_prompt(True))
    print('/nProgram Completed.')


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