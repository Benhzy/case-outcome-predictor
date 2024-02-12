import requests

def download_files():

    base_url = 'https://www.elitigation.sg/gd/gd/{year}_{court}_{case_id}/pdf'
    
    years = range(2000, 2024)
    courts = ['SGHC', 'SGCA']
    case_ids = range(1, 430)

    # Iterate over all combinations of years, courts, and case_ids
    for year in years:
        for court in courts:
            for case_id in case_ids:
                pdf_url = base_url.format(year=year, court=court, case_id=case_id)
                response = requests.get(pdf_url)

                # Check if the request was successful and the content is a PDF
                if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
                    s3_key = f'raw-cases/{year}_{court}_{case_id}.pdf'
                    file = open(s3_key, "wb")
                    file.write(response.content)
                    file.close()        
                else:
                    # Skip non-existent or non-PDF files
                    continue

download_files()