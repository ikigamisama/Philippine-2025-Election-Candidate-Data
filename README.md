# Philippine 2025 Election Candidate Data

This project focuses on collecting, cleaning, and modeling candidate information for the 2025 Philippine National Elections. It automates the data pipeline from raw ballot formats to a clean, structured dataset for analysis and further use.

---

## 📌 Project Scope

### 1. Web Scraping & Downloading (`scrape_ballot.py`)

- Automatically scrape and download all official ballot files from designated sources.
- Organize files into district-based folders and file paths.

### 2. PDF to HTML Conversion

- Convert all ballot PDFs into HTML format.
- Use the HTML structure for easier text extraction via BeautifulSoup.

### 3. Data Extraction & Preprocessing (`ingestion.py`)

- Parse HTML files to extract structured candidate data.
- Normalize data fields (e.g., name, party, position, district).
- Clean and validate extracted text using regex and transformation logic.

### 4. Data Organization & Storage (`merge.py`)

- Save cleaned candidate data into CSV files per district.
- Merge all district files into a unified master dataset.

---

## 🧰 Tools & Technologies

- **Python** – Core scripting language
- **BeautifulSoup** – HTML parsing and web scraping
- **spire** – PDF to HTML conversion
- **pandas** – Data manipulation and CSV handling
- **re (Regex)** – Text cleaning and transformation
- **glob / os** – File management and directory automation

---

## 📂 Folder Structure (Sample)

/project-root
│
├── /html
│ ├── BFT_NCR/
│ └── BFT_CAR/ABRA/
│
├── /csv
│ ├── BFT_NCR/
│ └── BFT_CAR/ABRA/
│
├── scrape_ballot.py
├── ingestion.py
├── sample.csv
├── output.ipynb
└── README.md

---

## ✅ Output

- Cleaned district-level CSVs containing structured candidate data.
- Compiled CSV for all national candidates in the 2025 election.

---

## 🔄 Future Enhancements

- Validate data against official sources (e.g., COMELEC)
- Add logging and error tracking for better fault tolerance
- Build visualization tools or dashboards for data exploration

---

## 🗳️ Project Purpose

This project contributes to election data transparency by turning unstructured ballot files into a clean and analyzable dataset. It can support civic tech tools, journalistic reporting, and public research.

---

## 📬 Contact

Feel free to reach out for collaboration or feedback!
