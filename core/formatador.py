import re
import pandas as pd

def clean_date(date_str: str) -> str:
    """
    Limpa e padroniza strings de data vindas de PDFs imperfeitos.
    Idealmente não faz parsing para datetime ainda, mas garante
    que sujeiras (espaços, caracteres espúrios) em volta da data sumam.
    """
    if pd.isna(date_str) or not date_str:
        return ""
        
    date_str = str(date_str).strip()
    # Pega apenas padrões d/m/y ou d-m-y
    match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{2,4})', date_str)
    if match:
         # Uniformiza separador para '/'
         return match.group(1).replace('-', '/')
    
    return date_str

def clean_value(val_str: str) -> float:
    """
    Converte os valores altamente caóticos e variantes do PDF em um Float negativo (Débito)
    ou positivo (Crédito).
    
    Exemplos Suportados:
    - "150,00" -> 150.0
    - "1.500,00" -> 1500.0
    - "-1.500,00" -> -1500.0
    - "80,00-" -> -80.0
    - "150,00 D" -> -150.0
    - "150,00 C" -> 150.0
    - "150,00 (-)" -> -150.0
    - "(150,00)" -> -150.0 (Padrão contábil americano, caso ocorra)
    """
    if not val_str or str(val_str).strip() == "":
        return 0.0

    val_str = str(val_str).strip().upper()
    is_negative = False

    # Detecção de sinais ou indicadores de débito na string original
    if '-' in val_str or '()' in val_str or ' D' in val_str or val_str.endswith('D') or val_str.startswith('('):
        is_negative = True

    # Remove todos os caracteres que não sejam dígitos ou vírgula
    # (Mantemos a vírgula do centavo provisoriamente)
    # Assumimos padrão BRL: "1.500,00" ou "1500,00"
    only_numbers_and_comma = re.sub(r'[^0-9,]', '', val_str)

    if not only_numbers_and_comma:
        return 0.0

    # Troca a vírgula (decimal do brasil) por ponto pra conversão em float
    float_str = only_numbers_and_comma.replace(',', '.')

    try:
        val_float = float(float_str)
        if is_negative:
            val_float = -abs(val_float)
        else:
            val_float = abs(val_float)
            
        return val_float
    except ValueError:
        return 0.0
