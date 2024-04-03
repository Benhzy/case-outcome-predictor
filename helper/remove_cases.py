import pandas as pd
import os

def delete_cases(directory, csv_file):
    df = pd.read_csv(csv_file)
    
    for file_name in df['filename']:
        file_path = os.path.join(directory, file_name)
        
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")


path = 'raw-cases/raw-cases'
delete_cases(path, 'reassigned_cases.csv')
