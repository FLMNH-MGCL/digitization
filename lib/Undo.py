import os
import time

class UndoTool:
    def __init__(self):
        pass

    def run(self):
        pass

def AskUsage():
    prompt = str(
            "\nThis program will undo mass file rename sessions using the log files " \
            "from other previously ran scripts. Each script generates a csv file with " \
            "the following format:\n\nold path,new path\nold path,new path\nold path,new path\n" \
            "etc.\n\nThe program will essentially rename the files at the path 'new path' back " \
            "to what it was in 'old path'. All that is needed to do is supply the path to the csv " \
            "file and it will handle the rest! The program will be able to be started 5 seconds after " \
            "this prompt shows up!"
        )

    wanted = input("\nDo you want to see the usage information?\n [1]yes\n [2]no\n --> ")
    if wanted == '1' or wanted == 'y' or wanted == 'yes':
        print(prompt)
        time.sleep(5)


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
    AskUsage()
    Undo(FilePrompt())


if __name__ == '__main__':
    main()
