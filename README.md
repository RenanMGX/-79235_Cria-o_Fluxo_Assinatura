# Fluxo de Assinatura Automática

Este projeto é uma automação para realizar assinaturas de documentos utilizando a integração com serviços como o Microsoft Graph API e DocuSign. Ele foi desenvolvido para facilitar o processo de assinatura de contratos e outros documentos de forma automatizada.

## Estrutura do Projeto

Abaixo está a estrutura principal do projeto:

```
#material/                # Contém materiais de apoio, como imagens e documentos.
Entities/                # Contém as classes principais para integração e automação.
    email_acess.py       # Classe para integração com o Microsoft Graph API.
    navegador.py         # Classe para automação de navegação no DocuSign.
resources/               # Recursos adicionais, como imagens para a automação.
bot.py                   # Script principal para integração com o BotCity Maestro.
main.py                  # Script principal para execução da automação.
requirements.txt         # Lista de dependências do projeto.
```

## Pré-requisitos

1. **Python 3.10 ou superior**
2. **Dependências do projeto**:
   - Instale as dependências utilizando o comando:
     ```bash
     pip install -r requirements.txt
     ```
3. **Configuração do Azure AD**:
   - Registre uma aplicação no Azure AD para obter as credenciais necessárias (CLIENT_ID, CLIENT_SECRET, TENANT_ID).
   - Conceda permissões como `Mail.Read` e `Mail.ReadWrite` para o Microsoft Graph API.

4. **Configuração do DocuSign**:
   - Certifique-se de que as credenciais de login para o DocuSign estão configuradas corretamente.

## Configuração

1. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

   ```env
   CLIENT_ID=seu-client-id
   CLIENT_SECRET=seu-client-secret
   TENANT_ID=seu-tenant-id
   EMAIL=seu-email
   PASSWORD=sua-senha
   BOTCITY_LOGIN=seu-login-botcity
   BOTCITY_KEY=sua-chave-botcity
   ```

2. Certifique-se de que as credenciais estão corretas e que o aplicativo no Azure AD possui as permissões necessárias.

## Como Executar

### 1. Fluxo de Assinatura Automática

Execute o script `main.py` para iniciar o processo de assinatura automática:

```bash
python main.py
```

### 2. Autenticação Interativa

Caso precise de autenticação interativa para o Microsoft Graph API, utilize os métodos adicionados no `email_acess.py`:

- **`authorize_user`**: Abre o navegador para o usuário conceder permissões.
- **`exchange_code_for_token`**: Troca o código de autorização por um token de acesso.

### 3. Automação de Navegação

A classe `Navegador` em `navegador.py` é responsável por realizar a automação no DocuSign. Certifique-se de que as credenciais estão configuradas corretamente.

## Dependências

As principais dependências do projeto incluem:

- `requests`: Para integração com APIs.
- `selenium`: Para automação de navegação.
- `botcity-maestro-sdk`: Para integração com o BotCity Maestro.
- `python-dotenv`: Para gerenciamento de variáveis de ambiente.

Consulte o arquivo `requirements.txt` para a lista completa.

## Contribuição

1. Faça um fork do repositório.
2. Crie uma branch para sua feature ou correção:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça commit das suas alterações:
   ```bash
   git commit -m "Minha nova feature"
   ```
4. Envie para o repositório remoto:
   ```bash
   git push origin minha-feature
   ```
5. Abra um Pull Request.

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo `LICENSE` para mais informações.