import pdfplumber
import re

def investigate_bb_pdf(filepath):
    print(f"Investigating BB parsing line-by-line: {filepath}")
    extracted = []
    
    # Regex para pegar a data inicial: DD/MM/YYYY
    # Ex: 01/02/2024 BB GIRO PRONAMPE 15.125,99 (-)
    # O valor fica no final, seguido opcionalmente de (+) ou (-)
    
    pattern = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d\.,]+)\s*(\([\-\+]\))?$')

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
                
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                match = pattern.match(line)
                if match:
                    data = match.group(1)
                    desc = match.group(2).strip()
                    val_str = match.group(3)
                    sinal = match.group(4) # pode ser '(-)' ou '(+)' ou None
                    
                    # Vamos verificar se extraímos tudo certinho
                    # Convertendo valor para checar se formataria certo
                    if sinal == '(-)':
                        val_str = '-' + val_str
                        
                    extracted.append((data, desc, val_str))
                else:
                    # Apenas imprime o que não casou com a regex para ver se perdemos algo
                    if "2024" in line or "Dia" in line:
                        print(f"IGNORED: {line}")
                        
    print("\nTotal extraído:", len(extracted))
    for ext in extracted[:10]:
        print(ext)
    print("...")
    for ext in extracted[-5:]:
        print(ext)

if __name__ == "__main__":
    import os
    pdf_path = "/home/pyter/Projects/bankEXtractor/tests/pdfs/bb.pdf"
    if os.path.exists(pdf_path):
        investigate_bb_pdf(pdf_path)
