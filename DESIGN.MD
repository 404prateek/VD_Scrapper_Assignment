Project Design Document – VD_Scrapper

1. Objective
The VD_Scrapper project automates the process of extracting, validating, and analyzing legal case data from the Indian eCourts portal.
It provides a complete ETL-style workflow — from scraping data to summarizing and storing results in PostgreSQL — ensuring accurate, structured, and automated case data management.

2. System Architecture
A. Input Layer

The scraper begins with simulated search queries for multiple states, benches, years, and keywords.

Inputs are generated dynamically and used to simulate real eCourts search forms.

B. Processing Layer

Scraping & Data Collection (scraper_automated.py):

Fetches search results and generates structured case details.

Saves results into PostgreSQL (ecourts_cases table) and CSV (final_case.csv).

HTML Parsing (ecourts_scraper.py):

Parses the saved HTML response (sample_case.html).

Extracts metadata such as filing dates, CNR numbers, judge names, petitioners, respondents, and PDF URLs.

Output stored in final_case_output.json.

PDF Validation (pdf_validator.py):

Downloads PDF files using extracted links.

Verifies MIME type, size, and SHA256 hash.

Saves validated results to PostgreSQL (pdf_validation_results) and JSON (validated_pdfs.json).

Text Extraction (pdf_text_extractor.py):

Extracts readable text from downloaded PDFs using PyMuPDF.

Stores text both in PostgreSQL (pdf_texts table) and local folder /extracted_texts.

Post-Processing (pdf_postprocess.py):

Uses NLP (TextRank and NLTK) for summarization and keyword extraction.

Stores results in PostgreSQL (pdf_summary_results) and as pdf_summary_results.json.

3. Folder Structure
VD_Scrapper/
│
├── data/
│   ├── captchas/
│   ├── progress.json
│   ├── state_bench_map.json
│
├── extracted_texts/
│   ├── <extracted .txt files>
│
├── outputs/
│   ├── pdfs/
│   ├── final_cases.csv
│
├── pdfs/
│   ├── <downloaded PDF files>
│
├── .venv/                      # Virtual environment
├── ecourts_scraper.py          # HTML parser
├── scraper_automated.py        # Main scraper logic
├── pdf_validator.py            # PDF validation & hashing
├── pdf_text_extractor.py       # PDF to text pipeline
├── pdf_postprocess.py          # Summarization & keywords
├── final_case.csv              # Raw case records
├── final_case_output.json      # Parsed case details
├── validated_pdfs.json         # PDF validation report
├── pdf_summary_results.json    # NLP summaries & keywords
├── DESIGN.MD                   # This document
├── README.MD                   # Project overview
├── requirements.txt            # Dependencies list
└── execution_log.log           # Process tracking


### 4. Database Schema

#### Table 1: `ecourts_cases`

| Column Name       | Type         | Description               |
|-------------------|--------------|----------------------------|
| id                | SERIAL       | Primary key                |
| state             | VARCHAR(100) | Court state                |
| bench             | VARCHAR(150) | Court bench                |
| keyword           | VARCHAR(100) | Search keyword             |
| year              | VARCHAR(10)  | Case year                  |
| search_type       | VARCHAR(20)  | Search mode                |
| case_number       | TEXT         | Unique case number         |
| status            | TEXT         | Current status             |
| filing_date       | TEXT         | Case filing date           |
| last_hearing_date | TEXT         | Last hearing date          |
| judge_names       | TEXT         | Assigned judges            |
| petitioner        | TEXT         | Petitioner name            |
| respondent        | TEXT         | Respondent name            |
| pdf_link          | TEXT         | PDF order URL              |
| meta              | JSONB        | Metadata                   |

---

#### Table 2: `pdf_validation_results`

| Column Name   | Type     | Description          |
|----------------|----------|----------------------|
| pdf_url       | TEXT     | Link to PDF          |
| file_name     | TEXT     | Saved file name      |
| mime_type     | TEXT     | File type            |
| file_size_kb  | FLOAT    | File size in KB      |
| sha256_hash   | TEXT     | Integrity hash       |
| is_valid      | BOOLEAN  | Validation result    |

---

#### Table 3: `pdf_texts`

| Column Name | Type | Description |
|--------------|------|-------------|
| pdf_name     | TEXT | PDF file name |
| raw_text     | TEXT | Extracted plain text |

---

#### Table 4: `pdf_summary_results`

| Column Name | Type | Description |
|--------------|------|-------------|
| file_name    | TEXT | File name of PDF |
| word_count   | INT  | Word count of extracted text |
| summary      | TEXT | Generated summary |
| keywords     | TEXT | Extracted keywords |


5. Workflow Summary

Scraper (Part A) → Fetches simulated results → Saves to DB & CSV.

HTML Parser (Part B) → Extracts structured case data → Saves as JSON.

PDF Validator (Part C) → Downloads and verifies all linked PDFs.

PDF Text Extractor (Part D) → Extracts and stores case texts.

Post-Processor (Part E) → Summarizes and indexes text data.

6. Technologies Used
Category	Tools
Language	Python 3.11
Database	PostgreSQL
Libraries	requests, psycopg2, pandas, PyMuPDF, nltk, sumy, beautifulsoup4
Environment	venv
Output Formats	CSV, JSON, PostgreSQL Tables

7. Sample Outputs

final_case.csv → Tabular raw search results.

final_case_output.json → Parsed case details.

validated_pdfs.json → Validation summary.

/pdfs/ → Downloaded case orders.

/extracted_texts/ → Cleaned text versions.

pdf_summary_results.json → Summaries & keywords.