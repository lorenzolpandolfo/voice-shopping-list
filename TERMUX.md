# Rodando o projeto no Termux pelo Proot Distro com Ubuntu

Para rodar o projeto em um servidor mobile que roda pelo Termux, siga os passos abaixo.

___

# Instalação automatizada

No Termux, rode o comando para iniciar o instalador:

```
curl -fsSL https://raw.githubusercontent.com/lorenzolpandolfo/voice-shopping-list/main/install-termux.sh | bash
```

E aguarde a instalação finalizar.

---

# Etapas manuais

Caso preferir ou o script automatizado apresentar problemas, siga as etapas manuais abaixo:

# 1. Preparar Termux

Atualizar os pacotes do Termux, instalar o **proot-distro** e **tmux**:

```
pkg update && pkg upgrade -y
pkg install proot-distro tmux -y
```

# 2. Instalar Ubuntu

No termux, execute os passos abaixo para instalar o Ubuntu e inicializá-lo:

```
proot-distro install ubuntu
proot-distro login ubuntu
```

# 3. Preparar Ubuntu

Dentro do Ubuntu, execute:


```
apt update && apt upgrade -y
apt install git build-essential python3-venv python3-pip curl pkg-config libssl-dev -y
```

# 4. Opcional: Atualizar Rust

Esta etapa é opcional e deve ser executada caso ocorram erros ao compilar algumas dependências. É recomendado pular essa etapa se não for necessário.

Dentro do Ubuntu, execute:


```
apt remove rustc cargo -y
curl https://sh.rustup.rs -sSf | sh
source $HOME/.cargo/env
rustc --version   # >=1.88
cargo --version
```

# 5. Clonar o projeto, Configurar Python e Poetry

Dentro do Ubuntu, execute:

```
git clone https://github.com/lorenzolpandolfo/voice-shopping-list

cd voice-shopping-list/

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install poetry

poetry install
```

# 6. Criar script de start do bot (start_inside_ubuntu.sh)

Este script fica dentro do Ubuntu, e serve para facilitar a inicialização do projeto.

```
#!/bin/bash
cd /root/voice-shopping-list
if [ ! -d venv ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install poetry
    poetry install --without dev
else
    source venv/bin/activate
fi
poetry run python main.py
```

# 7. Criar script de start do bot via Termux (start_voice_bot.sh)

Este script fica no termux, fora do Ubuntu e do tmux, e serve para facilitar a inicialização do projeto. Ele cria uma sessão no tmux e, dentro dela, inicia o Ubuntu. Dentro do Ubuntu, roda o script acima (`start_inside_ubuntu.sh`).

```
#!/data/data/com.termux/files/usr/bin/bash
SESSION_NAME="voice_bot"
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Sessão '$SESSION_NAME' já está rodando"
else
    tmux new-session -d -s "$SESSION_NAME" "proot-distro login ubuntu -- bash -c './start_inside_ubuntu.sh; exec bash'"
    echo "Sessão '$SESSION_NAME' criada"
fi
echo "Para checar logs: tmux attach -t $SESSION_NAME"
```

---

# Iniciar o bot
Para iniciar o bot, rode `./start_voice_bot.sh` dentro do Termux. Ele deve criar um tmux chamado `voice_bot` e que pode ser acessado com `tmux attach -t voice_bot`.

Então, dentro dessa sessão do **tmux**, está rodando o **Ubuntu**, que está rodando o projeto.

Não esqueça de definir as variáveis de ambiente e demais passos do README.md.

# Utilitários
- `tmux ls` para listar sessões do tmux
- `tmux attach -t voice_bot` para checar logs do bot
- `tmux kill-session -t voice_bot` para matar a sessão do bot

---

# Extra - script para checar se o bot está online rapidamente

```
#!/data/data/com.termux/files/usr/bin/bash

GREEN="\033[0;32m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo "[ Iniciando Verificação dos Serviços ]"
echo "> Data da verificação: $(date)"
echo ""

check_process() {
    local name="$1"
    local pattern="$2"

    if pgrep -f "$pattern" > /dev/null; then
        echo -e "[$name] ${GREEN}ONLINE${NC}"
    else
        echo -e "[$name] ${RED}OFFLINE${NC}"
    fi
}

# Exemplo com um server papermc e o playit
# check_process "Minecraft Server" "java.*paper.jar"
# check_process "Playit" "playit"

check_process "Voice Bot" "voice-shopping-list/venv/bin/python main.py"

```

# Extra - cronjob

É possível definir um cronjob para que o `voice_bot` inicie periodicamente:

```
crontab -e
```

e defina:
```
0 */1 * * * ~/start_voice_bot.sh
```

Assim a cada 1h, todos os dias, o script de inicialização do bot será executado.

