import re
import pypdf
import spacy
import os
import pandas as pd
import difflib
import fitz

SUPREME_COURT_JUDGES = [
    'Sundaresh Menon', 'Tay Yong Kwang', 'Steven Chong', 'Belinda Ang',
    'Woo Bih Li', 'Kannan Ramesh', 'Debbie Ong', 'Andrew Phang Boon Leong', 'Kannan Ramesh',
    'See Kee Oon', 'Judith Prakash', 'Choo Han Teck', 'Aedit Abdullah',
    'Quentin Loh', 'Chua Lee Ming', 'Valerie Thean', 'Hoo Sheau Peng',
    'Pang Khang Chau', 'Audrey Lim', 'Vincent Hoong', 'Dedar Singh Gill',
    'Mavis Chionh', 'S Mohan', 'Andre Maniam', 'Philip Jeyaretnam',
    'Kwek Mean Luck', 'Hri Kumar Nair', 'Goh Yihan', 'Teh Hwee Hwee',
    'Lee Seiu Kin', 'Chan Seng Onn', 'Tan Siong Thye', 'Wong Li Kok, Alex',
    'Christopher Tan', 'Kristy Tan', 'Lai Siu Chiu', 'Ang Cheng Hock',
    'George Wei', 'Vinodh Coomaraswamy', 'Chao Hick Tin', 'Foo Chee Hock', 'Foo Tuat Yien',
    'Kan Ting Chiu', 'Edmund Leow', 'Andrew Ang', 'Tan Lee Meng', 'Tan Puay Boon'
]
# Load spaCy's English NER model
nlp = spacy.load("en_core_web_sm")

# Step 1 - Obtain the start of the legal document after skipping through the content pages to obtain the page with the coram.
def identify_disclaimer_page(pdf_path):
    """
        Post 2016 legal documents seem to have a section at the top with a disclaimer.
        This potentially could be an area that we can use to localise our search for coram(s).

        Once we are able to identify the particular disclaimer section, 
        the 'coram(s)' comes after the 'court_level' and before the 'court_dates'

        This disclaimer can sometimes be parsed incorrectly due to the legal documents being in a PDF format.
        The incorrect parsing results in certain words having more whitespaces between them and within them.
        Hence, I have manually identified key phrases and inserted a regex pattern between certain words to ignore whitespaces.
    """
    #DISCLAIMER1 = r"This judgment is subject to final editorial corrections approved by the"
    #DISCLAIMER2 = r"This judgment is subject to final editorial corrections to be approved by the"
    #DISCLAIMER3 = r'(This\s*judgment\s*is\s*subject\s*to\s*final\s*editorial\s*correct\s*ions).+'
    DISCLAIMER = r'(This\s*ju\s*dgment\s*is\s*subject\s*to\s*final\s*editori\s*al\s*correct\s*ions).+'
    text = ''
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        num_pages = reader._get_num_pages()
        for page_number in range(num_pages):
            page = reader._get_page(page_number)
            text += page.extract_text()
            
            # Search for disclaimer
            if re.search(DISCLAIMER, text):
                # Page number is relative to the Python indexing (0-indexed)
                return page_number

def get_overlap(s1, s2):
    """
        Helper function to obtain the overlapping text in 2 strings.
        This text would ideally contain the judges names
    """
    s = difflib.SequenceMatcher(None, s1, s2)
    pos_a, pos_b, size = s.find_longest_match(0, len(s1), 0, len(s2)) 
    
    return s1[pos_a:pos_a+size]

# Step 2: Extract text from PDF at the coram page
def extract_coram_portion_from_pdf(pdf_path, coram_page):
    """
        This function would help us extract to further refine our search for the corams and judges,
        which we would later pass to spaCy NER to retrieve the relevant names.

        args:
            pdf_path: Absolute path of the Case Document.
            coram_page: Page number of where the coram details are (0-indexed).
    """
    DATE_IDENTIFIER = r"\d{1,2} [A-Z][a-z]{1,10} \d{4}"

    text = ''
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        page = reader._get_page(coram_page)
        text += page.extract_text()

    if pdf_path.split('_')[1] == 'SGHC':
        COURT_NAME_IDENTIFER = r'High Court'
        # Find the index of the first occurrence of the level of court/court name using regular expression
        indexA = text.find(COURT_NAME_IDENTIFER)
        # If the phrase is not found, return None
        if indexA == -1:
            return None
        # Truncate the original text to get what is after the Court Name
        textA = text[indexA + len(COURT_NAME_IDENTIFER):]
        # Find the index of the first occurrence of the date using regular expression
        match = re.search(DATE_IDENTIFIER, text)
        # If the date is not found, return None
        if not match:
            return None

        #Get the index of the start of the match
        indexB = match.start()
        # Truncate the original text to get what is before the Court Dates.
        textB = text[:indexB]
        # Use of helper function - get_overlap()
        overlapping_text = get_overlap(textA, textB)

        return overlapping_text
    
    elif pdf_path.split('_')[1] == 'SGCA':
        COURT_NAME_IDENTIFER = r'Court of App'
        # Find the index of the first occurrence of the level of court/court name using regular expression
        indexA = text.find(COURT_NAME_IDENTIFER)
        # If the phrase is not found, return None
        if indexA == -1:
            return None
        # Truncate the original text to get what is after the Court Name
        textA = text[indexA + len(COURT_NAME_IDENTIFER):]
        # Find the index of the first occurrence of the date using regular expression
        match = re.search(DATE_IDENTIFIER, text)
        # If the date is not found, return None
        if not match:
            return None
        # Get the index of the start of the match
        indexB = match.start()
        # Truncate the original text to get what is before the Court Date
        textB = text[:indexB]
        # Use of helper function - get_overlap()
        overlapping_text = get_overlap(textA, textB)

        return overlapping_text

# Step 3a: Identify potential names with a small list of Supreme Court Judges    
def identify_names_with_list(pdf_path, coram_page):
    text = ''
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        page = reader._get_page(coram_page)
        text += page.extract_text()

    # Format text such that if between words they contain more than 1 whitespace, change to only 1 whitespace
    formatted_text = re.sub(r'\s+', ' ', text)

    # Finding judge name through fixed list
    coram_names = [name for name in SUPREME_COURT_JUDGES if name.lower() in formatted_text.lower()]
    #print(f"Names: {coram_names}")
    return coram_names

# Step 3b: Identify potential names using spaCy NER --> This is p shit to be honest thank god there weren't that many cases
def identify_names_with_spaCy(text):
    # Format text such that if between words they contain more than 1 whitespace, change to only 1 whitespace
    formatted_text = re.sub(r'\s+', ' ', text)
    
    # Finding judge through spaCy NER
    doc = nlp(formatted_text)
    potential_names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
    return potential_names


# Step 4A: Output or store recognized names
def coram_extraction_post_2016(pdf_path):
    coram_page = identify_disclaimer_page(pdf_path)

    # In post 2016 case documents, if unable to find the coram page, return "" as Coram
    if coram_page is None:
        return ""
    
    coram_names = identify_names_with_list(pdf_path, coram_page)

    # If unable to use list of judges to find the names, use spaCy NER instead
    if len(coram_names) == 0:
        text = extract_coram_portion_from_pdf(pdf_path, coram_page)
        recognized_names = identify_names_with_spaCy(text)
        print(f"NER Names: {recognized_names}")
        return recognized_names
    
    return coram_names

# Step 4B: Output or store recognised names pre-2016 format
def coram_extraction_pre_2016(pdf_path):
    coram_pattern = re.compile(r"(Coram)\s*:\s*(.+)")
    remove_title_pattern = r'\b(?:CJ|SJ|JC|JA|J)\b'  # Add more titles as needed
    case_coram_list = []
    
    doc = fitz.open(pdf_path)
    text = doc[0].get_text("text")

    # Extract Coram
    for match in coram_pattern.finditer(text):
        coram_name_without_title = re.sub(remove_title_pattern, '', match.group(2))

        #Remove extra whitespace
        coram_name_without_title = coram_name_without_title.strip().replace(';', ',')
        case_coram_list.append(coram_name_without_title)

    return case_coram_list


def batch_process_coram(folder_path):
    fname = []
    coram_list = []
    unusable_files = []
    pdf_files = [file for file in os.listdir(folder_path) if file.lower().endswith(".pdf")]

    for file in pdf_files:
        pdf_path = os.path.join(folder_path, file)

        if int(file.split('_')[0]) > 2015:
            coram_info = coram_extraction_post_2016(pdf_path)

            if coram_info == "" or coram_info == []:
                unusable_files.append(file)
            
            coram_list.append(coram_info)
            fname.append(file)

        elif int(file.split('_')[0]) < 2016:
            coram_info = coram_extraction_pre_2016(pdf_path)

            if coram_info == []:
                unusable_files.append(file)

            coram_list.append(coram_info)
            fname.append(file)

    coram_dict = {
        "File Name": fname,
        "Coram": coram_list
    }

    df = pd.DataFrame(coram_dict)
    df.to_csv('final_coram_data.csv')


    unusable_files_dict = {'fname': unusable_files}

    df2 = pd.DataFrame(unusable_files_dict)
    df2.to_csv('Unusable Files.csv')

    print(
        f"All PDF files in {folder_path} have been processed. Coram information is saved to final_coram_data.csv. Total files processed: {len(fname)}.")

# Adjust these paths as per your requirements
folder_path = 'data/raw/'

batch_process_coram(folder_path)

# Testing usage
# pdf_path = r'data/raw/2000_SGHC_16.pdf'
# pdf_path2 = r'data/raw/2016_SGHC_38.pdf'
# test = coram_extraction_pre_2016(pdf_path)
# print(test)
        
