from abc import ABC, abstractmethod
import pandas as pd

class BaseBank(ABC):
    """
    Classe base (Contrato/Strategy) para todos os extratores de bancos.
    Qualquer novo banco adicionado ao sistema deve herdar desta classe
    e implementar o método `extract`.
    """

    @abstractmethod
    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Recebe o caminho de um arquivo PDF e retorna um DataFrame do pandas
        padronizado contendo as transações.
        
        O DataFrame de retorno DEVE conter as colunas obrigatórias:
        - "DATA" (formato dd/mm/aaaa ou data/datetime)
        - "DESCRIÇÃO" (texto descritivo do lançamento)
        - "VALOR" (float positivo para crédito, negativo para débito)
        """
        pass
