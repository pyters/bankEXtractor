import pdfplumber
import re

def investigate_acredicoop_pdf(filepath):
    print(f"Investigating: {filepath}")
    
    # 10/01/2024
    date_pattern = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+')
    
    with pdfplumber.open(filepath) as pdf:
        text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        lines = text.split('\n')
        
        parsed_items = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            d_match = date_pattern.match(line)
            if d_match:
                row_date = d_match.group(1)
                remainder = line[d_match.end():].strip()
                
                # Acredicoop structure:
                # [Date] [Desc] [Doc] [Value] [Balance]
                # Example:
                # 10/01/2024 DB. COTAS 86.089 -90,00 336,36
                # 12/01/2024 CREDITO PIX - AR CERTIFICA SOLUCOES 355902.931 90,00 376,36
                # Vamos splitar de trás pra frente
                parts = remainder.rsplit(' ', 2)
                if len(parts) == 3:
                    saldo_str = parts[2]
                    value_str = parts[1]
                    
                    desc_and_doc = parts[0]
                    # Doc is usually numbers and dots at the end of desc
                    desc_parts = desc_and_doc.rsplit(' ', 1)
                    if len(desc_parts) == 2 and re.match(r'^[\d\.]+$', desc_parts[1]):
                        desc = desc_parts[0]
                    else:
                        desc = desc_and_doc # Fallback: could not split Doc
                        
                    parsed_items.append((row_date, desc, value_str))
            
            i += 1
            
        print("--- PARSED ITEMS ---")
        for it in parsed_items[:20]:
             print(f"[{it[0]}] {it[1]} -> {it[2]}")

if __name__ == "__main__":
    investigate_acredicoop_pdf("/home/pyter/Projects/bankEXtractor/tests/pdfs/ACREDICOOP.pdf")
