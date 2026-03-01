import pandas as pd
import pdfplumber
import re

from core.formatador import clean_value, clean_date
from banks.base_bank import BaseBank

class BbBank(BaseBank):
    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Extrai dados do extrato PDF do Banco do Brasil (BB).
        Como os PDFs do BB muitas vezes não utilizam caixas rígidas de tabela,
        usamos processamento textual linha-a-linha com RegEx.
        """
        extracted_data = []

        # Regex para capturar: DATA (Espaço) DESCRIÇÃO (Espaço) VALOR (Espaço Opcional) SINAL (+ ou -)
        # Exemplo: 01/02/2024 BB GIRO PRONAMPE 15.125,99 (-)
        pattern = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d\.,]+)\s*(\([\-\+]\))?$')

        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    match = pattern.match(line)
                    if match:
                        data_str = match.group(1)
                        desc_str = match.group(2).strip()
                        val_str = match.group(3)
                        sinal = match.group(4)
                        
                        # Processa sinal negativo financeiro no formato "(-)"
                        if sinal == '(-)':
                            val_str = '-' + val_str
                            
                        extracted_data.append({
                            "DATA": clean_date(data_str),
                            "DESCRIÇÃO": desc_str,
                            "VALOR": clean_value(val_str)
                        })

        df = pd.DataFrame(extracted_data, columns=["DATA", "DESCRIÇÃO", "VALOR"])
        return df
