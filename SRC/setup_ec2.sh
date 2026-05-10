#!/bin/bash
# =============================================================================
# Script de setup completo para nova EC2 — Lideranças Empáticas
# Ubuntu 22.04 LTS | t3.micro
# Executar como: bash setup_ec2.sh
# =============================================================================

set -e

echo "=========================================="
echo " SETUP EC2 — Lideranças Empáticas"
echo "=========================================="

# =============================================================================
# 1. SISTEMA E DEPENDÊNCIAS
# =============================================================================
echo ""
echo "[1/7] Atualizando sistema..."
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y \
    git \
    curl \
    wget \
    htop \
    ca-certificates \
    gnupg \
    lsb-release

# =============================================================================
# 2. SWAP — evita OOM no t3.micro (1GB RAM)
# =============================================================================
echo ""
echo "[2/7] Configurando memória swap (2GB)..."

if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "  [✓] Swap de 2GB criado e ativado permanentemente"
else
    echo "  [!] Swap já existe, pulando"
fi

free -h

# =============================================================================
# 3. DOCKER
# =============================================================================
echo ""
echo "[3/7] Instalando Docker..."

sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Docker inicia automaticamente com o sistema
sudo systemctl enable docker
sudo systemctl start docker

# Permite usar docker sem sudo
sudo usermod -aG docker $USER

echo "  [✓] Docker: $(docker --version)"
echo "  [✓] Docker Compose: $(docker compose version)"

# =============================================================================
# 4. CLONAR REPOSITÓRIO
# =============================================================================
echo ""
echo "[4/7] Clonando repositório..."

cd ~
if [ -d "SRC" ]; then
    echo "  Pasta SRC já existe. Atualizando..."
    cd SRC
    git fetch --depth=1 origin main
    git merge origin/main --allow-unrelated-histories -m "update" 2>/dev/null || git reset --hard origin/main
    cd ~
else
    git clone --depth=1 https://github.com/2026-1-NCC5/Projeto2.git SRC
    echo "  [✓] Repositório clonado"
fi

# =============================================================================
# 5. CRIAR ARQUIVOS .ENV
# =============================================================================
echo ""
echo "[5/7] Criando arquivos de configuração (.env)..."

cat > ~/SRC/Server/.env << 'EOF'
POSTGRES_DB=liderancas_db
POSTGRES_USER=liderancas_user
POSTGRES_PASSWORD=SenhaForte123
DATABASE_URL=postgresql+psycopg2://liderancas_user:SenhaForte123@db:5432/liderancas_db

SECRET_KEY=ProjetoInterdisciplinarSenhaBemForte123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
CAMERA_API_KEY=camera-secret-key
EOF
echo "  [✓] Server/.env criado"

# Dashboard usa nome do container Docker internamente — não precisa do IP externo
cat > ~/SRC/Dashboard/.env << 'EOF'
DATABASE_URL=postgresql://liderancas_user:SenhaForte123@db:5432/liderancas_db
SERVER_URL=http://liderancas_backend:8000
EOF
echo "  [✓] Dashboard/.env criado"

# =============================================================================
# 6. BUILD E START DOS CONTAINERS
# =============================================================================
echo ""
echo "[6/7] Subindo containers Docker..."

# Usa newgrp para garantir permissões de docker sem precisar relogar
cd ~/SRC/Server

docker compose down --remove-orphans 2>/dev/null || true
docker compose up -d --build

echo ""
echo "  Aguardando containers iniciarem (45s)..."
sleep 45

echo ""
echo "  Status dos containers:"
docker compose ps

# =============================================================================
# 7. VERIFICAÇÃO FINAL
# =============================================================================
echo ""
echo "[7/7] Verificando serviços..."

PUBLIC_IP=$(curl -s --max-time 5 http://checkip.amazonaws.com/ \
    || curl -s --max-time 5 http://ifconfig.me \
    || echo "VERIFIQUE_NO_CONSOLE_AWS")

echo ""
echo "=========================================="
echo " SETUP CONCLUÍDO COM SUCESSO!"
echo "=========================================="
echo ""
echo "  IP público desta EC2: $PUBLIC_IP"
echo ""
echo "  Serviços:"
echo "    Backend  → http://$PUBLIC_IP:8000"
echo "    API Docs → http://$PUBLIC_IP:8000/docs"
echo "    Dashboard → http://$PUBLIC_IP:8050"
echo ""
echo "  Os containers reiniciam automaticamente"
echo "  com o sistema (restart: always)."
echo ""
echo "=========================================="
echo " PRÓXIMO PASSO:"
echo "  Atualize o IP $PUBLIC_IP nos arquivos:"
echo "  1. App/lib/core/api/api_config.dart"
echo "  2. camera_ai/camera_config.json"
echo "  3. camera_ai/config.py"
echo "  4. camera_ai/detector.py"
echo "=========================================="
echo ""

# Teste rápido do backend
echo "Testando backend..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "  [✓] Backend respondendo (HTTP $HTTP_CODE)"
else
    echo "  [!] Backend retornou HTTP $HTTP_CODE — aguarde mais alguns segundos e teste:"
    echo "      curl http://localhost:8000/docs"
fi

echo ""
echo "Testando dashboard..."
HTTP_DASH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8050 || echo "000")
if [ "$HTTP_DASH" = "200" ]; then
    echo "  [✓] Dashboard respondendo (HTTP $HTTP_DASH)"
else
    echo "  [!] Dashboard retornou HTTP $HTTP_DASH — aguarde mais alguns segundos."
fi
