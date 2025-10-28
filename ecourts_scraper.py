from bs4 import BeautifulSoup
import re
import json

def parse_case_detail_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    case_table = soup.find('table', class_='case_details_table')
    if case_table:
        rows = case_table.find_all('tr')
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all('td')]
            if len(cells) >= 4:
                if "Filing Number" in cells[0]:
                    data["Filing Number"] = cells[1]
                    data["Filing Date"] = cells[3]
                elif "Registration Number" in cells[0]:
                    data["Registration Number"] = cells[1]
                    data["Registration Date"] = cells[3]
        cnr = case_table.find('strong', style=re.compile('color'))
        if cnr:
            data["CNR Number"] = cnr.text.strip()

    status_table = soup.find('table', class_='table_r')
    if status_table:
        for tr in status_table.find_all('tr'):
            tds = [td.get_text(strip=True) for td in tr.find_all('td')]
            if len(tds) == 2:
                key = tds[0].replace(':', '').strip()
                value = tds[1]
                data[key] = value

    pet_adv = soup.find('span', class_='Petitioner_Advocate_table')
    resp_adv = soup.find('span', class_='Respondent_Advocate_table')
    data["Petitioners"] = pet_adv.get_text(" ", strip=True) if pet_adv else ""
    data["Respondents"] = resp_adv.get_text(" ", strip=True) if resp_adv else ""

    acts = []
    act_table = soup.find('table', id='act_table')
    if act_table:
        for tr in act_table.find_all('tr')[1:]:
            tds = [td.get_text(strip=True) for td in tr.find_all('td')]
            if len(tds) >= 2:
                acts.append({"Act": tds[0], "Section": tds[1]})
    if acts:
        data["Acts"] = acts

    pdf_links = []
    for a in soup.find_all("a", href=re.compile(r"cases/display_pdf\.php")):
        link = a.get("href")
        if link and "display_pdf.php" in link:
            if not link.startswith("http"):
                link = f"https://hcservices.ecourts.gov.in/hcservices/{link.lstrip('/')}"
            pdf_links.append(link)
    data["PDF_URLS"] = pdf_links

    docs = []
    doc_table = soup.find("table", class_="transfer_table")
    if doc_table:
        for tr in doc_table.find_all("tr")[1:]:
            tds = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(tds) >= 6:
                docs.append({
                    "Sr. No.": tds[0],
                    "Doc No.": tds[1],
                    "Date of Receiving": tds[2],
                    "Filed by": tds[3],
                    "Advocate": tds[4],
                    "Document Filed": tds[5]
                })
    if docs:
        data["Documents"] = docs

    return data


if __name__ == "__main__":
    try:
        with open("sample_case.html", "r", encoding="utf-8") as f:
            html = f.read()
        result = parse_case_detail_html(html)
        print(json.dumps(result, indent=4, ensure_ascii=False))
        with open("final_case_output.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print("Saved output to final_case_output.json")
    except FileNotFoundError:
        print("File 'sample_case.html' not found.")
    except Exception as e:
        print(f"Error occurred: {e}")







