# class to be used for writing log files
import datetime
import os

class Logger:
    def __init__(self, target_path, program_name):
        self.target_path = target_path
        self.program_name = program_name
        self.log_content = None
        self.error_content = None

    def get_details(self):
        print(self.target_path)
        print(self.program_name)

    def set_log_content(self, log_content):
        self.log_content = log_content
    
    def set_error_content(self, error_content):
        self.error_content = error_content
    
    def generate_unique_filename(self, filename):
        d = datetime.datetime.today()
        date = '{}_{}_{}'.format(str(d.year), str(d.month), str(d.day))

        filename = '{}_{}'.format(filename, date)

        count = ''
        num = 0
        while os.path.exists(filename + count + 'csv'):
            if num == 0 :
                filename += '_'
            num += 1
            count = str(num)

        if num == 0:
            filename = filename + '.csv'
        else:
            filename = filename + count + '.csv'

        return filename

    def write_out(self):
        content_log_filename = self.generate_unique_filename('{}_LOG'.format(self.program_name))
        # error_log_filename = ''
        print(self.target_path + content_log_filename)
