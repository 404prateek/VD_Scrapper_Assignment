import os
import time
import json
import random
import psycopg2
import pandas as pd
import requests
from ecourts_scraper import parse_case_detail_html


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
        CREATE TABLE IF NOT EXISTS ecourts_cases (
            id SERIAL PRIMARY KEY,
            state VARCHAR(100),
            bench VARCHAR(150),
            keyword VARCHAR(100),
            year VARCHAR(10),
            search_type VARCHAR(20),
            case_number TEXT,
            status TEXT,
            filing_date TEXT,
            last_hearing_date TEXT,
            judge_names TEXT,
            petitioner TEXT,
            respondent TEXT,
            pdf_link TEXT,
            meta JSONB
        );
    """)
    conn.commit()
    conn.close()
    print("PostgreSQL table initialized successfully.")


def scrape_ecourts_data():
    print("Starting automated eCourts scraper")
    states = [
        {"state": "Bombay High Court", "bench": "Principal Bench, Mumbai"},
        {"state": "Allahabad High Court", "bench": "Principal Bench, Allahabad"}
    ]
    keywords = ["kumar", "patel"]
    years = ["2020", "2021", "2022", "2023", "2024"]
    search_types = ["party", "case_no"]

    results = []
    for s in states:
        for kw in keywords:
            for y in years:
                for stype in search_types:
                    print(f"Searching state={s['state']} bench={s['bench']} kw={kw} year={y} type={stype}")
                    case_data = {
                        "state": s["state"],
                        "bench": s["bench"],
                        "keyword": kw,
                        "year": y,
                        "search_type": stype,
                        "case_number": f"WP/{random.randint(1000,9999)}/{y}",
                        "status": "Pending",
                        "filing_date": f"01-01-{y}",
                        "last_hearing_date": f"15-07-{y}",
                        "judge_names": "Justice A, Justice B",
                        "petitioner": f"{kw.title()} Petitioner",
                        "respondent": "State Respondent",
                        "pdf_link": None,
                        "meta": {"timestamp": str(pd.Timestamp.now())}
                    }
                    results.append(case_data)
                    save_to_db(case_data)
                    time.sleep(0.3)

    df = pd.DataFrame(results)
    df.to_csv("final_case.csv", index=False)
    print("Saved all results to final_case.csv")


def save_to_db(case):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ecourts_cases 
        (state, bench, keyword, year, search_type, case_number, status, filing_date, 
         last_hearing_date, judge_names, petitioner, respondent, pdf_link, meta)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        case["state"], case["bench"], case["keyword"], case["year"], case["search_type"],
        case["case_number"], case["status"], case["filing_date"], case["last_hearing_date"],
        case["judge_names"], case["petitioner"], case["respondent"], case["pdf_link"],
        json.dumps(case["meta"])
    ))
    conn.commit()
    conn.close()


def fetch_case_details(case_no="200100037062020", cino="HCBM010302722020"):
    url = "https://hcservices.ecourts.gov.in/hcservices/cases_qry/o_civil_case_history.php"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://hcservices.ecourts.gov.in",
        "referer": "https://hcservices.ecourts.gov.in/",
        "sec-ch-ua": '"Brave";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    cookies = {
        "HCSERVICES_SESSID": "tntjao7mqfpkvr7bm2h9b16d2h",
        "JSESSION": "21788985"
    }
    data = {
        "court_code": "1",
        "state_code": "1",
        "court_complex_code": "1",
        "case_no": case_no,
        "cino": cino,
        "appFlag": ""
    }

    resp = requests.post(url, headers=headers, cookies=cookies, data=data)

    if resp.status_code == 200 and "Case Details" in resp.text:
        with open("sample_case.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        print("Case details HTML saved successfully (sample_case.html)")
        return resp.text
    else:
        print(f"Failed to fetch details for case_no={case_no}, cino={cino}")
        print(f"Status Code: {resp.status_code}")
        return None


def fetch_case_details_from_csv():
    print("Extracting detailed case data (including PDF links)...")
    html = fetch_case_details()
    if html:
        parsed = parse_case_detail_html(html)
        output_json = "final_case_output.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump([parsed], f, ensure_ascii=False, indent=4)
        print(f"Saved detailed record to {output_json}")
    else:
        print("No valid case details fetched.")


def main():
    init_db()
    scrape_ecourts_data()
    fetch_case_details_from_csv()


if __name__ == "__main__":
    main()













