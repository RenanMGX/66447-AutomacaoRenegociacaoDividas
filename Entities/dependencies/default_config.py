from typing import Dict
from getpass import getuser

default:Dict[str, Dict[str,object]] = {
    'log': {
        'hostname': 'Patrimar-RPA',
        'port': '80',
        'token': 'Central-RPA'
    },
    'crd': {
        'imobme': 'IMOBME_QAS'
    },
    'nav':{
        'headless': True
    }
}