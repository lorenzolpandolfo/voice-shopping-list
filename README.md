# Voice Shopping List


Um **bot do Telegram** que recebe áudios para anotar compras e salva como tabela no Anytype.


## Como funciona
O áudio é convertido para texto utilizando o `faster_whisper`, enviado para uma LLM utilizando o **Groq**, para organização dos dados em JSON, e por fim, salvo no **Anytype**, em formato de tabela.

O bot contém um filtro de `user_id` para não processar respostas de outros.

## Setup

- Instale as dependências:
    ```bash
    poetry install
    ```

- Renomeie o `.env-example` e adicione as api keys do **Groq**, **Anytype** e **Telegram**.

- Inicie o Anytype localmente (ou em um servidor, contanto que ajuste no `.env`)

- Por fim, rode o projeto:
    ```bash
    poetry run python main.py
    ```
- Para testar, envie um áudio ao bot no telegram.

## Observações extras

- É necessário fazer o registro do BOT pelo Telegram
- É preciso estar com o Anytype rodando localmente (ou em um servidor)
- O modelo de linguagem utilizado é o `llama-3.1-8b-instant`, com o plano free do Groq, mas pode ser alterado em `groq_service.py`
- O prompt do modelo pode ser alterado em `ai_context.py`