# Voice Shopping List

Um **bot do Telegram** que recebe áudios para anotar compras e salva como tabela no **Google Planilhas** ou **Anytype**.

---

## Como funciona

1. O áudio é convertido para texto usando `faster_whisper`
2. O texto é enviado para uma LLM via **Groq**
3. A LLM organiza os dados em formato JSON
4. Os dados são salvos no **Anytype** ou no **Google Planilhas** como tabela

O bot possui filtro de `user_id` para não processar mensagens de outros usuários do Telegram.

---

## Setup

1. Instale as dependências:

```bash
poetry install
```

2. Renomeie o `.env-example` para `.env` e adicione as chaves de API do:
   - Groq  
   - Telegram  
   - Anytype (opcional)  
   - Google Planilhas (opcional)

3. Opcional: Inicie o Anytype localmente (ou em um servidor, ajustando o `.env`)

4. Execute o projeto:

```bash
poetry run python main.py
```

5. Envie um áudio para o bot no Telegram para testar.

---

## Observações

- É necessário registrar o bot no Telegram.
- O modelo utilizado é `llama-3.1-8b-instant` (plano free do Groq), podendo ser alterado em `groq_service.py`.
- Caso o `WHISPER_MODEL` não seja definido em `.env`, será utilizado o modelo `whisper-large-v3-turbo` pelo Groq, no plano free.
- O prompt pode ser alterado em `ai_context.py`.

---

## Opcional: Setup Anytype

- Manter o Anytype rodando localmente ou em um servidor
- Ajustar as variáveis no `.env`

---

## Opcional: Setup Google Planilhas

- Criar um projeto no Google Cloud  
- Criar uma Service Account  
- Gerar uma chave JSON para a Service Account  
- Salvar o arquivo como `service_account.json` na raiz do projeto  
- Ativar a Google Sheets API  
- Compartilhar a planilha com o e-mail da Service Account (permissão de Editor)  
- Definir as variáveis no `.env` conforme o `.env-example`