import os
os.environ['project_name'] = "66447 - Automação de Renegociação de Dividas"
os.environ['conclusion_phrase'] = "sucesso!"
os.environ['already_exist'] = "Este contrato já possui uma solicitação em andamento."
##################
from Entities.dependencies.informativo import Informativo
Informativo().limpar()
from Entities.dependencies.arguments import Arguments
from Entities.preparar_dados import PrepararDados
from Entities.dependencies.config import Config
from Entities.imobme import Imobme
from Entities.dependencies.logs import Logs, traceback
from Entities.dependencies.functions import P

#from distutils.util import strtobool

def strtobool(val):
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"invalid truth value {val!r}")


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
        print(P("Iniciando o processo de renegociação de dívidas...", color='blue'))
        Informativo().register("Iniciando o processo de renegociação de dívidas...", color='<django:blue>')
        
        path = get_path()
        
        try:
            PrepararDados.corrigir_colunas_spacos(path)
        except Exception as e:
            Informativo().register(f"{type(e)} - {str(e)}", color='<django:red>')
            raise e
          
        df = pd.read_excel(path)    
        
        try:
            
            df = PrepararDados.preparar_dados(path)
            dados_validados = PrepararDados.validar_dados(df)
        except Exception as e:
            Informativo().register(f"{type(e)} - {str(e)}", color='<django:red>')
            raise e
            
        if dados_validados:
            df = PrepararDados.replace_type(df)
            bot = Imobme(headless=strtobool(Config()['nav']['headless']))

            retorno = {}
            for row, value in df.iterrows():
                print(P(f"Processando linha {int(str(row)) + 1} de {len(df)}: {value['Numero do contrato']}"))
                Informativo().register(f"Processando linha {int(str(row)) + 1} de {len(df)}: {value['Numero do contrato']}")
                if (os.environ['conclusion_phrase'] in str(value['Retorno'])) or (os.environ['already_exist'] in str(value['Retorno'])):
                    retorno[row] = os.environ['conclusion_phrase']
                    continue
                try:
                    response = bot.registrar_renegociacao(value.to_dict(), debug=False) # <-------- Debug OFF
                except Exception as e:
                    response = f"Exceção não tratada: {type(e)}, {str(e)}"
                    print(P(response, color='red'))
                    Informativo().register(response, color='<django:red>')
                    Logs().register(status='Report', description=str(e), exception=traceback.format_exc())
                
                retorno[row] = response

            bot.quit()
                
            PrepararDados.regitrar_retorno(path=path, retorno=retorno)
            
            print(P("Processo concluído com sucesso!", color='green'))
            Informativo().register("Processo concluído com sucesso!", color='<django:green>')
            Logs().register(status='Concluido', description="Processo concluído com sucesso!")
            
    @staticmethod
    def teste():
        import pdb;pdb.set_trace()
        strtobool(Config()['nav']['headless'])
        input("Teste de execução bem-sucedida. Pressione Enter para continuar...")
            
if __name__ == '__main__':
    Arguments({
        'start': Main.start,
        'teste': Main.teste,
    })
