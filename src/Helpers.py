import os
import time

class Helpers:
    @staticmethod
    def ask_usage(prompt):
        wanted = input("\nDo you want to see the usage information?\n [1]yes\n [2]no\n --> ")
        if wanted == '1' or wanted == 'y' or wanted == 'yes':
            print(prompt)
            time.sleep(5)

    @staticmethod
    def get_existing_path(path, is_dir):
        correct_path = path
        while not os.path.exists(correct_path) or (is_dir and not os.path.isdir(correct_path)) or (not is_dir and os.path.isdir(correct_path)):
            print("\nCould not find path / file in filesystem (or is wrong type, i.e. requires file but provided directory)...")
            correct_path = input('\nPlease input an appropriate path: \n --> ')
            correct_path = correct_path.strip()

            if is_dir:
                if not correct_path.endswith('/') or not correct_path.endswith('\\'):
                    correct_path += '/'
            else:
                if correct_path.endswith('/') or correct_path.endswith('\\'):
                    correct_path = correct_path[:-1]
        
        return correct_path

    @staticmethod
    def path_prompt(prompt):
        path = input(prompt)
        path = path.strip()
        path = path.replace('\\', '/')

        if not path.endswith('/') or not path.endswith('\\'):
            path += '/'

        return path

    @staticmethod
    def file_prompt(prompt):
        file_path = input(prompt)
        file_path = file_path.strip()
        file_path = file_path.replace('\\', '/')

        if file_path.endswith('/') or file_path.endswith('\\'):
            file_path = file_path[:-1]
        
        return file_path