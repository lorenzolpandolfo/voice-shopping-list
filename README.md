# Voice Shopping List

Um **bot do Telegram** que recebe áudios para anotar compras e salva como tabela no **Google Planilhas**.


# Setup

Abaixo segue um guia de como configurar o projeto.


## Criando um projeto do Google Cloud

É necessário criar um projeto no Google Cloud, para realizar o fluxo de autenticação de usuários

1. Crie um projeto gratuito no [Google Cloud](https://console.cloud.google.com/)
2. Em [API e serviços > Credentials > Criar credenciais > ID do cliente OAuth](https://console.cloud.google.com/apis/credentials) crie uma credencial do tipo **TVs e dispositivos de entrada limitados**.
3. Baixe o `client_secret.json` e cole-o no diretório raiz do projeto. Não compartilhe este arquivo com ninguém.
4. Acesse [Google Auth Platform > Público Alvo](https://console.cloud.google.com/auth/audience) e adicione em **Usuários de teste** os usuários que vão utilizar o bot.


## Criando a Google Planilha

1. Crie uma Google Planilha no seu [Google Drive](https://drive.google.com)
2. Copie o id da planilha e guarde-o. Será utilizado em seguida: `docs.google.com/spreadsheets/d/<id>/`


## Preparando o Ambiente

1. Renomeie o `.env-example` para `.env` 
2. Preencha os dados com as chaves de API do [Groq](https://groq.com/) e do [Telegram Bot](https://core.telegram.org/bots/tutorial#getting-ready)
3. Renomeie o `users_data_example.json` para `users_data.json` e preencha os dados:
   - `spreadsheet_id` com o id da Google Planilha
   - `spreadsheet_tab` com o nome da aba da planilha (no final da página, geralmente **Página1** por padrão, pode ser alterado)
   - `telegram_user_id` com o id do seu usuário no Telegram.
     - Para conferir, acesse o `@userinfobot` no Telegram e envie `/start`


# Iniciar o projeto

Para iniciar o projeto, rode:
```
poetry install --without dev
poetry run python main.py
```


# Autenticação do Google

Para autenticar-se utilizando a conta Google no bot, envie o comando `/auth` e realize o processo de autenticação.
