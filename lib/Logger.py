# class to be used for writing log files
import datetime
import os

class Logger:
    def __init__(self, target_path, program_name):
        self.target_path = target_path
        self.program_name = program_name
        self.log_content = dict()
        self.error_content = []

    def get_details(self):
        print(self.target_path)
        print(self.program_name)

    def set_log_content(self, log_content):
        if not type(log_content) is dict:
            print('ERROR: INVALID LOG TYPE??')
        else:
            self.log_content = log_content
    
    def set_error_content(self, error_content):
        self.error_content = error_content
    
    def generate_unique_filename(self, filename, ext):
        d = datetime.datetime.today()
        date = '{}_{}_{}'.format(str(d.year), str(d.month), str(d.day))

        filename = '{}_{}'.format(filename, date)

        count = ''
        num = 0
        while os.path.exists(filename + count + ext):
            if num == 0 :
                filename += '_'
            num += 1
            count = str(num)

        if num == 0:
            filename = filename + ext
        else:
            filename = filename + count + ext

        return filename

    def write_out(self):
        content_log_filename = self.generate_unique_filename('{}_LOG'.format(self.program_name), '.csv')
        error_log_filename = self.generate_unique_filename('{}_ERRORS'.format(self.program_name), '.txt')

        print("Writing log file to {}\n".format(content_log_filename))

        csv_file = open(content_log_filename, mode='w')
        csv_file.write('Old Path,New Path\n')
        for old_path,new_path in self.log_content:
            csv_file.write("{},{}\n".format(old_path,new_path))
        csv_file.close()

        if self.error_content is None or len(self.error_content) == 0:
            return

        print("Writing error file to {}\n".format(error_log_filename))

        txt_file = open(error_log_filename, mode='w')
        txt_file.write('ERROR LOG:\n')
        for error in self.error_content:
            txt_file.write("{}\n".format(error))
