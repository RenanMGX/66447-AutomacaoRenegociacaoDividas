import os
os.environ['project_name'] = "66447 - Automação de Renegociação de Dividas"
os.environ['conclusion_phrase'] = "Sucesso!"
##################

from Entities.dependencies.arguments import Arguments
from Entities.preparar_dados import PrepararDados
from Entities.imobme import Imobme
from Entities.dependencies.logs import Logs, traceback

import pandas as pd

def get_path():
    base_path = os.path.join(os.getcwd(), 'file')
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    file = [os.path.join(base_path, x) for x in os.listdir(base_path)]
    file.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    if file:
        return file[0]
    
    raise FileNotFoundError("Nenhum arquivo encontrado na pasta 'file'.")

class Main:
    @staticmethod
    def start():
        path = get_path()
            
        df = pd.read_excel(path)    
        
        df = PrepararDados.preparar_dados(path)
        if PrepararDados.validar_dados(df):
            bot = Imobme(headless=True)
            
            retorno = {}
            for row, value in df.iterrows():
                if value['Observação'] == os.environ['conclusion_phrase']:
                    retorno[row] = os.environ['conclusion_phrase']
                    continue
                try:
                    response = bot.registrar_renegociacao(value.to_dict(), debug=True) # <-------- Debug ON
                except Exception as e:
                    response = f"Exceção não tratada: {type(e)}, {str(e)}"
                    Logs().register(status='Report', description=str(e), exception=traceback.format_exc())
                
                retorno[row] = response

            bot.quit()
                
            PrepararDados.regitrar_retorno(path=path, retorno=retorno)
            
if __name__ == '__main__':
    Arguments({
        'start': Main.start
    })
