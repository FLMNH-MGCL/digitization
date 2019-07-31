#    MGCL 3947933    --> MGCL_3947933_D
#    MGCL 3947933(2) --> MGCL_3947933_V
#    MGCL 3947933_L  --> MGCL_3947933_L

import os
import sys
import time
import datetime
import csv
import re
#from tkinter import *
#from tkinter import StringVar
#from tkinter import filedialog
#import tkinter.messagebox

old_new_paths = []

##############################
# ******** GUI CODE ******** #
"""
class GUI:
    window = None
    target_dir = None
    recursively = False
    #status_message = None

    def __init__(self, window):
        self.window = self.InitWindow(window)


    def mainloop(self):
        self.window.mainloop()


    def Run(self, status_message):
        # check if user hit run before selected target folder
        if self.target_dir == None:
            tkinter.messagebox.showerror(title='User Error', message='You must select a path first')
            return

        # check trailing slash
        if not self.target_dir.endswith('/') or not self.target_dir.endswith('\\'):
            self.target_dir += '/'

        # no errors up to this point, renaming will run so update status
        status_message.set('Running...')

        # check method (single directory or recursive renaming)
        if not self.recursively:
            Rename(self.target_dir)

        elif self.recursively:
            RecursiveRename(self.target_dir)

        status_message.set('Finished...')


    def Undo(self, status_message):
        # call non-class Undo function
        message = Undo()

        # update status bar / pop up message for error
        if message == 'There is nothing to undo.':
            tkinter.messagebox.showerror(title='User error', message=message)
        else:
            status_message.set(message)


    def ToggleRecursive(self, value):
        if value == 0:
            self.recursively = False
        elif value == 1:
            self.recursively = True


    def HelpPromt(self):
        prompt = str(
            "This program will help you rename .CR2 and .JPG image files. Simply select (or type in) the target folder, " \
            "select whether or not to run the algorithm recursively and then hit run.\n\nTo run the algorithm recursively" \
            " means that in addition to the target directory, every subdirectory underneath will also undergo the renaming." \
            " For example, if you target the folder /home/user/target/ and that folder contains a folder called random, if " \
            "you run without recursion then only files inside target are changed. If you run recursively, files that are also " \
            "inside the subfolder random (and files within any additional subfolders) will be renamed.\n\n" \
            "All changes are temporarily recorded in the program, so if you want to undo what the script did just hit the undo " \
            "button BEFORE you close the window!"
        )
        tkinter.messagebox.showinfo('Usage Help', prompt)


    def SelectFolder(self):
        self.target_dir = filedialog.askdirectory()


    def InitWindow(self, window):
        # ***** GENERAL WINDOW ***** #
        window.geometry("500x300")
        window.title('FLMNH File Rename Tool')
        #window.config(background='seashell3')
        window.config(background='dimgray')

        # ***** STATUS BAR ***** #
        status_message = StringVar()
        status = Label(window, textvariable=status_message, bd=1, relief=SUNKEN, anchor=W)
        status_message.set("Waiting...")
        status.pack(side=BOTTOM, fill=X)
        
        # ***** TOP MENU ***** #
        menu = Menu(window)
        window.config(menu=menu)
        subMenu = Menu(menu)
        menu.add_cascade(label="Help", menu=subMenu)
        subMenu.add_command(label="Usage", command=self.HelpPromt)

        # ***** BUTTONS ***** #
        button = Button(window, text="Select Folder", command=self.SelectFolder)
        button.pack()

        toggle = IntVar()
        recursion_checkbox = Checkbutton(window, text='Recursive', variable=toggle, command= lambda: self.ToggleRecursive(toggle.get()))
        recursion_checkbox.pack()

        run_button = Button(window, text="Run", command= lambda: self.Run(status_message))
        run_button.pack()

        undo_button = Button(window, text="Undo Changes", command= lambda: self.Undo(status_message))
        undo_button.pack()

        quit_button = Button(window, text='Quit', command=window.destroy)
        quit_button.pack()

        return window
"""

#############################
# ***** RENAMING CODE ***** #
def WriteOut(path):
    d = datetime.datetime.today()
    date = str(d.year) + '_' + str(d.month) + '_' + str(d.day)
    filename = path + 'RENAMED_SCRIPT_LOG_' + date

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
    csv_file.write('Old Path,New Path\n')
    for old_path,new_path in old_new_paths:
        csv_file.write(old_path + ',' + new_path + '\n')


def AskUsage():
    prompt = str(
            "\nThis program will rename the freshly scanned specimen images. This program is temporary, " \
            "it is meant to be used until the Data Matrix Reader program is finalized. The usage for this " \
            "is as follows:\n\nYou will be asked to enter the path to the folder that contains all of the " \
            "specimen images to be rename. If your terminal supports it, you can simply drag and drop the " \
            "folder into it. From here, the program will rename all images within the provided directory. " \
            "Once it is finished, you will have an opportunity to undo the changes made, so please review " \
            "them carefully. If you choose to not undo, and you exit / allow the program to complete, you " \
            "will not be able to undo unless you run the separate undo program. After 5 seconds of viewing " \
            "this prompt, you can start!"
        )
    wanted = input("\nDo you want to see the usage information?\n [1]yes\n [2]no\n --> ")
    if wanted == '1' or wanted == 'y' or wanted == 'yes':
        print(prompt)
        time.sleep(5)

def DirPrompt():
    parent_directory = input('\nPlease input the path to the directory that contains the images: ')
    parent_directory = parent_directory.strip()

    if not parent_directory.endswith('/') or not parent_directory.endswith('\\'):
        parent_directory += '/'

    while not os.path.exists(parent_directory) or not os.path.isdir(parent_directory):
        print("\nCould not find path in filesystem or is not a directory...")
        parent_directory = input('\nPlease input the path to the directory that contains the images: ')
        parent_directory = parent_directory.strip()

        if not parent_directory.endswith('/') or not parent_directory.endswith('\\'):
            parent_directory += '/'

    return parent_directory


def GetSubDirs(path):
    subdirectories = []
    for img in sorted(os.listdir(path)):
        if os.path.isdir(path + img):
            subdirectories.append(img)
    return subdirectories

def GetDirFiles(path):
    files = []
    valid = ['JPG', 'jpg', 'CR2', 'cr2']
    for img in sorted(os.listdir(path)):
        if not os.path.isdir(path + img) and img.split('.')[1] in valid:
            files.append(img)
    return files

def RecursiveRename(path):
    subdirectories = GetSubDirs(path)
    for dir in subdirectories:
        RecursiveRename(path + dir + '/')
    Rename(path)

def Rename(path):
    global old_new_paths
    print("\nWorking in... {}\n".format(path))

    for filename in GetDirFiles(path):
        ext = '.' + filename.split('.')[1]

        # Separate ext and filename
        new_name = filename.split('.')[0]

        # instances of ' (2)' become _V
        new_name = new_name.replace("(2)", "_V") # MGCL ID (2).CR2 => MGCL ID _V.CR2

        # Spaces replaced with '_'
        new_name = new_name.replace(' ', '_') # MGCL ID _V.CR2 => MGCL_ID__V.CR2

        new_name = re.sub("\_+", "_", new_name) # MGCL_ID__V.CR2 => MGCL_ID_V.CR2

        # If not _V nor _L nor _D, add _D 
        if (new_name.find("_V") == -1 and new_name.find("_L") == -1 and new_name.find("_D") == -1):
            new_name += "_D"

        if filename != new_name + ext:
            os.rename(path + filename, path + (new_name + ext))
            old_new_paths.append(tuple((path + filename, path + (new_name + ext))))
            print("\nRenaming {} as {}\n".format(path + filename, path + new_name + ext))

    print("Directory completed.")


def Undo():
    # check if there is anything to undo
    if len(old_new_paths) == 0:
        return 'There is nothing to undo.'

    # return 'This function needs to be tested first'

    # old_new_names list of tuples must include the paths!
    for old_name,new_name in old_new_paths:
        os.rename(new_name, old_name)

    return 'Changes have been reversed.'


def Wait(path):
    time.sleep(5)
    global old_new_paths

    wait = True
    print("Program completed... Please review changes.")

    while wait == True:
        undo = input("Do you wish to undo?\n [1]yes\n [2]no\n --> ")
        if undo == '1' or undo == 'y' or undo =='yes':
            print(Undo())
            wait = False
        elif undo == '2' or undo == 'n' or undo == 'no':
            wait = False
        else:
            print('Input error. Invalid option.')
            continue
    
    WriteOut(path)
    repeat = input ("Do you want to repeat program in a new parent directory?\n [1]yes\n [2]no\n --> ")
    if repeat == '1' or repeat == 'y' or repeat == 'yes':
        old_new_paths.clear()
        AskUsage()
        Run(DirPrompt())
    else:
        print("Exiting...")
        time.sleep(2)


def Run(parent_directory):
    method = input("\nChoose 1 of the following: \n [1]Standard (All image files in this directory level) \n [2]Recursive " \
            "(All image files in this directory level and every level below) \n--> ")

    if method == '1':
        Rename(parent_directory)

    elif method == '2':
        # Recursive
        RecursiveRename(parent_directory)

    else:
        print("Input error.")
        sys.exit(1)

    print('All images handled...')
    Wait(parent_directory)


def main():
    global old_new_paths

    #choice = input("\nWould you prefer to use a: \n [1]command-line interface \n [2]graphical interface \n--> ")
    choice = '1'

    if choice == '1':
        AskUsage()
        Run(DirPrompt())

    #elif choice == '2':
        #window = Tk()
        #my_gui = GUI(window)
        #my_gui.mainloop()

    print("\nProgram completed.\n")

# Driver Code
if __name__ == '__main__':
    main()
