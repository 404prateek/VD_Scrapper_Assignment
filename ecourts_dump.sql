DROP TABLE IF EXISTS ecourts_cases CASCADE;
DROP TABLE IF EXISTS pdf_texts CASCADE;
DROP TABLE IF EXISTS pdf_validation_results CASCADE;
DROP TABLE IF EXISTS pdf_summary_results CASCADE;


CREATE TABLE ecourts_cases (
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

INSERT INTO ecourts_cases (state, bench, keyword, year, search_type, case_number, status, filing_date, last_hearing_date, judge_names, petitioner, respondent, pdf_link, meta)
VALUES
('Bombay High Court', 'Principal Bench, Mumbai', 'kumar', '2021', 'party', 'WP/1201/2021', 'Pending', '01-01-2021', '15-07-2021', 'Justice A, Justice B', 'Kumar Petitioner', 'State Respondent', NULL, '{"timestamp": "2025-10-28T10:00:00"}'),
('Bombay High Court', 'Principal Bench, Mumbai', 'patel', '2022', 'case_no', 'WP/2202/2022', 'Disposed', '12-02-2022', '20-08-2022', 'Justice C, Justice D', 'Patel Petitioner', 'Union of India', NULL, '{"timestamp": "2025-10-28T10:00:00"}'),
('Allahabad High Court', 'Principal Bench, Allahabad', 'kumar', '2023', 'party', 'WP/3706/2023', 'Pending', '15-03-2023', '05-09-2023', 'Justice E, Justice F', 'Kumar Petitioner', 'State Respondent', NULL, '{"timestamp": "2025-10-28T10:00:00"}'),
('Allahabad High Court', 'Principal Bench, Allahabad', 'patel', '2024', 'case_no', 'WP/4801/2024', 'Disposed', '05-04-2024', '10-10-2024', 'Justice G, Justice H', 'Patel Petitioner', 'State Respondent', NULL, '{"timestamp": "2025-10-28T10:00:00"}');


CREATE TABLE pdf_texts (
    id SERIAL PRIMARY KEY,
    pdf_url TEXT,
    file_name TEXT,
    text_extracted TEXT
);

INSERT INTO pdf_texts (pdf_url, file_name, text_extracted)
VALUES
('https://hcservices.ecourts.gov.in/hcservices/display_pdf.php?filename=abc123.pdf', 'abc123.pdf', 'Order regarding interim relief granted...'),
('https://hcservices.ecourts.gov.in/hcservices/display_pdf.php?filename=xyz456.pdf', 'xyz456.pdf', 'Final judgment and order passed by Justice A...');


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

INSERT INTO pdf_validation_results (pdf_url, file_name, mime_type, file_size_kb, sha256_hash, is_valid, error_message)
VALUES
('https://hcservices.ecourts.gov.in/hcservices/display_pdf.php?filename=abc123.pdf', 'abc123.pdf', 'application/pdf', 234.5, 'a3f5b8e72c0f...', TRUE, NULL),
('https://hcservices.ecourts.gov.in/hcservices/display_pdf.php?filename=xyz456.pdf', 'xyz456.pdf', 'application/pdf', 198.7, 'b6c1e2a44d9f...', TRUE, NULL);


CREATE TABLE pdf_summary_results (
    id SERIAL PRIMARY KEY,
    file_name TEXT,
    word_count INT,
    summary TEXT,
    keywords TEXT
);

INSERT INTO pdf_summary_results (file_name, word_count, summary, keywords)
VALUES
('abc123.pdf', 250, 'Court grants interim relief pending final decision.', 'relief, court, interim, pending, decision'),
('xyz456.pdf', 300, 'Judgment passed with reference to constitutional law and procedure.', 'judgment, law, constitutional, procedure, passed');


