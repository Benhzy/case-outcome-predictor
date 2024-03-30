import pandas as pd
from pypdf import PdfReader
import re
import os


def read_pdf_text(pdf_path, skip_toc=True):
    reader = PdfReader(pdf_path)
    text_by_page = [page.extract_text() + '\n' for page in reader.pages]

    # Identify pages to skip based on TABLE OF CONTENTS
    skip_pages = set()
    if skip_toc:
        for i, page_text in enumerate(text_by_page):
            if "TABLE OF CONTENTS" in page_text.upper():
                # Skip this page and the next one
                skip_pages.update({i, i+1})

    # Combine texts of pages not skipped
    text = ''.join([text for i, text in enumerate(text_by_page) if i not in skip_pages])
    return text

def extract_facts(pdf_path):
    text = read_pdf_text(pdf_path)

    # Define start pattern for facts section
    start_pattern = re.compile(r"(The facts|The Background|Factual Background|Background Facts|Background to the dispute|The underlying facts|Pertinent background facts|Background|facts)", re.IGNORECASE)
    
    # Define a generic end pattern assuming the start of a new section
    end_pattern = re.compile(r"(the issues|the issues on appeal|the appeal|appeal|the claim|the present claim|background to the dispute|the substantive issue|issues to be determined|the relevant issues)", re.IGNORECASE)

    # Search for the start of the facts section
    start_match = start_pattern.search(text)
    if not start_match:
        return ""

    # Extract starting point
    facts_start = start_match.start()
    
    # Attempt to find the end of the facts section
    end_match = end_pattern.search(text, facts_start)
    
    if end_match:
        facts_end = end_match.start()
    else:
        facts_end = len(text)  # Assume facts go till document's end if no explicit end pattern found

    # Extract and return the facts text
    facts_text = text[facts_start:facts_end].strip()
    
    return facts_text


def process_folder(folder_path):
    data = []  
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print('\nProcessing:', filename)
            facts = extract_facts(pdf_path)
            print(facts)

            data.append({'casename': filename, 'facts': facts})
    
    df = pd.DataFrame(data)
    return df

folder_path = 'data/raw'
# folder_path = 'test'
df = process_folder(folder_path)
 
csv_file_path = 'facts.csv'
df.to_csv(csv_file_path, index=False)