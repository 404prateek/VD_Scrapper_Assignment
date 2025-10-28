VD_Scrapper – Automated eCourts Case Data Scraper

Overview

VD_Scrapper is an end-to-end automated pipeline that extracts, validates, and processes case-related data from the Indian eCourts system.
It performs web scraping, PDF validation, text extraction, and intelligent summarization — storing all structured results in PostgreSQL.

Key Features

Automated Case Scraper: Simulates searches across states, benches, keywords, and years.

HTML Parser: Extracts full case details, petitioner/respondent info, hearing history, and PDF order links.

PDF Validator: Downloads and validates each PDF’s MIME type, size, and SHA-256 hash.

Text Extractor: Reads PDF text using PyMuPDF and stores it in PostgreSQL.

Post-Processor: Generates summaries and keywords from extracted text using NLP (sumy + nltk).

Database Logging: All results are logged and stored in PostgreSQL for easy querying.

VD_Scrapper/
│
├── data/ # Intermediate data and state tracking
│ ├── captchas/ # Saved captcha images (if any)
│ ├── progress.json # Tracks scraping progress
│ └── state_bench_map.json # Maps states to high court benches
│
├── extracted_texts/ # Extracted text files from processed PDFs
│
├── outputs/ # Output folder for results and CSVs
│ └── pdfs/ # Optional PDF copies or exports
│
├── pdfs/ # Downloaded case PDF files
│
├── ecourts_dump.sql # PostgreSQL database dump (schema + sample data)
│
├── ecourts_scraper.py # Parses case details from eCourts HTML
├── scraper_automated.py # Main scraping and DB insertion pipeline
├── pdf_text_extractor.py # Extracts text content from downloaded PDFs
├── pdf_validator.py # Validates and hashes downloaded PDFs
├── pdf_postprocess.py # Summarizes and extracts keywords from text
│
├── final_case.csv # Consolidated scraped case data
├── final_case_output.json # Parsed case HTML as structured JSON
├── validated_pdfs.json # PDF validation and metadata results
├── pdf_summary_results.json # Summarization and keyword extraction results
│
├── DESIGN.MD # Detailed system design document
├── requirements.txt # Python dependencies list
├── README.MD # Main project documentation (this file)
└── execution_log.log # Runtime logs for scraper and extraction
Note:> The repository includes the full PostgreSQL dump (`ecourts_dump.sql`)  
which can be imported locally to reproduce the database setup and results.


🧩 Modules Overview
Module	Description
scraper_automated.py	Scrapes case details (keywords, states, years) and stores results in PostgreSQL.
ecourts_scraper.py	Parses detailed HTML and extracts case metadata + PDF links.
pdf_validator.py	Validates PDFs (MIME type, hash, size) and saves results to DB.
pdf_text_extractor.py	Extracts text from PDFs and stores it in pdf_texts table.
pdf_postprocess.py	Summarizes judgments and extracts top keywords.
Setup Instructions
1️. Clone Repository
git clone https://github.com/<404prateek>/VD_Scrapper.git
cd VD_Scrapper

2️. Create and Activate Virtual Environment
python -m venv .venv
.venv\Scripts\activate   # (Windows)

3️. Install Dependencies
pip install -r requirements.txt

4️. Setup PostgreSQL

Create a new database named ecourts:

CREATE DATABASE ecourts;


Then update credentials in each Python file under get_db_connection().

How to Run
Step 1 – Initialize and Scrape Cases
python scraper_automated.py

Step 2 – Parse Case HTML
python ecourts_scraper.py

Step 3 – Validate PDFs
python pdf_validator.py

Step 4 – Extract Text
python pdf_text_extractor.py

Step 5 – Summarize and Extract Keywords
python pdf_postprocess.py

Database Tables
Table	Purpose
ecourts_cases	Stores raw case info from scraping
pdf_validation_results	Stores validation metadata of PDFs
pdf_texts	Stores extracted text from PDFs
pdf_summary_results	Stores generated summaries and keywords
Sample Outputs

final_case.csv / final_case_output.json – Case data and parsed HTML.

validated_pdfs.json – PDF validation status.

pdf_summary_results.json – Summarization and keywords.

PostgreSQL Tables – All structured records available locally.

Notes

Ensure PostgreSQL is running locally or inside Docker (no cloud DBs).

Include a sample database dump (.sql) and 20–50 output cases for submission.

For debugging, refer to execution_log.log and debug_case.html.

Author
Prateek Kumar
