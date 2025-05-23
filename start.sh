#!/usr/bin/env bash
set -euo pipefail

echo "Iniciando sistemas distribuídos..."
docker compose up --build -d

echo "Aguardando serviços iniciarem..."
sleep 10  # Aguarda inicialização mínima

echo "Executando testes unitários..."

# Verificar se as dependências de teste estão instaladas sem tentar instalar via apt
# Isso evita problemas de permissão
check_dependencies() {
  if ! command -v python3 &> /dev/null; then
    echo "Python3 não encontrado. Por favor, instale o Python antes de executar."
    exit 1
  fi
  
  # Verifica se o módulo requests está instalado usando o Python
  if ! python3 -c "import requests" &> /dev/null; then
    echo "Módulo Python 'requests' não encontrado."
    echo "Para instalar manualmente: pip install requests"
    echo "Executando testes sem a instalação automática do módulo."
  fi
}

# Verificar dependências
check_dependencies

# Executa os testes unitários
python3 -m unitary_tests.run_tests

# Se os testes passarem (código de saída 0), continua com a inicialização
if [ $? -eq 0 ]; then
    echo
    echo "Testes concluídos com sucesso! Sistema pronto para uso."
    echo
    echo "Nginx LB → http://localhost/"
    echo "RabbitMQ UI → http://localhost:25673 (admin/admin)"
    echo "Cockroach UI → http://localhost:8080"
    echo "Swagger → http://localhost/docs"
    echo "Health API → http://localhost/health"
    echo
    echo "Sistema iniciado e em execução! "
else
    echo "Testes unitários falharam! Verifique os logs para mais detalhes."
    echo "ℹO sistema está rodando, mas pode não estar funcionando corretamente."
fi
