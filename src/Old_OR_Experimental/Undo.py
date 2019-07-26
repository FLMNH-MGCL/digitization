import os

def DirPrompt():
    csv_path = input('\nPlease input the path to the csv file that contains the old/new paths: ')
    csv_path = csv_path.strip()

    while not os.path.exists(csv_path) or not os.path.isfile(csv_path):
        print("\nCould not find path in filesystem or is not a file...")
        csv_path = input('\nPlease input the path to the csv file that contains the old/new paths: ')
        csv_path = csv_path.strip()

    return parent_directory


def Undo():
    pass


def main():
    pass


if __name__ == '__main__':
    main()
