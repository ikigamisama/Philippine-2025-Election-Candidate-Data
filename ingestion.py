import os
import re
import glob
import numpy as np
import pandas as pd

from spire.pdf.common import *
from spire.pdf import *
from bs4 import BeautifulSoup


def get_file_path_list(path, file_type):
    return [
        os.path.join(dp, f)
        for dp, dn, filenames in os.walk(path)
        for f in filenames if f.endswith(file_type)
    ]


already_file = ["LAV.pdf", "OV.pdf", "LAV.csv", "OV.csv"]


# Step 1. PDF to HTML Convert


# doc = PdfDocument()

# pdf_file_list = get_file_path_list('./pdf', '.pdf')
# for pdf in pdf_file_list:
#     html_path = "./html/" + pdf.replace('./pdf\\', '').split('\\')[0]
#     save_path = "./html/" + pdf.replace('./pdf\\', '').replace('.pdf', '.html')

#     if pdf.replace('./pdf\\', '') not in already_file:
#         os.makedirs(html_path, exist_ok=True)

#     print(f"Converting PDF TO HTML: {save_path}")
#     doc.LoadFromFile(pdf)
#     convertOptions = doc.ConvertOptions
#     convertOptions.SetPdfToHtmlOptions(True, True, 1, True)
#     doc.SaveToFile(save_path, FileFormat.HTML)
#     doc.Dispose()


# Step 2. HTML file to Web Scrape and Data Ingestion

html_file_list = get_file_path_list('./html', '.html')

folder_path = list(dict.fromkeys(
    os.makedirs(os.path.dirname(html).replace(
        './html', './csv'), exist_ok=True)
    for html in html_file_list
    if html.replace('.html', '.csv').split('\\')[-1] not in already_file
))

# Step 3. Data Preprocessing

for html in html_file_list:
    content = None
    with open(html, "r", encoding="utf-8") as file:
        content = file.read()

    s = BeautifulSoup(content, 'html.parser')
    texts = [t.get_text(strip=True) for t in s.find_all("text")]

    sections = {}
    current_section = None
    buffer = []

    header_pattern = re.compile(
        r'^(SENATOR|PARTY LIST|MEMBER,|PROVINCIAL|MAYOR|VICE-MAYOR)', re.IGNORECASE)
    vote_limit_pattern = re.compile(r'VOTE FOR \d+|VOTE$', re.IGNORECASE)

    for line in texts:
        line_clean = line.strip().replace('\xa0', ' ')

        if header_pattern.match(line_clean) and vote_limit_pattern.search(line_clean):
            if current_section and buffer:
                sections[current_section] = buffer
                buffer = []

            current_section = line_clean

        elif current_section and len(buffer) == 0 and 'BUMOTO NG' in line_clean.upper():
            current_section += '\n' + line_clean

        elif current_section:
            buffer.append(line.strip())

    if current_section and buffer:
        sections[current_section] = buffer

    do_not_include = [
        "CGEG@COM CGEG@COM CGEG@COM CGEG@COM CGEG@C0M",
        "FOR PARTY LIST CANDIDATES, CHECK THE BACK OF THIS BALLOT",
        "Para sa mga kandidato ng Party List, tingnan ang likod ng balotang ito",
        "Page 1 of 2", "Evaluation Warning : The document was created with Spire.PDF for Python.",
        "MAY", "12,", "2025", "NATIONAL,", "LOCAL", "AND", "BARMM", "PARLIAMENTARY", "ELECTIONS",
        "PARAAN", "NG", "PAGBOTO", "Clustered", "Precinct", "ID:",
        "1.", "Markahan", "ang", "loob", "ng", "bilog", "sa", "tabi", "ng", "nais", "ibotong", "kandidato.",
        "2.", "Gamitin", "lamang", "ang", "marking", "pen", "na", "ibinigay", "para", "sa", "pagmarka", "ng", "mga", "bilog.",
        "3.", "Huwag", "markahan", "ng", "hihigit", "sa", "dapat.", "Precincts", "in", "Cluster:",
        "0002A", "0083A", "89010002", "90150001",
        "Evaluation Warning : The document was created with Spire.PDF for Python."
    ]

    # Step 4. Implement Data Payload
    positions_nationwide = []
    candidates_nationwide = []
    district_nationwide = []
    political_party_nationwide = []

    positions_local = []
    candidates_local = []
    district_local = []
    political_party_local = []

    for header, candidate in sections.items():
        position = None
        if "/" in header:
            if header.split('/')[0].split(', ')[0] == "MEMBER":
                position = f"{header.split('/')[0].split(', ')[1]}"
            else:
                position = f"{header.split('/')[0].split(', ')[0]}"

        cleaned_candidates = []
        buffer_candidates = ""

        for c in candidate:
            if c in do_not_include:
                continue

            if c.strip().split()[0].rstrip('.').isdigit():
                if buffer_candidates:
                    cleaned_candidates.append(buffer_candidates.strip())
                buffer_candidates = c
            else:
                buffer_candidates += " " + c

        if buffer_candidates:
            cleaned_candidates.append(buffer_candidates.strip())

        for c in cleaned_candidates:
            cleaned = re.sub(r'\s+', ' ', re.sub(r'\)\s.*', ')',
                             re.sub(r'^\d+\.?\s*', '', c))).strip()

            if html.replace('./html\\', '').replace('.html', '') in ['LAV', 'OV'] and position.strip() in ['SENATOR', 'PARTY LIST']:
                positions_nationwide.append(position.strip())

                if position.strip() == "PARTY LIST":
                    candidates_nationwide.append(cleaned)
                    political_party_nationwide.append(np.nan)
                else:
                    candidates_nationwide.append(cleaned.split('(')[0].strip())
                    political_party_nationwide.append(
                        cleaned.split('(')[1].replace(")", "").strip())

                district_nationwide.append(np.nan)
            elif html.replace('./html\\', '').replace('.html', '') not in ['LAV', 'OV'] and position.strip() not in ['SENATOR', 'PARTY LIST']:
                if cleaned and cleaned[0] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    positions_local.append(position.strip())
                    if '(' in cleaned and ')' in cleaned:
                        candidates_local.append(cleaned.split('(')[0].strip())
                        political_party_local.append(
                            cleaned.split('(')[1].replace(")", "").strip())
                    else:
                        candidates_local.append(cleaned.strip())
                        political_party_local.append('IND')
                    district_local.append(html.replace(
                        './html\\', '').replace('.html', ''))

    # Step 4. Save as CSV file
    if html.replace('./html\\', '').replace('.html', '') in ['LAV', 'OV']:
        df = pd.DataFrame({
            'position': positions_nationwide,
            'candidate': candidates_nationwide,
            'party': political_party_nationwide,
            'district': district_nationwide
        })
        df.to_csv(html.replace(
            './html', './csv').replace('.html', '.csv'), index=False)
    else:
        df = pd.DataFrame({
            'position': positions_local,
            'candidate': candidates_local,
            'party': political_party_local,
            'district': district_local
        })
        df.to_csv(html.replace(
            './html', './csv').replace('.html', '.csv'), index=False)

    print(
        f"Saved csv file {html.replace('./html', './csv').replace('.html', '.csv')}")
