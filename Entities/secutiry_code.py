import os
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

class SecurityCode:
    @property
    def path(self) -> str:
        return self.__path
    
    def __init__(self, path:str):
        if not os.path.isdir(path):
            raise NotADirectoryError(f"The path {path} is not a valid directory.")
        if not os.path.exists(path):
            raise FileNotFoundError(f"The path {path} does not exist.")
        
        self.__path = path

    def list_files(self):
        try:
            files = os.listdir(self.__path)
            return [os.path.join(self.path, file) for file in files if file.endswith('.txt')]
        except Exception as e:
            print(f"An error occurred while listing files: {e}")
            return []
        
    def get_code(self):
        files = self.list_files()
        for file in files:
            #file_time = datetime.fromtimestamp(os.path.getmtime(file))

            body = ""
            with open(file, 'r', encoding='utf-8') as f:
                body = f.read()
            
            if (match:= re.search(r'[0-9]{6}', body)):
                return match.group()

            raise ValueError("No 6-digit code found in the file.")

        raise FileNotFoundError("No .txt files found in the directory.")
    
    def delete_files(self):
        files = self.list_files()
        for file in files:
            try:
                os.remove(file)
            except Exception as e:
                print(f"An error occurred while deleting file {file}: {e}")

if __name__ == "__main__":
    from patrimar_dependencies.sharepointfolder import SharePointFolders

    bot = SecurityCode(
        SharePointFolders(r'RPA - Dados\Configs\79235 - Assinaturas_docusing\Emails_Diretor')
    )
    #print(bot.delete_files())
    print(bot.get_code())
