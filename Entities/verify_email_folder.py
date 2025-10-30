import os
import shutil
from datetime import datetime
import re
from dateutil.relativedelta import relativedelta
import pandas as pd

class VerifyEmailFolder:
    @property
    def base_folder(self) -> str:
        return self.__base_folder
    
    @property
    def files_origin(self) -> list:
        return [os.path.join(self.base_folder, f) for f in  os.listdir(self.base_folder)]
    
    def __init__(self, base_folder:str) -> None:
        if not os.path.isdir(base_folder):
            raise ValueError("O caminho informado não é uma pasta válida.")
        if not os.path.exists(base_folder):
            raise ValueError("O caminho informado não existe.")
        
        self.__base_folder = base_folder
        self._sanitize_folder(self.base_folder)

    @staticmethod
    def _sanitize_folder(base_folder) -> str:
        arquivos = {
            'name':[],
            'date':[],
            'file_path':[],
        }
        for file in os.listdir(base_folder):
            file_path = os.path.join(base_folder, file)
            if os.path.isdir(file_path):
                print("Removendo pasta:", file_path)
                continue
            if not file.lower().endswith('.csv'):
                print("Removendo arquivo inválido:", file_path)
                continue
                
            arquivos['file_path'].append(file_path)
            date_str = re.search(r'\d{2}-\d{2}-\d{4}', file)
            hour_str = re.search(r'\d{2}-\d{2} \D{2}', file)
            if date_str and hour_str:
                date_str = date_str.group(0)
                pm = False
                if "PM" in hour_str.group(0).upper():
                    pm = True
                
                date_union = date_str + ' ' + hour_str.group(0).replace(' PM','').replace(' AM','').strip()
                date = datetime.strptime(date_union, '%d-%m-%Y %H-%M')
                if pm:
                    date = date + relativedelta(hours=12)
                arquivos['date'].append(date)
                arquivos['name'].append(file.split(" ")[0])
            else:
                print("Removendo arquivo com nome inválido:", file_path)
                continue
        
        files_to_save = []
        df = pd.DataFrame(arquivos)
        #print(df)
        
        list_files = df['name'].to_list()
        for file_name in list_files:
            df_file = df[df['name'] == file_name]
            files_to_save.append(df_file.nlargest(1, 'date')['file_path'].values[0])
        
        for file in os.listdir(base_folder):
            file_path = os.path.join(base_folder, file)
            if file_path in files_to_save:
                continue
            else:
                print("Removendo arquivo antigo:", file_path)
                os.remove(file_path)
        return "arquivos"
    
    
    
if __name__ == "__main__":
    from patrimar_dependencies.sharepointfolder import SharePointFolders
    
    bot = VerifyEmailFolder(SharePointFolders(r'RPA - Dados\Relatorios\Controle SAP ORACLE UNIFIER\ALL_FILES_FROM_EMAIL').value)
    
    for f in bot.files_origin:
        if "ORC-EX_Detalhado-Material" in f:
            rec_orc_ex = SharePointFolders(r'RPA - Dados\Relatorios\Controle SAP ORACLE UNIFIER\rec_orc_ex').value
            shutil.copy2(f, rec_orc_ex)
            os.remove(f)
            bot._sanitize_folder(rec_orc_ex)
        elif "ORC-PL_Detalhado-Material" in f:
            rec_orc_pl = SharePointFolders(r'RPA - Dados\Relatorios\Controle SAP ORACLE UNIFIER\rec_orc_pl').value
            shutil.copy2(f, rec_orc_pl)
            os.remove(f)
            bot._sanitize_folder(rec_orc_pl)
        elif "REC-ORC_Unifier" in f:
            rec_orc_unifier = SharePointFolders(r'RPA - Dados\Relatorios\Controle SAP ORACLE UNIFIER\rec_orc_unifier').value
            shutil.copy2(f, rec_orc_unifier)
            os.remove(f)
            bot._sanitize_folder(rec_orc_unifier)

    #bot._sanitize_folder()
    #print(bot.files_origin)
    
    