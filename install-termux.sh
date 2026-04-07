#!/data/data/com.termux/files/usr/bin/bash

set -e

REPO_URL="https://github.com/lorenzolpandolfo/voice-shopping-list"
PROJECT_NAME="voice-shopping-list"
SESSION_NAME="voice_bot"

quiet() {
  "$@" > /dev/null
}

echo "Etapa 1/6 - Preparando Termux"
quiet pkg update -y
quiet pkg install proot-distro tmux -y

echo "Etapa 2/6 - Garantindo Ubuntu"
if ! proot-distro list | grep -q ubuntu; then
  quiet proot-distro install ubuntu
fi

echo "Etapa 3/6 - Preparando Ubuntu"
proot-distro login ubuntu -- bash -c "
set -e
apt update -y > /dev/null
apt install git build-essential python3-venv python3-pip curl pkg-config libssl-dev -y > /dev/null
"

echo "Etapa 4/6 - Projeto e dependências"
proot-distro login ubuntu -- bash -c "
set -e

if [ ! -d ~/$PROJECT_NAME ]; then
  git clone $REPO_URL > /dev/null
fi

cd ~/$PROJECT_NAME

if [ ! -d venv ]; then
  python3 -m venv venv
fi

source venv/bin/activate

if ! command -v poetry > /dev/null 2>&1; then
  pip install --upgrade pip > /dev/null
  pip install poetry > /dev/null
fi

if [ ! -f poetry.lock ] || [ ! -d .venv ]; then
  poetry install --without dev > /dev/null
fi
"

echo "Etapa 5/6 - Script interno"
proot-distro login ubuntu -- bash -c "
if [ ! -f ~/start_inside_ubuntu.sh ]; then
cat > ~/start_inside_ubuntu.sh << 'EOF'
#!/bin/bash
set -e
cd ~/voice-shopping-list
source venv/bin/activate
poetry run python main.py
EOF
chmod +x ~/start_inside_ubuntu.sh
fi
"

echo "Etapa 6/6 - Script de start"
if [ ! -f ~/start_voice_bot.sh ]; then
cat > ~/start_voice_bot.sh << EOF
#!/data/data/com.termux/files/usr/bin/bash
SESSION_NAME="$SESSION_NAME"

if tmux has-session -t "\$SESSION_NAME" 2>/dev/null; then
  echo "Sessão '\$SESSION_NAME' já está rodando"
else
  tmux new-session -d -s "\$SESSION_NAME" "proot-distro login ubuntu -- bash -c '~/start_inside_ubuntu.sh; exec bash'"
  echo "Sessão '\$SESSION_NAME' criada"
fi

echo "Para ver logs: tmux attach -t \$SESSION_NAME"
EOF
chmod +x ~/start_voice_bot.sh
fi

echo ""
echo "Instalação concluída."
echo "Execute: ./start_voice_bot.sh"