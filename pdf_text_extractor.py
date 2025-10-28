import os
import re
import requests
import fitz
from bs4 import BeautifulSoup
import psycopg2


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="ecourts",
        user="postgres",
        password="Dhruv@2004",
        port=5432
    )


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pdf_texts (
            id SERIAL PRIMARY KEY,
            pdf_url TEXT,
            file_name TEXT,
            text_extracted TEXT
        );
    """)
    conn.commit()
    conn.close()
    print("PostgreSQL text extraction table ready.")


def extract_pdf_link_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    link = soup.find("a", href=re.compile(r"cases/display_pdf\.php"))

    if link:
        href = link["href"]
        full_url = f"https://hcservices.ecourts.gov.in/hcservices/{href}"
        print(f"Extracted PDF URL: {full_url}")
        return full_url
    else:
        print("No PDF link found in HTML.")
        return None


def download_pdf(pdf_url, case_no="200100037062020", cino="HCBM010302722020", save_dir="pdfs"):
    os.makedirs(save_dir, exist_ok=True)
    file_name = pdf_url.split("filename=")[-1].split("&")[0][:50] + ".pdf"
    file_path = os.path.join(save_dir, file_name)

    try:
        session = requests.Session()
        session.get("https://hcservices.ecourts.gov.in/hcservices/", timeout=10)

        case_url = "https://hcservices.ecourts.gov.in/hcservices/cases_qry/o_civil_case_history.php"
        data = {
            "court_code": "1",
            "state_code": "1",
            "court_complex_code": "1",
            "case_no": case_no,
            "cino": cino,
            "appFlag": ""
        }

        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://hcservices.ecourts.gov.in",
            "referer": "https://hcservices.ecourts.gov.in/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/141.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }

        resp_case = session.post(case_url, headers=headers, data=data, timeout=15)
        if resp_case.status_code != 200:
            raise Exception(f"Case details load failed ({resp_case.status_code})")

        resp_pdf = session.get(pdf_url, headers=headers, timeout=20)
        content_type = resp_pdf.headers.get("Content-Type", "")

        if not content_type.startswith("application/pdf"):
            with open("debug_not_pdf.html", "wb") as f:
                f.write(resp_pdf.content)
            raise Exception("Response is not a PDF file (see debug_not_pdf.html)")

        with open(file_path, "wb") as f:
            f.write(resp_pdf.content)

        print(f"PDF downloaded successfully: {file_name}")
        return file_path

    except Exception as e:
        print(f"Failed to download PDF: {e}")
        return None


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        print(f"Text extracted from {os.path.basename(pdf_path)}")
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()


def save_text_to_db(pdf_url, file_name, text):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pdf_texts (pdf_url, file_name, text_extracted)
        VALUES (%s, %s, %s)
    """, (pdf_url, file_name, text))
    conn.commit()
    conn.close()


def main():
    print("Starting PDF text extraction process...")
    init_db()

    html_path = "sample_case.html"
    pdf_url = extract_pdf_link_from_html(html_path)
    if not pdf_url:
        return

    pdf_path = download_pdf(pdf_url)
    if not pdf_path:
        return

    text = extract_text_from_pdf(pdf_path)
    save_text_to_db(pdf_url, os.path.basename(pdf_path), text)

    os.makedirs("extracted_texts", exist_ok=True)
    with open(f"extracted_texts/{os.path.basename(pdf_path)}.txt", "w", encoding="utf-8") as f:
        f.write(text)

    print("All PDF texts saved to PostgreSQL and /extracted_texts folder.")


if __name__ == "__main__":
    main()
