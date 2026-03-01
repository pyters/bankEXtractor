import pdfplumber
import re

def investigate_bradesco_pdf(filepath):
    print(f"Investigating: {filepath}")
    with pdfplumber.open(filepath) as pdf:
        page = pdf.pages[0]
                        
        print("\n--- TESTANDO TEXTO CRU E REGEX SPLIT ---")
        text = page.extract_text(layout=True)
        lines = text.split('\n')
        for line in lines[8:40]:
            if len(line.strip()) == 0: continue
            
            # Divide a linha em colunas onde houver 2 ou mais espaços
            cols = [col.strip() for col in re.split(r'\s{2,}', line) if col.strip()]
            print(cols)

if __name__ == "__main__":
    investigate_bradesco_pdf("/home/pyter/Projects/bankEXtractor/tests/pdfs/BRADESCO.PDF")
