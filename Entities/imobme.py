import os
import re
import exceptions

from dependencies.functions import P
from dependencies.navegador_chrome import NavegadorChrome, By, Keys, WebDriver, WebElement
from dependencies.credenciais import Credential
from dependencies.config import Config
from time import sleep
from typing import Union

class Imobme(NavegadorChrome):
    @property
    def base_url(self) -> str:
        if (url:=re.search(r'[A-z]+://[A-z0-9.]+/', self.__crd['url'])):
            return url.group()
        raise exceptions.UrlError("URL inválida!")
    
    @staticmethod
    def verify_login(func):
        def wrap(*args, **kwargs):
            self:Imobme = args[0]
            
            tag_html = self.find_element(By.TAG_NAME, 'html').text
            if "Imobme - Autenticação" in tag_html:
                print(P("Efetuando login...", color='yellow'))
                sleep(3)
                self.find_element(By.ID, 'login').send_keys(self.__crd['login'])
                t_password = self.find_element(By.ID, 'password')
                t_password.send_keys(self.__crd['password'])
                
                print(P("Aguardando resposta...", color='yellow'))
                t_password.send_keys(Keys.ENTER)                
                
                sleep(2)
                tag_html = self.find_element(By.TAG_NAME, 'html').text
                if "\nLogin não encontrado.\n" in self.find_element(By.TAG_NAME, 'html').text:
                    print(P("Login não encontrado!", color='red'))
                    raise exceptions.LoginError("Login não encontrado!")
                
                tag_html = self.find_element(By.TAG_NAME, 'html').text
                if (t_senha_invalida:=re.search(r'Senha Inválida. Número de Tentativas Restantes: [0-9]', tag_html)):
                    print(P(t_senha_invalida.group(), color='red'))
                    raise exceptions.LoginError(t_senha_invalida.group())
                
                tag_html = self.find_element(By.TAG_NAME, 'html').text
                if "\nUsuário já logado!\n" in self.find_element(By.TAG_NAME, 'html').text:
                    self.find_element(By.XPATH, '/html/body/div[2]/div[3]/div/button[1]').click()
                
                #import pdb;pdb.set_trace()
                print(P("Login efetuado com sucesso!", color='green'))
                sleep(1)

            result = func(*args, **kwargs)

            return result
        return wrap
    
    def __init__(self, *, download_path:str=os.path.join(os.getcwd(), 'downloads')) -> None:
        if (re.search(r'[.][a-zA-Z]+', os.path.basename(download_path))):
            download_path = os.path.dirname(download_path)
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            
        self.__crd:dict = Credential(Config()['crd']['imobme']).load()
                    
        super().__init__(download_path=download_path)
        
        self.__load_page('Autenticacao/Login')
        sleep(3)
        self.__load_page('Autenticacao/Login')
        self.maximize_window()
        
    def __load_page(self, endpoint:str):
        if not endpoint.endswith('/'):
            endpoint += '/'
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        
        url = os.path.join(self.base_url, endpoint)
        print(P(f"Carregando página: {url}...          ", color='yellow'))  
        self.get(url)
        
    def __esperar_carregamento(self, *, initial_wait:Union[int, float]=1):
        sleep(initial_wait)
        while self._find_element(By.ID, 'feedback-loader').text == 'Carregando':
            print(P("Aguardando carregar página...                ", color='yellow'), end='\r')
            sleep(1)
        print(end='\r')
                
    @verify_login     
    def _find_element(self, by=By.ID, value: str | None = None, *, timeout: int = 10, force: bool = False, wait_before: int | float = 0, wait_after: int | float = 0) -> WebElement:
        return super().find_element(by, value, timeout=timeout, force=force, wait_before=wait_before, wait_after=wait_after)
        
    @verify_login
    def teste(self):
        self.__load_page('CalculoMensal/Cobranca')
        
        
if __name__ == '__main__':
    pass