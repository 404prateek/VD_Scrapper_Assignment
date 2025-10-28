import os
import json
import hashlib
import requests
import psycopg2


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="ecourts",
        user="postgres",
        password="Dhruv@2004",
        port=5432
    )


def init_pdf_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS pdf_validation_results;")
    conn.commit()
    cur.execute("""
        CREATE TABLE pdf_validation_results (
            id SERIAL PRIMARY KEY,
            pdf_url TEXT,
            file_name TEXT,
            mime_type TEXT,
            file_size_kb FLOAT,
            sha256_hash TEXT,
            is_valid BOOLEAN,
            error_message TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("PDF validation table ready.")


def validate_single_pdf(pdf_url):
    os.makedirs("pdfs", exist_ok=True)
    result = {"pdf_url": pdf_url}

    try:
        response = requests.get(pdf_url, timeout=20)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")

        file_name = pdf_url.split("filename=")[-1][:40] + ".pdf"
        file_path = os.path.join("pdfs", file_name)
        with open(file_path, "wb") as f:
            f.write(response.content)

        mime_type = response.headers.get("Content-Type", "unknown")
        file_size_kb = os.path.getsize(file_path) / 1024
        sha256_hash = hashlib.sha256(response.content).hexdigest()
        is_valid = mime_type == "application/pdf" and file_size_kb > 1

        result.update({
            "file_name": file_name,
            "mime_type": mime_type,
            "file_size_kb": round(file_size_kb, 2),
            "sha256_hash": sha256_hash,
            "is_valid": is_valid,
            "error_message": None
        })
        print(f"{file_name} validated successfully ({round(file_size_kb, 1)} KB)")

    except Exception as e:
        result.update({
            "file_name": None,
            "mime_type": None,
            "file_size_kb": None,
            "sha256_hash": None,
            "is_valid": False,
            "error_message": str(e)
        })
        print(f"Failed to validate {pdf_url}: {e}")

    return result


def validate_pdfs_from_json(json_path="final_case_output.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        pdf_urls = []
        for entry in data:
            if "PDF_URLS" in entry:
                pdf_urls.extend(entry["PDF_URLS"])
    else:
        pdf_urls = data.get("PDF_URLS", [])

    print(f"Found {len(pdf_urls)} PDF link(s) to validate.")

    results = []
    for url in pdf_urls:
        result = validate_single_pdf(url)
        results.append(result)

    with open("validated_pdfs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print("Results saved to validated_pdfs.json")

    conn = get_db_connection()
    cur = conn.cursor()
    for r in results:
        cur.execute("""
            INSERT INTO pdf_validation_results
            (pdf_url, file_name, mime_type, file_size_kb, sha256_hash, is_valid, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            r["pdf_url"],
            r["file_name"],
            r["mime_type"],
            r["file_size_kb"],
            r["sha256_hash"],
            r["is_valid"],
            r["error_message"]
        ))
    conn.commit()
    cur.close()
    conn.close()
    print("All validation results saved to PostgreSQL.")


if __name__ == "__main__":
    print("Starting PDF validation process...")
    init_pdf_table()
    validate_pdfs_from_json()
