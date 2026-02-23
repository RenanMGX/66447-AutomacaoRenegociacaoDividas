import pandas as pd
import xlwings as xw
from xlwings.main import Book, Sheet, Range
from typing import Dict, List
import os
from patrimar_dependencies.functions import Functions
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
                          'Observação',
                          'Vencimento',
                          'Retorno',
                          'Desconto'
                          
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
    def replace_type(df: pd.DataFrame) -> pd.DataFrame:
        df['Data base'] = pd.to_datetime(df['Data base'])
        df['1° Vencimento'] = pd.to_datetime(df['1° Vencimento'])
        df['2° Vencimento'] = pd.to_datetime(df['2° Vencimento'])
        df['Vencimento'] = pd.to_datetime(df['Vencimento'])
        
        return df
    
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
            if column.value == 'Retorno':
                observacao_address = column.get_address()
                
        if observacao_address:
            for row, value in retorno.items():
                target_cell = re.sub(r'[0-9]+', str(row+2), observacao_address)
                ws.range(target_cell).value = value

        
        wb.save()
        wb.close()
        app.kill()
        
        Functions.fechar_excel(path)
        
        return

    @staticmethod   
    def corrigir_colunas_spacos(path:str) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"O arquivo '{path}' não foi encontrado!")
        elif not path.lower().endswith(('.xlsx', '.xls', '.xlsm')):
            raise TypeError("O arquivo deve ser um Excel!")
        
        app = xw.App(visible=False)
        with app.books.open(path) as wb:
            ws:Sheet = wb.sheets[0]
            
            columns_cells:Range = ws.range("A1").expand("right")
            for cell in columns_cells:
                cell.value = str(cell.value).strip()
                
            wb.save()
            
        app.kill()
        
        return

if __name__ == "__main__":
    pass
 