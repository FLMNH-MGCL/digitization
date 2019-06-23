#    MGCL 3947933    --> MGCL_3947933_D
#    MGCL 3947933(2) --> MGCL_3947933_V
#    MGCL 3947933_L  --> MGCL_3947933_L

import os
import sys
from tkinter import *
from tkinter import StringVar
from tkinter import filedialog
import tkinter.messagebox

old_new_names = []

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


#############################
# ***** RENAMING CODE ***** #

def GetSubDirs(path):
    subdirectories = []
    for img in os.listdir(path):
        if os.path.isdir(path + img):
            subdirectories.append(img)
    return subdirectories

def GetDirFiles(path):
    files = []
    for img in os.listdir(path):
        if not os.path.isdir(path + img):
            files.append(img)
    return files

def RecursiveRename(path):
    subdirectories = GetSubDirs(path)
    for dir in subdirectories:
        RecursiveRename(path + dir + '/')
    Rename(path)

def Rename(path):
    ext = ".CR2"
    print("\nWorking in... {}\n".format(path))

    for filename in GetDirFiles(path):
        print(filename)
        if filename.split('.')[1] != ext:
            continue

        # Separate ext and filename
        new_name = filename.split('.')[0]

        # instances of ' (2)' become _V
        new_name = new_name.replace("(2)", "_V")

        # Spaces replaced with '_'
        new_name = new_name.replace(' ', '_')

        # If not _V nor _L nor _D, add _D 
        if (new_name.find("_V") == -1 and new_name.find("_L") == -1 and new_name.find("_D") == -1):
            new_name += "_D"

        if filename != new_name + ext:
            #os.rename(path + filename, path + (new_name + ext))
            old_new_names.append(tuple((path + filename, path + (new_name + ext))))
            print(new_name + ext)

    print("Directory completed.")


def Undo():
    # check if there is anything to undo
    if len(old_new_names) == 0:
        return 'There is nothing to undo.'

    return 'This function needs to be tested first'

    # old_new_names list of tuples must include the paths!
    for old_name,new_name in old_new_names:
        os.rename(new_name, old_name)

    return 'Changes have been reversed.'


def main():
    choice = input("\nWould you prefer to use a: \n [1]command-line interface \n [2]graphical interface \n--> ")
    
    if choice == '1':
        ext = ".CR2"
        print("\nThis program will help you rename " + ext + " files in a directory")
        path = input("Please type the path of the directory: ")
        if not path.endswith('/') or not path.endswith('\\'):
            path += '/'

        method = input("\nChoose 1 of the following: \n [1]Standard (All " + ext + " files in this directory level) \n [2]Recursive (All " + ext + " files in this directory level and every level below) \n--> ")
        
        if method == '1':
            Rename(path)

        elif method == '2':
            # Recursive
            RecursiveRename(path)

        else:
            print("Input error.")
            sys.exit(1)

    elif choice == '2':
        window = Tk()
        my_gui = GUI(window)
        my_gui.mainloop()

    print("\nProgram completed.\n")

# Driver Code
if __name__ == '__main__':
    main()
