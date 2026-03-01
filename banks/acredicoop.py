import pandas as pd
import pdfplumber
import re

from core.formatador import clean_value, clean_date
from banks.base_bank import BaseBank

class AcredicoopBank(BaseBank):
    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Extrai dados do extrato PDF do Acredicoop.
        Baseado em texto flat com a estrutura:
        [DATA] [DESCRIÇÃO (Pode conter espaços)] [DOCUMENTO] [VALOR] [SALDO]
        """
        extracted_data = []

        date_pattern = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+')

        with pdfplumber.open(filepath) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
            lines = text.split('\n')
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                d_match = date_pattern.match(line)
                if d_match:
                    row_date = d_match.group(1)
                    remainder = line[d_match.end():].strip()
                    
                    # Vamos splitar de trás pra frente
                    # [Desc] [Doc] [Valor] [Saldo]
                    parts = remainder.rsplit(' ', 2)
                    if len(parts) == 3:
                        saldo_str = parts[2]
                        value_str = parts[1]
                        
                        desc_and_doc = parts[0]
                        # Tentar remover o ID do Doc se for os últimos caracteres compostos por números e ponto
                        desc_parts = desc_and_doc.rsplit(' ', 1)
                        if len(desc_parts) == 2 and re.match(r'^[\d\.]+$', desc_parts[1]):
                            desc = desc_parts[0]
                        else:
                            desc = desc_and_doc # Fallback: se o doc estiver nulo ou misturado
                            
                        extracted_data.append({
                            "DATA": clean_date(row_date),
                            "DESCRIÇÃO": desc.strip(),
                            "VALOR": clean_value(value_str)
                        })
                
                i += 1

        df = pd.DataFrame(extracted_data, columns=["DATA", "DESCRIÇÃO", "VALOR"])
        df = df.dropna(subset=['DATA'])
        return df
