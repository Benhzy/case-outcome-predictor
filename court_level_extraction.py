import os

PATH = r"raw-cases"

def extract_court_level(path=PATH) -> set:
    """ Extract the court level for each legal case found in the given folder path """

    court_levels = set()
    for file in os.listdir(path):
        year, court_level, case = file.split("_")
        if court_level not in court_levels:
            court_levels.add(court_level)
    return court_levels
# print(extract_court_level(PATH))