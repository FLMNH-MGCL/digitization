import os
import shutil

GB = 1073741824

def group_files(path):
    # group by groups of 1GB
    all_files = sorted(os.listdir(path))
    proposed = []
    total_size = 0
    for f in all_files:
        print('{} Size: {}'.format(f, os.stat(path + f).st_size))


def main():
    group_files(input())


if __name__ == '__main__':
    main()