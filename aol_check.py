import pypdf
import os
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
 'confidence']

def find_aol(text):
    found_areas = []
    for area in AREA_OF_LAW:
        if area in text.lower():
            found_areas.append(area)
    return found_areas

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