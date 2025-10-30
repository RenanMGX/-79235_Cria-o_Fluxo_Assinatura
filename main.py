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
            #anonymous=True
        )
        
        if manual_login:
            nav.manual_login()
            import pdb; pdb.set_trace(header="\n\n -------> Parada para login Manual <------- \n\n")
            return      
        
        count_error = 0 
        error = None
        for doc in name_docs:
            try:
                ExecuteAPP.__execute_in_loop(bot=nav, param=doc)
            except Exception as e:
                count_error += 1
                error = e
                if not maestro is None:
                    maestro.error(task_id=int(execution.task_id), exception=e)
                print(f"Erro ao assinar {doc}: {e}")
                
        if count_error >= len(name_docs):
            if not error is None:
                raise error
            raise Exception("Nenhum documento foi assinado.")
        
        print("Processo finalizado.")
                

        
if __name__ == "__main__":
    from patrimar_dependencies.credenciais_botcity import CredentialBotCity
    crd = CredentialBotCity(
        login=os.getenv("BOTCITY_LOGIN"),#type: ignore
        key=os.getenv("BOTCITY_KEY") #type: ignore
    ).get_credential(label="Analista")
    
    bot = ExecuteAPP.start(
        email=crd['email'],
        password=crd["password"],
        #email=os.getenv("EMAIL"), #type: ignore
        #password=os.getenv("PASSWORD"), #type: ignore
        name_docs=["TESTE"],
        manual_login=False
    )
    