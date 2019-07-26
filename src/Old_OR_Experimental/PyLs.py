import os
import datetime

csv_data = []

def GetFolders(path):
    dirs = []
    for dir in sorted(os.listdir(path)):
        if os.path.isdir(path + dir):
            dirs.append(dir)
    return dirs


def GetFiles(path):
    files = []
    for file in sorted(os.listdir(path)):
        if os.path.isfile(path + file) and file != '.DS_STORE':
            files.append(file)
    return files


def WriteOut(path):
    global csv_data
    d = datetime.datetime.today()
    date = str(d.year) + '_' + str(d.month) + '_' + str(d.day)
    filename = path + 'WLS_SCRIPT_LOG_' + date

    count = ''
    num = 0
    while os.path.exists(filename + count + '.csv'):
        if num == 0:
            filename += '_'
        num += 1
        count = str(num)

    if num == 0:
        filename = filename + '.csv'
    else:
        filename = filename + count + '.csv'

    csv_file = open(filename, mode='w')
    for data in csv_data:
        csv_file.write(data)


def wls(path):
    global csv_data
    files = GetFiles(path)
    dirs = GetFolders(path)

    for dir in dirs:
        wls(path + dir + '/')
    for file in files:
        csv_data.append(path + file + '\n')
    csv_data.append('\n')

def main():
    wls(os.getcwd() + '/')
    WriteOut(os.getcwd() + '/')
    #print(os.getcwd())


if __name__ == '__main__':
    main()
