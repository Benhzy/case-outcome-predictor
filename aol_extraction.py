import pypdf
import os
import re
import pandas as pd

AREA_OF_LAW = ['civil procedure',
 'conflict of laws',
 'admiralty and shipping',
 'criminal law',
 'criminal procedure and sentencing',
 'contempt of court',
 'arbitration',
 'insolvency law',
 'injunctions',
 'bailment',
 'carriage of goods by air and land',
 'credit and security',
 'companies',
 'courts and jurisdiction',
 'revenue law',
 'words and phrases',
 'insurance',
 'contract',
 'evidence',
 'debt and recovery',
 'res judicata',
 'trusts',
 'damages',
 'designs',
 'banking',
 'probate and administration',
 'equity',
 'administrative law',
 'employment law',
 'tort',
 'land',
 'family law',
 'choses in action',
 'building and construction law',
 'mental disorders and treatment',
 'intellectual property',
 'trade marks and trade names',
 'constitutional law',
 'immigration',
 'legal profession',
 'gifts',
 'restitution',
 'statutory interpretation',
 'agency',
 'succession and wills',
 'limitation of actions',
 'charities',
 'professions',
 'road traffic',
 'bills of exchange and other negotiable instruments',
 'commercial transactions',
 'confidence',
 'Partnership',
 'Unincorporated Associations and Trade Unions']
# "trade marks and trade names", is supposed to be under IP, but in pre-2017 cases they are not 


def find_aol(text):
    patterns = [
        r"(\[\n?|\n)(\b(?:{}))\s*[—–-]\s*\[?([^—–\]]+)\]?\s*[—–-]",
        r"\[(\b(?:{}))\]\s*[—–-]\s*\[([^—–\]]+?)\]",
        r"\[(.*?)\s*—\s*(.+?)\]"
    ]

    aol_dict = {}

    for pattern in patterns:
        formatted_pattern = pattern.format("|".join(map(re.escape, AREA_OF_LAW)))
        matches = re.finditer(formatted_pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) == 3:
                main_area = match.group(2).lower()  
                sub_area = match.group(3).strip().lower()
            else:
                main_area = match.group(1).lower()  
                sub_area = match.group(2).strip().lower() 
                print(main_area)

            # if main_area not in AREA_OF_LAW:
            #     continue

            if main_area == 'trade marks and trade names':
                main_area = 'intellectual property'
                sub_area = 'trade marks and trade names'
            if '\n' in sub_area:
                    sub_area = sub_area.split("\n")[0]

            # Add the main area and sub-area to the dictionary
            if main_area in aol_dict:
                if sub_area not in aol_dict[main_area] and sub_area != '':
                    aol_dict[main_area].append(sub_area)
                    
            else:
                aol_dict[main_area] = [sub_area]

        if aol_dict != {}:
            break
        
    return aol_dict

def extract_aol(pdf_path):
    text = ''
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        num_pages = min(10, len(reader.pages)) # only take at most first 10 pages 
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    found_areas = find_aol(text)
    return found_areas

def process_folder(folder_path):
    data = []  
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print('\nProcessing:', filename)
            areas_of_law = extract_aol(pdf_path)

            data.append({'casename': filename, 'area_of_law': areas_of_law if areas_of_law else []})
    
    df = pd.DataFrame(data)
    return df
 
folder_path = 'raw-cases'
# folder_path = 'test'
df = process_folder(folder_path)
 
csv_file_path = 'areas_of_law.csv'
df.to_csv(csv_file_path, index=False)