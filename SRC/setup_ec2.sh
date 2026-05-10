#!/bin/bash
# =============================================================================
# Script de setup completo para nova EC2 — Lideranças Empáticas
# Executar como: bash setup_ec2.sh
# =============================================================================

set -e  # Para se qualquer comando falhar

echo "=========================================="
echo " SETUP EC2 — Lideranças Empáticas"
echo "=========================================="

# =============================================================================
# 1. SISTEMA
# =============================================================================
echo ""
echo "[1/6] Atualizando sistema..."
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    htop \
    ca-certificates \
    gnupg \
    lsb-release

# =============================================================================
# 2. DOCKER
# =============================================================================
echo ""
echo "[2/6] Instalando Docker..."

# Remove versões antigas se existirem
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Adiciona repositório oficial do Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Permite usar docker sem sudo
sudo usermod -aG docker $USER

echo "Docker instalado: $(docker --version)"
echo "Docker Compose instalado: $(docker compose version)"

# =============================================================================
# 3. CLONAR REPOSITÓRIO
# =============================================================================
echo ""
echo "[3/6] Clonando repositório..."

cd ~
if [ -d "SRC" ]; then
    echo "Pasta SRC já existe. Fazendo pull..."
    cd SRC
    git pull origin main
    cd ~
else
    git clone --depth=1 https://github.com/2026-1-NCC5/Projeto2.git SRC
fi

# =============================================================================
# 4. CRIAR ARQUIVOS .ENV
# =============================================================================
echo ""
echo "[4/6] Criando arquivos de configuração (.env)..."

# Server .env
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

# Dashboard .env — SERVER_URL usa nome do container (rede interna Docker)
cat > ~/SRC/Dashboard/.env << 'EOF'
DATABASE_URL=postgresql://liderancas_user:SenhaForte123@db:5432/liderancas_db
SERVER_URL=http://liderancas_backend:8000
EOF

echo "  [✓] Dashboard/.env criado"

# =============================================================================
# 5. BUILD E START DOS CONTAINERS
# =============================================================================
echo ""
echo "[5/6] Subindo containers Docker..."

cd ~/SRC/Server

# Para containers antigos se existirem
docker compose down --remove-orphans 2>/dev/null || true

# Build e start
docker compose up -d --build

echo ""
echo "Aguardando containers iniciarem (30s)..."
sleep 30

# Status
docker compose ps

# =============================================================================
# 6. VERIFICAÇÃO
# =============================================================================
echo ""
echo "[6/6] Verificando serviços..."

# Pega o IP público da instância
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com/ 2>/dev/null || curl -s http://ifconfig.me 2>/dev/null || echo "IP_NAO_DETECTADO")

echo ""
echo "=========================================="
echo " SETUP CONCLUÍDO!"
echo "=========================================="
echo ""
echo " IP público desta EC2: $PUBLIC_IP"
echo ""
echo " Serviços disponíveis:"
echo "   Backend  → http://$PUBLIC_IP:8000"
echo "   Docs API → http://$PUBLIC_IP:8000/docs"
echo "   Dashboard → http://$PUBLIC_IP:8050"
echo ""
echo " IMPORTANTE: Atualize o IP $PUBLIC_IP nos arquivos do projeto."
echo " Consulte o arquivo SRC/explicacao.md para a lista completa."
echo ""
echo "=========================================="

# Teste rápido
echo "Teste do backend:"
curl -s -o /dev/null -w "  Status HTTP: %{http_code}\n" http://localhost:8000/docs || echo "  Backend ainda iniciando, aguarde alguns segundos."
