import os

def FilePrompt():
    csv_path = input('\nPlease input the path to the csv file that contains the old/new paths: ')
    csv_path = csv_path.strip()

    while not os.path.exists(csv_path) or not os.path.isfile(csv_path) or csv_path.split('.')[1].lower() != 'csv':
        print("\nCould not find path in filesystem or is not a csv file...")
        csv_path = input('\nPlease input the path to the csv file that contains the old/new paths: ')
        csv_path = csv_path.strip()

    return csv_path


def Undo(path):
    old_new_paths = []
    with open(path) as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            old_path = line.split(',')[0]
            new_path = line.split(',')[1]
            old_new_paths.append(tuple((old_path, new_path)))

    for old_path,new_path in old_new_paths:
        #os.rename(new_path, old_path)
        print('\nRenaming {} as {}\n'.format(new_path, old_path))

    print('Program completed...')

def main():
    Undo(FilePrompt())


if __name__ == '__main__':
    main()
