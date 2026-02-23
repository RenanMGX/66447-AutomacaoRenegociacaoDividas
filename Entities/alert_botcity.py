from botcity.maestro import * #type: ignore
from typing import Literal

try:
    maestro:BotMaestroSDK = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()
except:
    maestro = None #type: ignore

def bot_alert(
    message:str, 
    #alert_type:AlertType=AlertType.INFO, 
    alert_type:Literal[
        "INFO",
        "ERROR",
        "WARNING"
        ] = "INFO", 
    title:str="Informativo"
):  
    if alert_type == "INFO":
        _alert_type = AlertType.INFO
    elif alert_type == "ERROR":
        _alert_type = AlertType.ERROR
    elif alert_type == "WARNING":
        _alert_type = AlertType.WARN
    
    if maestro:
        maestro.alert(
            task_id=execution.task_id,#type: ignore
            title=title,
            message=message,
            alert_type=_alert_type
        )
    print(message)
        
if __name__ == "__main__":
    pass
