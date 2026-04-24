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
from main import ExecuteAPP

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False #type: ignore

class Processos:
    @property
    def total(self) -> int:
        return self.__total
    
    @total.setter
    def total(self, value:int):
        if value >= 0:
            self.__total = value
        else:
            raise ValueError("Total deve ser um valor inteiro maior ou igual a zero.")
    
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
        manual_login_param = execution.parameters.get("manual_login")
        if not manual_login_param:
            manual_login = False
        else:
            manual_login = True if str(manual_login_param).lower() in ['true', '1', 'yes', 'y'] else False

        name_docs_param = execution.parameters.get("name_docs")
        if not name_docs_param:
            raise ValueError("Parâmetro 'name_docs' é obrigatório.")
        else:
            name_docs_param = str(name_docs_param)
            if "," in name_docs_param:
                name_docs = [doc.strip() for doc in name_docs_param.split(",")]
            else:
                name_docs = [name_docs_param]
                
            
        crd_param = execution.parameters.get("crd")
        if not isinstance(crd_param, str):
            raise ValueError("Parâmetro 'crd_param' deve ser uma string representando o label da credencial.")
        
        
        return ExecuteAPP.start(
            email=maestro.get_credential(label=crd_param, key="email"),
            password=maestro.get_credential(label=crd_param, key="password"),
            manual_login=manual_login,
            name_docs=name_docs
        )

if __name__ == '__main__':
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()
    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    task_name = execution.parameters.get('task_name')

    try:
        result = Execute.start()
        processados, falhas = result if result is not None else (0, 0)
        
        p = Processos(processados + falhas)
        p.add_processado(processados)
        
        status = AutomationTaskFinishStatus.FAILED if processados == 0 and falhas > 0 else AutomationTaskFinishStatus.SUCCESS
        message = f"Tarefa {task_name} finalizada com sucesso" if status == AutomationTaskFinishStatus.SUCCESS else f"Tarefa {task_name} finalizada com Error"
        
        maestro.finish_task(
                    task_id=execution.task_id,
                    status=status,
                    message=message,
                    total_items=p.total, # Número total de itens processados
                    processed_items=p.processados, # Número de itens processados com sucesso
                    failed_items=p.falhas # Número de itens processados com falha
        )
        
    except Exception as error:
        p = Processos(1)
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
