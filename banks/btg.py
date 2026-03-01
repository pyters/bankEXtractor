import pandas as pd
import pdfplumber
import sys
import os
import re

from core.formatador import clean_value, clean_date
from banks.base_bank import BaseBank

class BtgBank(BaseBank):
    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Extrai dados do extrato PDF do BTG Pactual baseado no layout real de tabelas.
        """
        extracted_data = []
        
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        # O BTG gera tabelas de pelo menos 4 colunas: Data, Descrição, Valor, Saldo
                        if len(row) >= 3:
                            data_str = str(row[0]).strip() if row[0] else ""
                            desc_str = str(row[1]).strip() if row[1] else ""
                            valor_str = str(row[2]).strip() if row[2] else ""
                            
                            # Filtros básicos para ignorar headers e rodapés vazios
                            if not data_str or data_str.lower() == "data lançamento":
                                continue
                                
                            # Verifica se a coluna 1 parece uma data válida DD/MM/AAAA
                            if not re.match(r'^\d{2}/\d{2}/\d{4}$', data_str):
                                continue
                                
                            # Remove as quebras de linha (`\n`) inseridas internamente pelo pdfplumber
                            desc_limpa = desc_str.replace('\n', ' ')
                            
                            # Agora o usuário quer transações sem valor ('Saldo de Fechamento', 'Saldo de abertura')
                            # e rendimentos ('Valor de Rendimento Remunera+') salvas como 0.00
                            # Vamos limpar o valor para 0.0 se não existir
                            
                            final_val = 0.0
                            if valor_str and valor_str.strip() != "":
                                final_val = clean_value(valor_str)
                                
                            # Mas caso seja a linha de rendimento que POSSUI valor numérico real, mas o contexto
                            # do usuário antes pedia para ignorar, vamos verificar se ela vai com valor ou sempre zero.
                            # O Remunera+ geralmente tem valor positivo. Vamos incluir normalmente o valor dela,
                            # a menos que o contábil também queira ignorar esse micro-centavo e por zerado. 
                            # Por padrão, vamos extrair o valor real dela, já que agora ela não é mais banida.
                            
                            extracted_data.append({
                                "DATA": clean_date(data_str),
                                "DESCRIÇÃO": desc_limpa,
                                "VALOR": final_val
                            })

        df = pd.DataFrame(extracted_data, columns=["DATA", "DESCRIÇÃO", "VALOR"])
        return df
