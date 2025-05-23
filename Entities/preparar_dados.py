import pandas as pd
import xlwings as xw
from xlwings.main import Book, Sheet, Range
from typing import Dict, List
import os
from Entities.dependencies.functions import Functions
import re

class PrepararDados:
    @staticmethod
    def preparar_dados(path:str) -> pd.DataFrame:
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path=} não existe!")
        if not path.lower().endswith(('.xlsx', '.xls', '.xlsm')):
            raise TypeError(f"{path=} não é um arquivo excel!")
        
        df = pd.read_excel(path)
        if df.empty:
            raise ValueError(f"{path=} não possui dados!")
        
        # df = df[
        #     df['Observação'] != "Sucesso!"
        # ]
        
        return df
    
    @staticmethod
    def validar_dados(df:pd.DataFrame,
                      *, 
                      valid_columns:list = [
                          'Numero do contrato',
                          'Data base',
                          '1° Vencimento',
                          '2° Vencimento',
                          'Valor vencido',
                          'Valor da entrada',
                          'Vencimento da entrada',
                          'Valor parcelado',
                          'Quantidade de Parcelas',
                          'Valor da mensal',
                          'Vencimento',
                      ]
                      
                      ) -> bool:
        
        columns_not_found = []
        for valid_column in valid_columns:
            if valid_column not in df.columns:
                columns_not_found.append(valid_column)
                
        if columns_not_found:
            raise ValueError(f"Colunas não encontradas: {columns_not_found}")
        
        
        return True
    
    @staticmethod
    def regitrar_retorno(*, path:str, retorno:Dict[int, str]) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path=} não existe!")
        if not path.lower().endswith(('.xlsx', '.xls', '.xlsm')):
            raise TypeError(f"{path=} não é um arquivo excel!")
        
        Functions.fechar_excel(path)
        app = xw.App(visible=False)
        wb:Book = app.books.open(path)
        ws:Sheet = wb.sheets[0]
        
        columns:Range = ws.range('A1').expand('right')
        observacao_address:str = ""
        for column in columns:
            if column.value == 'Observação':
                observacao_address = column.get_address()
                
        if observacao_address:
            for row, value in retorno.items():
                target_cell = re.sub(r'[0-9]+', str(row+2), observacao_address)
                ws.range(target_cell).value = value

        
        #import pdb;pdb.set_trace()
        wb.save()
        wb.close()
        app.kill()
        
        Functions.fechar_excel(path)
        
        return