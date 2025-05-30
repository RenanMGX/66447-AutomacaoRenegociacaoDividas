import os
import re
import exceptions
import math

from dependencies.functions import P
from dependencies.navegador_chrome import NavegadorChrome, By, Keys, WebDriver, WebElement, Select
from dependencies.credenciais import Credential
from dependencies.config import Config
from dependencies.informativo import Informativo
from time import sleep
from typing import Union
from datetime import datetime

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
    
    def __init__(self, *, headless:bool=True, download_path:str=os.path.join(os.getcwd(), 'downloads')) -> None:
        if (re.search(r'[.][a-zA-Z]+', os.path.basename(download_path))):
            download_path = os.path.dirname(download_path)
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            
        self.__crd:dict = Credential(Config()['crd']['imobme']).load()
                    
        super().__init__(download_path=download_path, headless=headless)
        
        self.__load_page('Autenticacao/Login')
        sleep(3)
        self.maximize_window()
        self.__start()
        
        
    def __load_page(self, endpoint:str, *, remover_barra_final:bool=False):
        if not endpoint.endswith('/'):
            if not remover_barra_final:
                endpoint += '/'
            
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        
        url = os.path.join(self.base_url, endpoint)
        print(P(f"Carregando página: {url}...          ", color='yellow'))  
        
        self.get(url, load_timeout=60)
        
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
    def __start(self):
        self.__load_page('Contrato')
        print(P("Pagina Iniciada no Contrato!"))
        
    @verify_login
    def registrar_renegociacao(self, dados:dict, *, debug:bool=False):   
        self.__load_page(f"Contrato/PosicaoFinanceira/{int(dados['Numero do contrato'])}")
        
        data_base:datetime = dados['Data base']
        self._find_element(By.ID, 'DataPosicao').clear()
        self._find_element(By.ID, 'DataPosicao').send_keys(data_base.strftime('%d%m%Y'))

        self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[2]/div[1]/form/button').click()
        self.__esperar_carregamento()
        self.__load_page(f"Contrato/Renegociacao/{int(dados['Numero do contrato'])}?dataPosicao={data_base.strftime('%Y-%m-%d')}", remover_barra_final=True)
        
        try:
            adv_text = self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[1]/div/div').text
            if os.environ['already_exist'] in adv_text:
                print(P(adv_text, color='red'))
                Informativo().register(text=adv_text, color='<django:red>')
                return adv_text
        except:
            pass
        
        
        
        is_pcv = False
        tbody_s = self.find_elements(By.TAG_NAME, 'tbody')
        
        for tbody in tbody_s:
            try:
                text = tbody.text
                if f"{int(dados['Numero do contrato'])} - PCV" in text:
                    is_pcv = True
                    break
            except:
                pass
          
        #self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[6]/div/h4').location_once_scrolled_into_view
        
        self._find_element(By.XPATH, '//*[@id="tab-serie"]/thead/tr').location_once_scrolled_into_view
        
        data1 = dados['1° Vencimento']
        data2 = dados['2° Vencimento']
        tbody = self._find_element(By.XPATH, '//*[@id="tab-parcela"]/tbody')
        for tr in tbody.find_elements(By.TAG_NAME, 'tr'):
            td_date = datetime.strptime(tr.find_element(By.XPATH, 'td[4]').text, "%d/%m/%Y")
            if (td_date >= data1) and (td_date <= data2):
                td_check_box = tr.find_element(By.XPATH, 'td[1]')

                td_check_box.find_elements(By.TAG_NAME, 'input')[0].click()
                
            self.execute_script("window.scrollBy(0, 35);")
            
        self._find_element(By.ID, 'AgreementTabs').location_once_scrolled_into_view
        
        total_com_ajuste = round(float(self._find_element(By.ID, 'total-com-ajuste').text.replace('.', '').replace(',', '.')), 2)
        
        if not total_com_ajuste == round(dados['Valor vencido'], 2):
            print(P(f"Valor vencido: {dados['Valor vencido']} diferente do valor total com ajuste: {total_com_ajuste}", color='red'))
            Informativo().register(text=f"Valor vencido: {dados['Valor vencido']} diferente do valor total com ajuste: {total_com_ajuste}", color='<django:red>')
            return f"Valor vencido: {dados['Valor vencido']} diferente do valor total com ajuste: {total_com_ajuste}"
        
        self._find_element(By.ID, 'total-com-ajuste').location_once_scrolled_into_view
        
        # Parcela Unica
        try:
            dados['Vencimento da entrada'].today()
            if math.isnan(dados['Valor da entrada']):
                raise Exception("não é valor valido")
            
            while len(str(self._find_element(By.ID, 'ValorSerie').get_attribute('value'))) > 0:
                self._find_element(By.ID, 'ValorSerie').send_keys(Keys.BACKSPACE)
            
            self._find_element(By.ID, 'ValorSerie').send_keys(dados['Valor da entrada'])
            
            self.__select(select_id='TipoParcelaId_chosen', target='Poupança')
            
            self.__select(select_id='PeriodicidadeId_chosen', target='Única')
                    
            self._find_element(By.ID, 'DataPrimeiraParcela').clear()
            self._find_element(By.ID, 'DataPrimeiraParcela').send_keys(dados['Vencimento da entrada'].strftime('%d%m%Y'))
            
            if is_pcv:
                self._find_element(By.ID, 'TemCorrecao').click()
            
            self._find_element(By.ID, 'btnSerieAdd').click()
            
            self.__esperar_carregamento() 
            
            total_diferenca = round(float(self._find_element(By.ID, 'total-diferenca').text.replace('.', '').replace(',', '.')), 2)
            
            if not total_diferenca == round(dados['Valor parcelado'], 2):
                print(P(f"Valor parcelado: {dados['Valor parcelado']} diferente do valor total diferenca: {total_diferenca}", color='red'))
                Informativo().register(text=f"Valor parcelado: {dados['Valor parcelado']} diferente do valor total diferenca: {total_diferenca}", color='<django:red>')
                return f"Valor parcelado: {round(dados['Valor parcelado'], 2)} diferente do valor total diferenca: {total_diferenca}"
        except:
            pass
                    
        
        # Parcelas
        try:
            dados['Vencimento'].today()
            
            if math.isnan(dados['Valor parcelado']):
                raise Exception("não é valor valido")
            
            if math.isnan(dados['Quantidade de Parcelas']):
                raise Exception("não é valor valido")
            
            if math.isnan(dados['Valor da mensal']):
                raise Exception("não é valor valido")
            
            while len(str(self._find_element(By.ID, 'ValorSerie').get_attribute('value'))) > 0:
                self._find_element(By.ID, 'ValorSerie').send_keys(Keys.BACKSPACE)
            
            self._find_element(By.ID, 'ValorSerie').send_keys(round(dados['Valor parcelado'], 2))
            
            
            self.__select(select_id='TipoParcelaId_chosen', target='Poupança')
            
            self.__select(select_id='PeriodicidadeId_chosen', target='Mensal')
            
            for _ in range(5):
                self._find_element(By.ID, 'QuantidadeParcelas').send_keys(Keys.BACK_SPACE)
            self._find_element(By.ID, 'QuantidadeParcelas').send_keys(dados['Quantidade de Parcelas'])
            
            self._find_element(By.ID, 'ValorParcela').click()
            
            valor_parcela = round(float(str(self._find_element(By.ID, 'ValorParcela').get_attribute('value')).replace('.', '').replace(',', '.')), 2)
            
            if not valor_parcela == round(dados['Valor da mensal'], 2):
                print(P(f"Valor da mensal: {dados['Valor da mensal']} diferente do valor da parcela: {valor_parcela}", color='red'))
                Informativo().register(text=f"Valor da mensal: {dados['Valor da mensal']} diferente do valor da parcela: {valor_parcela}", color='<django:red>')
                return f"Valor da mensal: {round(dados['Valor da mensal'], 2)} diferente do valor da parcela: {valor_parcela}"
            
            
            self._find_element(By.ID, 'DataPrimeiraParcela').clear()
            self._find_element(By.ID, 'DataPrimeiraParcela').send_keys(dados['Vencimento'].strftime('%d%m%Y'))
            
            if is_pcv:
                self._find_element(By.ID, 'TemCorrecao').click()
            
            self._find_element(By.ID, 'btnSerieAdd').click()
            
            self.__esperar_carregamento() 
            
            total_diferenca = float(self._find_element(By.ID, 'total-diferenca').text.replace('.', '').replace(',', '.'))
            
            if total_diferenca != 0:
                print(P(f"Valor total diferenca: {total_diferenca} diferente de 0", color='red'))
                Informativo().register(text=f"Valor total diferenca: {total_diferenca} diferente de 0", color='<django:red>')
                return f"Valor total diferenca: {total_diferenca} diferente de 0"
        except:
            pass
          
        
        
        #import pdb;pdb.set_trace()
        try:
            self._find_element(By.XPATH, '/html/body/div[2]/div[3]/div/button', timeout=2).click()
            erro_msg = self._find_element(By.ID, 'mensagemModal').text
            print(P(f"Erro: {erro_msg}", color='red'))
            Informativo().register(text=f"Erro: {erro_msg}", color='<django:red>')
            return f"{round(dados['Valor parcelado'], 2)} {erro_msg}"

        except:
            pass
        self._find_element(By.ID, 'MotivoId').location_once_scrolled_into_view
        
        options = Select(self._find_element(By.ID, 'MotivoId'))
        options.select_by_value('5')
        
        if dados['Observação']:
            self._find_element(By.ID, 'Observacao').send_keys(dados['Observação'])
        else:
            self._find_element(By.ID, 'Observacao').send_keys("KITEI")
        
        import pdb;pdb.set_trace()
        if not debug:
            self._find_element(By.ID, 'Solicitar').click()
        
        
        try:
            alert = self._find_element(By.ID, 'divAlert', timeout=1)
            print(P(f"Sucesso: {alert.text}", color='green'))
            Informativo().register(text=f"Sucesso: {alert.text}", color='<django:green>')
            return alert.text
        except:
            pass
        
        
        msg_final = self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[2]/div/div').text
        
        print(P("Renegociação registrada com sucesso!", color='green'))
        Informativo().register(text="Renegociação registrada com sucesso!", color='<django:green>')
        
        return msg_final

        
    def __select(self, *, select_id:str, target:str, sep:str='_o_', timeout:int=100):
        self._find_element(By.ID, select_id).click()
        sleep(0.5)
        for num in range(1,timeout):
            option_id = f'{select_id}{sep}{num}'
            try:
                if self._find_element(By.ID, option_id, timeout=1).text == target:
                    self._find_element(By.ID, option_id, timeout=1).click()
                    return
            except:
                break

    @verify_login
    def teste(self):
        self.__load_page('CalculoMensal/Cobranca')
        
        
        
if __name__ == '__main__':
    pass
