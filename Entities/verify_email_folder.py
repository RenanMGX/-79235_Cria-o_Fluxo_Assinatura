import os
from datetime import datetime


class VerifyEmailFolder:
    @property
    def path(self) -> str:
        return self.__path
    
    @property
    def lista_arquivos(self) -> list:
        if not self.__lista_arquivos:
            self.get_all_files()
        return self.__lista_arquivos
    
    def __init__(self, path:str) -> None:
        if not os.path.isdir(path):
            raise Exception("Path is not a directory")
        if not os.path.exists(path):
            raise Exception("Path does not exist")
        
        self.__path:str = path
        self.__lista_arquivos = []
        
    def get_all_files(self):
        lista_arquivos = []
        for root, dirs, files in os.walk(self.path):
            for file in files:
                full_path = os.path.join(root, file)
                lista_arquivos.append(full_path)
                
        self.__lista_arquivos = lista_arquivos
        return self
    
    def get_recent_email(self) -> str:
        if self.lista_arquivos:
            last:datetime = datetime(1900, 1, 1)
            for file in self.lista_arquivos:
                file_time = datetime.fromtimestamp(os.path.getmtime(file))
                if (file_time > last) and (file):
                    last = file_time
                    fime_time = file
                
                print(fime_time)


    
    
    
if __name__ == "__main__":
    from patrimar_dependencies.sharepointfolder import SharePointFolders
    
    bot = VerifyEmailFolder(SharePointFolders(r'RPA - Dados\Emails em Texto').value)
    
    print(bot.get_recent_email())
    
    
    