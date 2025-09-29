import os
import dotenv; dotenv.load_dotenv()
from Entities.navegador import Navegador
from botcity.maestro import * #type: ignore


maestro = BotMaestroSDK.from_sys_args()
try:
    execution = maestro.get_execution()
except Exception as e:
    maestro = None

class ExecuteAPP:
    @staticmethod
    def __execute_in_loop(*, bot: Navegador, param:str):
        while bot.assinar_contrato(param):
            print(f"Assinado com sucesso!")
    
    @staticmethod
    def start(
        *,
        email:str,
        password:str,
        name_docs:list,
        manual_login:bool=False
    ):
        
        
        nav = Navegador(
            email=email,
            password=password,
        )
        
        if manual_login:
            nav.manual_login()
            return      
        
        for doc in name_docs:
            try:
                ExecuteAPP.__execute_in_loop(bot=nav, param=doc)
            except Exception as e:
                if not maestro is None:
                    maestro.error(task_id=int(execution.task_id), exception=e)
                print(f"Erro ao assinar {doc}: {e}")
                

        
if __name__ == "__main__":
    from patrimar_dependencies.credenciais_botcity import CredentialBotCity
    crd = CredentialBotCity(
        login=os.getenv("BOTCITY_LOGIN"),#type: ignore
        key=os.getenv("BOTCITY_KEY") #type: ignore
    ).get_credential(label="CFO")
    
    bot = ExecuteAPP.start(
        #email=crd['email'],
        #password=crd["password"],
        email=os.getenv("EMAIL"),#type: ignore
        password=os.getenv("PASSWORD"),#type: ignore
    )
    