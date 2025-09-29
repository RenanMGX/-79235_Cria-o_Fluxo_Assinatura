import requests
import json
from datetime import datetime
import os
import dotenv; dotenv.load_dotenv()
import webbrowser
from urllib.parse import urlencode

class OutlookEmailReader:
    def __init__(self, client_id, client_secret, tenant_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.access_token = None
        self.base_url = "https://graph.microsoft.com/v1.0"
        
    def authenticate(self):
        """Autentica usando Client Credentials Flow (aplicação)"""
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            print("✅ Autenticação realizada com sucesso!")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na autenticação: {e}")
            return False
    
    def get_headers(self):
        """Retorna headers para requisições autenticadas"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def list_emails(self, email_address, count=10, filter_unread=False):
        """Lista emails da caixa de entrada"""
        if not self.access_token:
            print("❌ Necessário autenticar primeiro!")
            return None
        
        # URL para acessar emails do usuário específico
        url = f"{self.base_url}/users/{email_address}/messages"
        
        # Parâmetros da consulta
        params = {
            '$top': count,
            '$orderby': 'receivedDateTime desc',
            '$select': 'id,subject,from,receivedDateTime,isRead,hasAttachments,bodyPreview'
        }
        
        if filter_unread:
            params['$filter'] = 'isRead eq false'
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            if response.status_code != 200:
                response.raise_for_status()
            
            emails_data = response.json()
            return emails_data.get('value', [])
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao listar emails: {e}")
            return None
    
    def read_email(self, email_address, email_id):
        """Lê um email específico pelo ID"""
        if not self.access_token:
            print("❌ Necessário autenticar primeiro!")
            return None
        
        url = f"{self.base_url}/users/{email_address}/messages/{email_id}"
        
        params = {
            '$select': 'id,subject,from,toRecipients,ccRecipients,receivedDateTime,isRead,hasAttachments,body,attachments'
        }
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            
            email_data = response.json()
            return email_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao ler email: {e}")
            return None
    
    def display_email_list(self, emails):
        """Exibe lista de emails formatada"""
        if not emails:
            print("📭 Nenhum email encontrado.")
            return
        
        print(f"\n📧 Encontrados {len(emails)} emails:")
        print("=" * 80)
        
        for i, email in enumerate(emails, 1):
            status = "📩" if not email['isRead'] else "📨"
            attachments = "📎" if email.get('hasAttachments', False) else "  "
            
            from_email = email['from']['emailAddress']['address'] if email.get('from') else "Desconhecido"
            from_name = email['from']['emailAddress']['name'] if email.get('from') else "Desconhecido"
            
            received_date = datetime.fromisoformat(email['receivedDateTime'].replace('Z', '+00:00'))
            date_str = received_date.strftime("%d/%m/%Y %H:%M")
            
            print(f"{i:2d}. {status} {attachments} [{date_str}]")
            print(f"    De: {from_name} <{from_email}>")
            print(f"    Assunto: {email['subject']}")
            print(f"    Preview: {email.get('bodyPreview', '')[:100]}...")
            print(f"    ID: {email['id']}")
            print("-" * 80)
    
    def display_email_content(self, email_data):
        """Exibe conteúdo completo do email"""
        if not email_data:
            print("❌ Email não encontrado.")
            return
        
        print("\n" + "=" * 80)
        print("📧 DETALHES DO EMAIL")
        print("=" * 80)
        
        # Informações básicas
        from_info = email_data.get('from', {}).get('emailAddress', {})
        print(f"De: {from_info.get('name', 'N/A')} <{from_info.get('address', 'N/A')}>")
        
        # Destinatários
        to_recipients = email_data.get('toRecipients', [])
        if to_recipients:
            to_list = [f"{r['emailAddress']['name']} <{r['emailAddress']['address']}>" for r in to_recipients]
            print(f"Para: {', '.join(to_list)}")
        
        # CC se houver
        cc_recipients = email_data.get('ccRecipients', [])
        if cc_recipients:
            cc_list = [f"{r['emailAddress']['name']} <{r['emailAddress']['address']}>" for r in cc_recipients]
            print(f"CC: {', '.join(cc_list)}")
        
        print(f"Assunto: {email_data.get('subject', 'Sem assunto')}")
        
        received_date = datetime.fromisoformat(email_data['receivedDateTime'].replace('Z', '+00:00'))
        print(f"Data: {received_date.strftime('%d/%m/%Y às %H:%M:%S')}")
        
        print(f"Status: {'Não lido' if not email_data.get('isRead', True) else 'Lido'}")
        print(f"Anexos: {'Sim' if email_data.get('hasAttachments', False) else 'Não'}")
        
        print("\n" + "-" * 80)
        print("CONTEÚDO:")
        print("-" * 80)
        
        # Corpo do email
        body = email_data.get('body', {})
        content_type = body.get('contentType', 'text')
        content = body.get('content', 'Sem conteúdo')
        
        if content_type == 'html':
            # Remover tags HTML básicas para exibição
            import re
            content = re.sub('<[^<]+?>', '', content)
            content = content.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
        
        print(content)
        print("=" * 80)
    
    def authorize_user(self, redirect_uri):
        """Abre a URL de autorização para o usuário conceder permissões"""
        auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"

        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'response_mode': 'query',
            'scope': 'https://graph.microsoft.com/Mail.Read',
            'state': '12345'  # Opcional, para rastrear a solicitação
        }

        # Construir a URL de autorização
        full_url = f"{auth_url}?{urlencode(params)}"

        print("🌐 Abrindo o navegador para autenticação...")
        webbrowser.open(full_url)
        print("🔗 Após conceder as permissões, copie o código da URL de redirecionamento.")

    def exchange_code_for_token(self, code, redirect_uri):
        """Troca o código de autorização por um token de acesso"""
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'scope': 'https://graph.microsoft.com/Mail.Read'
        }

        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data['access_token']
            print("✅ Token de acesso obtido com sucesso!")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao trocar o código por token: {e}")
            return False

def main():
    """Função principal - exemplo de uso"""
    
    # ⚠️ CONFIGURAÇÃO NECESSÁRIA ⚠️
    # Você precisa registrar uma aplicação no Azure AD e obter essas informações
    CLIENT_ID = os.getenv("CLIENT_ID")  # "seu-client-id-aqui"
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")  # "seu-client-secret-aqui"
    TENANT_ID = os.getenv("TENANT_ID")  # "seu-tenant-id-aqui"
    EMAIL_ADDRESS = "rpa@patrimar.com.br"  # "rpa@patrimar.com.br"

    # Verificar se as configurações foram preenchidas
    if CLIENT_ID == "seu-client-id-aqui":
        print("❌ ERRO: Você precisa configurar as credenciais da aplicação Azure AD!")
        print("\nPara configurar:")
        print("1. Acesse https://portal.azure.com")
        print("2. Vá para 'Azure Active Directory' > 'App registrations'")
        print("3. Clique em 'New registration'")
        print("4. Registre sua aplicação")
        print("5. Obtenha CLIENT_ID, CLIENT_SECRET e TENANT_ID")
        print("6. Configure as permissões necessárias (Mail.Read, Mail.ReadWrite)")
        return
    
    # Inicializar o leitor de email
    email_reader = OutlookEmailReader(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
    
    # Autenticar
    if not email_reader.authenticate():
        return
    
    print(f"\n🔍 Buscando emails para: {EMAIL_ADDRESS}")
    
    # Listar emails recentes
    emails = email_reader.list_emails(EMAIL_ADDRESS, count=5)
    
    if emails:
        email_reader.display_email_list(emails)
        
        # Perguntar qual email ler
        try:
            choice = input("\nDigite o número do email que deseja ler (ou Enter para sair): ")
            if choice.strip():
                index = int(choice) - 1
                if 0 <= index < len(emails):
                    selected_email = emails[index]
                    
                    print(f"\n📖 Lendo email: {selected_email['subject']}")
                    
                    # Ler email completo
                    full_email = email_reader.read_email(EMAIL_ADDRESS, selected_email['id'])
                    email_reader.display_email_content(full_email)
                else:
                    print("❌ Número inválido!")
        except ValueError:
            print("❌ Por favor, digite um número válido!")
        except KeyboardInterrupt:
            print("\n👋 Saindo...")

if __name__ == "__main__":
    main()

