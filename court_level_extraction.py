import os
import pandas as pd

PATH = r"raw-cases"

def extract_court_level(path=PATH) -> list:
    """ Extract the court level for each legal case found in the given folder path """

    court_levels = []
    for file in os.listdir(path):
        year, court_level, case = file.split("_")
        court_levels.append(court_level)
    return court_levels

data = pd.DataFrame(extract_court_level(PATH), columns=["court_level"])

data.to_csv("sg_legal_cases_dataset.csv", index=False)