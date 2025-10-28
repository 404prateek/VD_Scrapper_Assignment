import os
import json
import psycopg2
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="ecourts",
        user="postgres",
        password="Dhruv@2004",
        port=5432
    )


def init_summary_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS pdf_summary_results;")
    conn.commit()
    cur.execute("""
        CREATE TABLE pdf_summary_results (
            id SERIAL PRIMARY KEY,
            file_name TEXT,
            word_count INT,
            summary TEXT,
            keywords TEXT
        );
    """)
    conn.commit()
    conn.close()
    print("PostgreSQL summary table ready.")


def summarize_text(text, sentence_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    summary_sentences = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary_sentences)


def extract_keywords(text, num_keywords=8):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text.lower())
    words = [w for w in words if w.isalpha() and w not in stop_words]
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return ", ".join([w for w, _ in sorted_words[:num_keywords]])


def process_extracted_texts(folder_path="extracted_texts"):
    if not os.path.exists(folder_path):
        print("Folder not found:", folder_path)
        return

    conn = get_db_connection()
    cur = conn.cursor()
    summary_data = []

    print("Starting PDF post-processing...")

    for file in os.listdir(folder_path):
        if not file.endswith(".txt"):
            continue

        file_path = os.path.join(folder_path, file)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if len(text) < 50:
            print(f"Skipping {file} (too short or empty)")
            continue

        word_count = len(text.split())
        summary = summarize_text(text)
        keywords = extract_keywords(text)

        cur.execute("""
            INSERT INTO pdf_summary_results (file_name, word_count, summary, keywords)
            VALUES (%s, %s, %s, %s)
        """, (file, word_count, summary, keywords))
        conn.commit()

        summary_data.append({
            "file_name": file,
            "word_count": word_count,
            "summary": summary,
            "keywords": keywords
        })

        print(f"Processed {file} ({word_count} words)")

    conn.close()

    with open("pdf_summary_results.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=4, ensure_ascii=False)

    print("All summaries saved to pdf_summary_results.json and PostgreSQL.")


if __name__ == "__main__":
    init_summary_table()
    process_extracted_texts("extracted_texts")
