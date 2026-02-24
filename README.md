# Voice Shopping List

Um **bot do Telegram** que recebe áudios para anotar compras e salva como tabela no **Google Planilhas**.

---

# Setup

Abaixo segue um guia de como configurar o projeto.

## Configurando Google Cloud

### Criando um projeto do Google Cloud
1. Será necessário criar um projeto gratuíto no [Google Cloud](https://console.cloud.google.com/)

### Permitir criação de chave da Conta de Serviço
1. Acesse [IAM](https://console.cloud.google.com/iam-admin/iam)
2. Selecione no topo da página, ao lado direito de Google Cloud, a sua organização pessoal
   - A organização deve ter sido criada com o free-trial do Google Cloud. O nome é parecido com `seuemail-org`
   - Se não encontrar, tente clicar nos 3 pontinhos no canto direito da janela de selecionar projetos e escolha **IAM/Permissões**. Deve carregar a página de permissões da organização
3. Defina a permissão **Administrador da política da organização** no seu usuário
4. Em [Políticas da Organização](https://console.cloud.google.com/iam-admin/orgpolicies/list) use o filtro de flags com `iam.managed.disableServiceAccountKeyCreation` e desabilite a flag

### Criando a Conta de Serviço
1. Acesse [IAM > Contas de Serviço](https://console.cloud.google.com/iam-admin/serviceaccounts) e selecione o projeto
2. Clique em Criar conta de serviço, defina o nome e pule as etapas de **Permissão** e **Principais com acesso**
3. **Guarde o email da conta de serviço**, ele será utilizado depois, para dar acesso ao bot na sua Google Planilha
4. Em `Ações > Gerenciar chaves > Adicionar chave > Criar nova chave`, crie uma chave de acesso JSON. Não a compartilhe com ninguém!
5. Baixe o arquivo da chave e mova-o para o diretório `/accounts`


### Criando a Google Planilha
1. Crie uma Google Planilha no seu [Google Drive](drive.google.com) e copie o id: `docs.google.com/spreadsheets/d/<id>/`
2. Renomeie o `users_data_example.json` para `users_data.json` e preencha os dados:
   - `spreadsheet_id` com o id da planilha
   - `preadsheet_tab` com o nome da aba da planilha (no final da página, geralmente Página1 por padrão)
   - `service_account_path` com o caminho da chave de conta de serviço (em relação ao diretório em que o bot vai executar)
   - `telegram_user_id` com o id do seu usuário no Telegram.
     - Para conferir, acesse o `@userinfobot` e envie `/start`
3. Adicione acesso de Editor ao seu email da Conta de Serviço criada anteriormente
4. Ativar a [Google Sheets API](https://console.cloud.google.com/apis/api/sheets.googleapis.com) para o projeto



# Iniciar o projeto

Não esqueça de preencher as variáveis em `.env-example`

Para iniciar o projeto, rode:
```
poetry install --without dev
poetry run python main.py
```