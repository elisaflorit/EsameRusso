class ExamException(Exception):
    pass

class CSVTimeSeriesFile:
    
    def __init__(self, name):
    
        # Setto il nome del file
        self.name = name
        print(self.name)
    
    
    def get_data(self):

        try:
            my_file = open (self.name, 'r')
            my_file.readline()
        except Exception as e:
            raise ExamException(f"Errore in apertura del file: {e}")
        
        return 1

if __name__ == '__main__':
    time_series_file = CSVTimeSeriesFile(name='data.csv')
    time_series = time_series_file.get_data()
    print(time_series)