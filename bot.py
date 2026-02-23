"""
WARNING:

Please make sure you install the bot dependencies with `pip install --upgrade -r requirements.txt`
in order to get all the dependencies on your Python environment.

Also, if you are using PyCharm or another IDE, make sure that you use the SAME Python interpreter
as your IDE.

If you get an error like:
```
ModuleNotFoundError: No module named 'botcity'
```

This means that you are likely using a different Python interpreter than the one used to install the dependencies.
To fix this, you can either:
- Use the same interpreter as your IDE and install your bot with `pip install --upgrade -r requirements.txt`
- Use the same interpreter as the one used to install the bot (`pip install --upgrade -r requirements.txt`)

Please refer to the documentation for more information at
https://documentation.botcity.dev/tutorials/custom-automations/python-custom/
"""
# Import for integration with BotCity Maestro SDK
from botcity.maestro import * #type: ignore
import traceback
from patrimar_dependencies.gemini_ia import ErrorIA
from patrimar_dependencies.screenshot import screenshot
from datetime import datetime
from main import Main, os
from patrimar_dependencies.task_botcity import TaskBotCity
from pathlib import Path
from patrimar_dependencies.sharepointfolder import SharePointFolders
from Entities.alert_botcity import bot_alert

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False #type: ignore

class Processos:
    @property
    def total(self) -> int:
        return self.__total
    
    @property
    def processados(self) -> int:
        return self.__processados
    
    @property
    def falhas(self) -> int:
        result = self.total - self.processados
        return result if result >= 0 else 0
    
    def __init__(self, value:int) -> None:
        self.__total:int = value
        self.__processados:int = 0
        
    def add_processado(self, value:int=1):
        for _ in range(value):
            if (self.processados + 1) <= self.total:
                self.__processados += 1

class Execute:
    @staticmethod
    def start():
        date_param = execution.parameters.get("date") # date_param <----------------------
        if date_param:
            date = datetime.strptime(str(date_param), "%d/%m/%Y")
        else:
            date = datetime.now()  # Data de exemplo, pode ser alterada conforme necessário

        crd_param = execution.parameters.get("crd") # crd_param <----------------------
        if not crd_param:
            raise Exception(f"O parametro {crd_param=} está vazio!")
        else:
            crd_param = str(crd_param)

        method_param = execution.parameters.get("method") # method_param <----------------------
        if not method_param:
            raise Exception(f"O parametro {method_param=} está vazio!")
        else:
            method = str(method_param)

        if method == "on_demand":
            #bot_alert("TESTE DE ALERTA ON DEMAND")
            file_name_param = execution.parameters.get("file_name") # file_name_param <----------------------
            if not file_name_param:
                raise Exception(f"O parametro {file_name_param=} está vazio!")
            else:
                file_name = str(file_name_param)
            
            file_param = execution.parameters.get("file") # file_param <----------------------
            if not file_param:
                raise Exception(f"O parametro {file_param=} está vazio!")
            else:
                file = str(file_param)
                #file_path = os.path.join(os.getcwd(), "file", datetime.now().strftime("%Y%m%d%H%M%S"), file_name)
                file_path = Path.cwd().joinpath("file").joinpath(datetime.now().strftime("%Y%m%d%H%M%S%f")).joinpath(file_name)
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(str(file_path), 'wb') as _file:
                    _file.write(TaskBotCity.decode_file(file))
            
            Main.start(
                path=str(file_path),
                url=maestro.get_credential(label=crd_param, key="url"),
                login=maestro.get_credential(label=crd_param, key="login"),
                password=maestro.get_credential(label=crd_param, key="password"),
            )
            
            maestro.post_artifact(
                task_id=int(execution.task_id),
                artifact_name=os.path.basename(file_path),
                filepath=str(file_path)
            )      
            
            try:
                os.unlink(str(file_path))
            except:
                pass
            
            
        elif method == "scheduled":
            folder_path_param = execution.parameters.get("folder_path") # folder_path_param <----------------------
            if not folder_path_param:
                raise Exception(f"O parametro {folder_path_param=} está vazio!")
            else:
                folder_path = str(folder_path_param)
                if "SHAREPOINT::" in folder_path:
                    folder_path = folder_path.replace("SHAREPOINT::", "")
                    if not folder_path:
                        raise Exception(f"O parametro {folder_path=} está vazio!")                    
                    folder_path = SharePointFolders(folder_path)
            
            if not os.path.exists(folder_path):
                raise FileNotFoundError(f"O caminho '{folder_path}' não foi encontrado!")
            if not os.path.isdir(folder_path):
                raise NotADirectoryError(f"O caminho '{folder_path}' não é uma pasta!")
            
            
            
            Main.multi_start(
                folder_path=folder_path,
                url=maestro.get_credential(label=crd_param, key="url"),
                login=maestro.get_credential(label=crd_param, key="login"),
                password=maestro.get_credential(label=crd_param, key="password"),
            )

        else:
            raise Exception(f"O parametro {method=} é inválido! Deve ser 'on_demand' ou 'scheduled'.")
        
        p.add_processado()

if __name__ == '__main__':
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()
    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    task_name = execution.parameters.get('task_name')
    
    p = Processos(1)

    try:
        Execute.start()
        
        maestro.finish_task(
                    task_id=execution.task_id,
                    status=AutomationTaskFinishStatus.SUCCESS,
                    message=f"Tarefa {task_name} finalizada com sucesso",
                    total_items=p.total, # Número total de itens processados
                    processed_items=p.processados, # Número de itens processados com sucesso
                    failed_items=p.falhas # Número de itens processados com falha
        )
        
    except Exception as error:
        ia_response = "Sem Resposta da IA"
        try:
            token = maestro.get_credential(label="GeminiIA-Token-Default", key="token")
            if isinstance(token, str):
                ia_result = ErrorIA.error_message(
                    token=token,
                    message=traceback.format_exc()
                )
                ia_response = ia_result.replace("\n", " ")
        except Exception as e:
            maestro.error(task_id=int(execution.task_id), exception=e)

        maestro.error(task_id=int(execution.task_id), exception=error, screenshot=screenshot(), tags={"IA Response": ia_response})
        maestro.finish_task(
                    task_id=execution.task_id,
                    status=AutomationTaskFinishStatus.FAILED,
                    message=f"Tarefa {task_name} finalizada com Error",
                    total_items=p.total, # Número total de itens processados
                    processed_items=p.processados, # Número de itens processados com sucesso
                    failed_items=p.falhas # Número de itens processados com falha
        )
