import os
from dotenv import load_dotenv; load_dotenv()
os.environ['project_name'] = "66447 - Automação de Renegociação de Dividas"
os.environ['conclusion_phrase'] = "sucesso!"
os.environ['already_exist'] = "Este contrato já possui uma solicitação em andamento."
##################
#from patrimar_dependencies.informativo import Informativo
#Informativo().limpar()
from Entities.preparar_dados import PrepararDados
from Entities.imobme import Imobme
from patrimar_dependencies.informativo import P
import json
import locale ; locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
from pathlib import Path
from datetime import datetime
import shutil
from patrimar_dependencies.functions import Functions
from Entities.alert_botcity import bot_alert

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
    def start(
        *,
        path:str,
        url:str,
        login:str,
        password:str,
        headless=False
    ):
        #Informativo().register("Iniciando o processo de renegociação de dívidas...", color='<django:blue>')
        bot_alert("Iniciando o processo de renegociação de dívidas...")
        
        
        try:
            PrepararDados.corrigir_colunas_spacos(path)
        except Exception as e:
            #Informativo().register(f"{type(e)} - {str(e)}", color='<django:red>')
            bot_alert(f"{type(e)} - {str(e)}", alert_type='ERROR')
            raise e
          
        df = pd.read_excel(path)    
        
        try:
            
            df = PrepararDados.preparar_dados(path)
            dados_validados = PrepararDados.validar_dados(df)
        except Exception as e:
            #Informativo().register(f"{type(e)} - {str(e)}", color='<django:red>')
            bot_alert(f"{type(e)} - {str(e)}", alert_type='ERROR')
            raise e
            
        if dados_validados:
            df = PrepararDados.replace_type(df)
            bot = Imobme(
                url=url,
                login=login,
                password=password,
                headless=headless
            )

            retorno = {}
            for row, value in df.iterrows():
                #Informativo().register(f"Processando linha {int(str(row)) + 1} de {len(df)}: {value['Numero do contrato']}")
                bot_alert(f"    Processando linha {int(str(row)) + 1} de {len(df)} - Numero do contrato: {value['Numero do contrato']}")
                if (os.environ['conclusion_phrase'] in str(value['Retorno'])) or (os.environ['already_exist'] in str(value['Retorno'])):
                    retorno[row] = os.environ['conclusion_phrase']
                    continue
                try:
                    response = bot.registrar_renegociacao(value.to_dict(), debug=False) # <-------- Debug OFF
                except Exception as e:
                    response = f"Exceção não tratada: {type(e)}, {str(e)}"
                    print(P(response, color='red'))
                    #Informativo().register(response, color='<django:red>')
                    bot_alert(f"    {response}", alert_type='ERROR')
                
                retorno[row] = response

            bot.quit()
            
            with open(os.path.join(os.getcwd(), 'last_retorno.json'), 'w') as f:
                json.dump(retorno, f, indent=4)
            
            for _ in range(3): 
                try:
                    PrepararDados.regitrar_retorno(path=path, retorno=retorno)
                    break
                except Exception as e:
                    if _ >= 2:
                        #Informativo().register(f"{type(e)} - {str(e)}", color='<django:red>')
                        bot_alert(f"{type(e)} - {str(e)}", alert_type='ERROR')
                        raise e
                
            
            #Informativo().register("Processo concluído com sucesso!", color='<django:green>')
            bot_alert("Processo concluído com sucesso!")
        
        return path
    
    @staticmethod
    def multi_start(
        *,
        folder_path:str,
        url:str,
        login:str,
        password:str,
    ):
        date = datetime.now()
        for file in os.listdir(folder_path):
            file = Path(folder_path).joinpath(file)
            try:
                if file.is_file():
                    if file.suffix in ['.xlsx', '.xls', '.xlsm']:
                            Main.start(
                                path=str(file),
                                url=url,
                                login=login,
                                password=password,
                            )
                            
                            new_file = file.parent.joinpath("Processados").joinpath(date.strftime("%Y")).joinpath(date.strftime("%B")).joinpath(file.name.replace(file.suffix, datetime.now().strftime(f"_%Y%m%d%H%M%S%f{file.suffix}")))
                            new_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            Functions.fechar_excel(str(file))
                            
                            shutil.move(str(file), str(new_file))
                        
            except Exception as e:
                print(f"Erro ao processar o arquivo '{file}': {e}")

            
    @staticmethod
    def teste():
        import pdb;pdb.set_trace()
        input("Teste de execução bem-sucedida. Pressione Enter para continuar...")
            
if __name__ == '__main__':
    from patrimar_dependencies.credenciais_botcity import CredentialBotCity
    
    crd = CredentialBotCity(
        login=os.getenv('BOTCITY_LOGIN', ''),
        key=os.getenv('BOTCITY_KEY', '')
    ).get_credential(
        'IMOBME_PRD'
    )
    
    print(crd)
    
    Main.multi_start(
        folder_path=r'file',
        url=crd['url'],
        login=crd['login'],
        password=crd['password'],
    )
        
    # Main.start(
    #     path=r'file\Renegociação.xlsm',
    #     url=crd['url'],
    #     login=crd['login'],
    #     password=crd['password'],
    #     headless=False
    # )
    