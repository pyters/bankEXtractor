import pandas as pd
import pdfplumber

from core.formatador import clean_value, clean_date
from banks.base_bank import BaseBank

class SicrediBank(BaseBank):
    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Extrai dados do extrato PDF do Sicredi.
        O Sicredi possui grids limpos nativos identificáveis diretamente pelo pdfplumber.
        """
        extracted_data = []

        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables:
                    continue
                    
                for table in tables:
                    for row in table:
                        if len(row) < 4:
                            continue
                            
                        data_str = str(row[0]).strip() if row[0] else ""
                        desc_str = str(row[1]).strip() if row[1] else ""
                        val_str = str(row[3]).strip() if row[3] else ""
                        
                        # Ignorar cabeçalho da tabela
                        if "Data" in data_str and "Descrição" in desc_str:
                            continue
                            
                        # Limpar quebras de linha que o pdfplumber junta dentro da mesma célula num PDF Sicredi
                        desc_str = desc_str.replace('\n', ' ')
                        
                        # Fix Saldo Anterior
                        if "SALDO ANTERIOR" in desc_str.upper():
                            val_str = "0,00"
                        elif not val_str:
                            continue
                            
                        extracted_data.append({
                            "DATA": clean_date(data_str),
                            "DESCRIÇÃO": desc_str,
                            "VALOR": clean_value(val_str)
                        })

        df = pd.DataFrame(extracted_data, columns=["DATA", "DESCRIÇÃO", "VALOR"])
        
        # Como no Sicredi o Sicredi pode imprimir a Data apenas na primeira transação do dia (ou repetir?)
        # Baseado em nossa analise de amostra do Sicredi antes: ele normalmente repete ou deixa vario?
        # Se for vazio, damos um forward fill.
        # "SALDO ANTERIOR" as vezes cai sem data, então damos None para apagar.
        # Se a Data original que entrou pro clean_date for "", retorna None
        # if `extracted_data` first rows has None date due to SALDO ANTERIOR... 
        
        # Vamos rodar preenchimento pra frente se necessário
        df['DATA'] = df['DATA'].ffill()
        df = df.dropna(subset=['DATA'])
        
        return df
