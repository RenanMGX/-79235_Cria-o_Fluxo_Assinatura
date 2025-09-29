from patrimar_dependencies.navegador_chrome import NavegadorChrome, By, Keys, WebElement, Select
from patrimar_dependencies.functions import P
from time import sleep
from typing import Literal, List, Dict
from functools import wraps
import os
import requests
from Entities.local_llm import LocalLLM
import base64
from botcity.maestro import * #type: ignore

maestro = BotMaestroSDK.from_sys_args()
try:
    execution = maestro.get_execution()
except Exception as e:
    maestro = None



class Navegador(NavegadorChrome):
    @property
    def url_base(self):
        return "https://apps.docusign.com/"
        
    @staticmethod
    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            self:Navegador = args[0]
            sleep(2)

            html = self.find_element(By.XPATH, 'html')
            if "Log in to Docusign" in html.text:
                self._login()
                sleep(2)
            
            return f(*args, **kwargs)
        return wrap
    
    def __site_wait(self, sleep_time:float|int=1):
        sleep(sleep_time)
        while True:
            if 'Carregando...' in self.find_element(By.XPATH, 'html').text:
                continue
            else:
                return
    
    def __init__(self, *, email:str|None, password:str|None, save_user=True, headless=False, anonymous=False):
        if email is None or password is None:
            raise Exception("Email and password are required")
        
        self.email = email
        self.password = password
        super().__init__(save_user=save_user, headless=headless, anonymous=anonymous)

        #self.get("https://account.docusign.com")
        self.get(self.url_base)
        
        self.manual_login_param = False
        
    def _go_to(self, endpoint:str):
        while endpoint.startswith("\\"):
            endpoint = endpoint[1:]
        while endpoint.startswith("/"):
            endpoint = endpoint[1:]
        
        result = os.path.join(self.url_base, endpoint)
        result = result.replace("\\", "/")
        self.get(result)

    def _login(self):
        #import pdb;pdb.set_trace(header=1)
        
        html = self.find_element(By.XPATH, 'html')
        for input in html.find_elements(By.TAG_NAME, 'input'):
            if input.get_attribute('name') == 'email':
                input.send_keys(self.email)
                input.send_keys(Keys.ENTER)
                break
                    
        self.__site_wait(2)
                    
        html = self.find_element(By.XPATH, 'html')
        for input in html.find_elements(By.TAG_NAME, 'input'):
            if input.get_attribute('name') == 'password':
                input.send_keys(self.password)
                input.send_keys(Keys.ENTER)
                break
        
        self.__site_wait(2) 
        html = self.find_element(By.XPATH, 'html')
        if "Invalid email and / or password" in html.text:
            raise Exception("Invalid email and / or password")
        
        sleep(5)
        html = self.find_element(By.XPATH, 'html')
        if not "Boas-vindas".lower() in html.text.lower():
            if self.manual_login_param:
                #import pdb; pdb.set_trace(header="\n\n -------> Parada para login Manual <------- \n\n")
                print(P("\n\n -------> Parada para login Manual <------- \n\n", color="yellow"))
                while True:
                    try:
                        self.title
                    except:
                        break
                    sleep(1)
                    
            else:
                raise Exception(f"Falha ao Logar: \n{html.text}")
    
    @login_required        
    def assinar_contrato(
        self,
        nome_contrato:str|Literal[
            "Termo De Quitação", 
            "Termo De Confissão De Dívida",
            "Termo Aditivo"
        ]
    ) -> bool:
        self._go_to("send/documents")
        self.set_window_size(1920, 1080)      
        self.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div[1]/div[1]/div/div[3]/div/div[2]/button', force=True, timeout=3).click()

        #search_box = self.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/input')
        #sleep(3)
        search_box:None|WebElement = None
        for _ in range(10):
            for input in self.find_elements(By.TAG_NAME, 'input'):
                if input.get_attribute('placeholder') == 'Pesquisar caixa de entrada e pastas':
                    search_box = input
                    break
            self.__site_wait()
            if search_box is None:
                continue
            break
            
            
        if search_box is None:
            raise Exception("Search box not found")  

        sleep(1)
        while len(str(search_box.get_attribute('value'))) > 0: 
            search_box.send_keys(Keys.BACK_SPACE)
        
        sleep(1)
        search_box.send_keys(nome_contrato)
        search_box.send_keys(Keys.ENTER)

        for button in self.find_elements(By.TAG_NAME, 'button'):
            if button.text == 'Status':
                button.click()
                self.__site_wait(0.25)
                break
            
        for label in self.find_elements(By.TAG_NAME, 'label'):
            if label.text == 'Em andamento':
                label.click()
                self.__site_wait(0.25)
                break
        
        for button in self.find_elements(By.TAG_NAME, 'button'):
            if button.text == 'Aplicar':
                button.click()
                self.__site_wait(0.25)
                break
        
        self.__site_wait()
        #import pdb; pdb.set_trace()
        
        try:
            tbody = self.find_element(By.TAG_NAME, "tbody")
            self.__site_wait()
            tbody.text
        except:
            if not maestro is None:
                maestro.alert(
                    task_id=execution.task_id,
                    title=f"Contrato {nome_contrato}",
                    message="Nenhum contrato encontrado",
                    alert_type=AlertType.INFO
                )            
            print(P("Nenhum contrato encontrado", color="yellow"))
            return False

        
        error:Exception|None = None
        for _ in range(len(tbody.find_elements(By.TAG_NAME, "tr"))):
            self.__site_wait()
            try:
                tbody = self.find_element(By.TAG_NAME, "tbody")
            except:
                if not maestro is None:
                    maestro.alert(
                        task_id=execution.task_id,
                        title=f"Contrato {nome_contrato}",
                        message="Todos os contratos foram assinados",
                        alert_type=AlertType.INFO
                    )            
                print(P("Todos os contratos foram assinados", color="green"))
                return False
            
            contratos:List[WebElement] = tbody.find_elements(By.TAG_NAME, "tr")
            
            try:
                self.__assinar(contratos[_])
                return True
            except Exception as e:
                self.back()
                self.__site_wait(5)
                error = e
                continue
                    
        if error is not None:
            raise error
        
        print(P("Não foi possivel assinar nada", color="red"))   
        return False
                
        
    def __assinar(self, elemento:WebElement):
        self.__site_wait(2)
        for button in elemento.find_elements(By.TAG_NAME, "button"):
            if button.text == 'Assinar':
                button.click()
                self.__site_wait(2)
                break
        
        #import pdb;pdb.set_trace(header=3)   
            
        page_loaded = False
        for _ in range(60):
            html = self.find_element(By.XPATH, 'html')
            if "Revisar e continuar" in html.text:
                page_loaded = True
                break
            self.__site_wait()
        
        #import pdb;pdb.set_trace(header=4)   
          
        if not page_loaded:
            raise Exception("Page did not load")
        
        #return

        for button in self.find_elements(By.TAG_NAME, "button"):
            if 'Continuar' == button.text:
                button.click()
                self.__site_wait(2)
                break
        
        #import pdb;pdb.set_trace(header=5)   
        
        for button in self.find_elements(By.TAG_NAME, "button"):
                if button.text == 'Assinar\nExigido - ' or button.text == 'Rubricar\nExigido - ':
                    button.click()
                    self.__site_wait(2)
                    for button in self.find_elements(By.TAG_NAME, "button"):
                        if (button.text == 'USAR SALVAS') or (button.text == 'Adotar e assinar'):
                            button.click()
                            self.__site_wait(2)
                            break
        
               
        #self.get_window_size()  

        #import pdb;pdb.set_trace()   
        
        for button in self.find_elements(By.TAG_NAME, "button"):
            if button.text == 'Concluir':
                button.click()
                self.__site_wait(5)
                break
        

        #import pdb;pdb.set_trace(header=7)
        
        for button in self.find_elements(By.TAG_NAME, "button"):
            if button.text == 'Não, obrigado':
                button.click()
                self.__site_wait(5)
                break
        
    def manual_login(self):
        self.manual_login_param = True
        self._login()
        #import pdb; pdb.set_trace()
      
    @login_required                  
    def teste(self):
        self._go_to("send/documents")
        
        #import pdb;pdb.set_trace(header="2")
        
        src_img = self.find_elements(By.TAG_NAME, 'img')[0].get_attribute('src')
        
        self.execute_script("window.open(arguments[0]);", src_img)
        self.switch_to.window(self.window_handles[1])
        
        imagem_binaria = self.find_element(By.TAG_NAME, "img").screenshot_as_png

        self.close()
        self.switch_to.window(self.window_handles[0])
        
        LocalLLM.seed = 123
        LocalLLM.temperature = 0.0
        LocalLLM.top_p = 1.0
        LocalLLM.num_predict = 512
        img_b64 = base64.b64encode(imagem_binaria).decode("utf-8")
        LocalLLM.image(img=img_b64, model='gemma3:27b', prompt="Qual é o Titulo do Documento? Qual é o nome do Credor? Qual é o numero CNPJ do Credor? Qual o nome do Devedor? qual o sexo do devedor? qual estado civil do Devedor? qual o CPF ou CNPJ do Devedor?", raw_return=False)
        
        

if __name__ == "__main__":
    pass
        
