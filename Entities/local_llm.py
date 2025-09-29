import requests
import json
from typing import Literal, Dict

class LocalLLM:
    host:str = "patrimartp117"
    headersList = {
        "Content-Type": "application/json"
    }
    temperature:float|None = None
    top_p:float|None = None
    seed:int|None = None
    num_predict:int|None = None
    
    @staticmethod
    def __tratar_response(response:requests.Response, raw_return:bool, name_response:Literal["response", "message"]):
        if response.status_code == 200:
            result = []
            for line in response.iter_lines():
                json_result = json.loads(
                    line.decode('utf-8')
                )
                json_result['status_code'] = response.status_code
                    
                result.append(
                    json_result
                )
            if raw_return:
                return result
            
            if name_response == 'response':
                return {
                    "response": "".join([r["response"] for r in result if not r['done']]),
                    "model": result[0]['model'],
                    "created_at": result[-2]['created_at'],
                    "status_code": result[0]['status_code']
                }
            elif name_response == 'message':
                return {
                    "message": {"role": "assistant", "content": "".join([x['message']['content'] for x in result if not x['done']])},
                    "model": result[0]['model'],
                    "created_at": result[-2]['created_at'],
                    "status_code": result[0]['status_code']
                }
            
        else:
            return response
            
    
    @staticmethod
    def generative(
        prompt:str,
        *,
        model:str|Literal[
            "deepseek-r1:1.5b",
            "deepseek-r1:8b",
            "deepseek-r1:32b",
            "llama3.2:1b",
            "llama3.2:3b",
            "llama3.2:8b",
            "gpt-oss:20b"         
        ],
        raw_return:bool=False
    ):
        
        reqUrl = f"http://{LocalLLM.host}:11434/api/generate"
        
        dados:Dict[str, object] = {
            "model": model,
            "prompt": prompt,
        }
        dados['temperature'] = LocalLLM.temperature if LocalLLM.temperature is not None else None 
        dados['top_p'] = LocalLLM.top_p if LocalLLM.top_p is not None else None
        dados['seed'] = LocalLLM.seed if LocalLLM.seed is not None else None
        dados['num_predict'] = LocalLLM.num_predict if LocalLLM.num_predict is not None else None
        
        
        
        payload = json.dumps(dados)
        
        response = requests.request("POST", reqUrl, data=payload, headers=LocalLLM.headersList)
        
        return LocalLLM.__tratar_response(response, raw_return, 'response')
        
    @staticmethod
    def chat(
        prompt:str,
        *,
        system:str="Você é um assistente útil.",
        model:str|Literal[
            "deepseek-r1:1.5b",
            "deepseek-r1:8b",
            "deepseek-r1:32b",
            "llama3.2:1b",
            "llama3.2:3b",
            "llama3.2:8b",
            "gpt-oss:20b"         
        ],
        raw_return:bool=False,
        messages:list[dict]|None=None,
    ):
        
        reqUrl = f"http://{LocalLLM.host}:11434/api/chat"
        
        if messages is not None:
            final_messages = messages
            final_messages.append(
                {"role": "user", "content": prompt}
            )
        else:
            final_messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
            
        dados = {
            "model": model,
            "messages": final_messages
        }
        dados['temperature'] = LocalLLM.temperature if LocalLLM.temperature is not None else None
        dados['top_p'] = LocalLLM.top_p if LocalLLM.top_p is not None else None
        dados['seed'] = LocalLLM.seed if LocalLLM.seed is not None else None
        dados['num_predict'] = LocalLLM.num_predict if LocalLLM.num_predict is not None else None
                
        payload = json.dumps(dados)

        response = requests.request("POST", reqUrl, data=payload, headers=LocalLLM.headersList)
        
        return LocalLLM.__tratar_response(response, raw_return, 'message')
        
    @staticmethod
    def image(
        *,
        img:str,
        prompt:str="O que há nessa imagem?",
        model:str|Literal[
            "llava-llama3:8b",  
            "llava:7b",
            "gemma3:4b",
            "gemma3:12b",
        ],
        raw_return:bool=False,
    ):
        
        reqUrl = f"http://{LocalLLM.host}:11434/api/generate"
        
        dados = {
            "model": model,
            "prompt": prompt,
            "images": [img]
        }
        dados['temperature'] = LocalLLM.temperature if LocalLLM.temperature is not None else None
        dados['top_p'] = LocalLLM.top_p if LocalLLM.top_p is not None else None
        dados['seed'] = LocalLLM.seed if LocalLLM.seed is not None else None
        dados['num_predict'] = LocalLLM.num_predict if LocalLLM.num_predict is not None else None
        

        payload = json.dumps(dados)
        
        response = requests.request("POST", reqUrl, data=payload, headers=LocalLLM.headersList)
        
        return LocalLLM.__tratar_response(response, raw_return, 'response')
        
        
        
if __name__ == "__main__":
    import base64

    # Carregar imagem em base64
    with open(r"#material\Screenshot_6.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")    
    
    LocalLLM.seed = 123
    LocalLLM.temperature = 0.0
    LocalLLM.top_p = 1.0
    LocalLLM.num_predict = 512
    result = LocalLLM.image(
        model='gemma3:4b',
        img=img_b64,
        raw_return=False
    )
    
    #import pdb; pdb.set_trace()
    print(result)
        
        














