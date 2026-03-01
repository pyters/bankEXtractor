import pdfplumber
import re

def investigate_inter_pdf(filepath):
    print(f"Investigating: {filepath}")
    
    date_pattern = re.compile(r'^(\d{1,2})\s+de\s+([A-Za-zç]+)\s+de\s+(\d{4})')
    tx_pattern = re.compile(r'^(.*?)\s+([\-]?R\$?\s*[\d\.,]+)\s+([\-]?R\$?\s*[\d\.,]+)$')
    
    current_date = None
    
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            
            for line in text.split('\n'):
                line = line.strip()
                if not line: continue
                
                d_match = date_pattern.match(line)
                if d_match:
                    current_date = f"{d_match.group(1)} {d_match.group(2)} {d_match.group(3)}"
                    print(f"NEW DATE: {current_date}")
                    continue
                
                t_match = tx_pattern.match(line)
                if t_match:
                    desc = t_match.group(1)
                    val = t_match.group(2)
                    saldo = t_match.group(3)
                    print(f"[{current_date}] {desc} | {val} | {saldo}")
                elif "R$" in line and "Saldo do dia" not in line and "Saldo bloqueado" not in line:
                    print(f"??? MISSING LINE: {line}")

if __name__ == "__main__":
    investigate_inter_pdf("/home/pyter/Projects/bankEXtractor/tests/pdfs/INTER.pdf")
