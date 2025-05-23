# Diretório de Configuração do Nginx

Este diretório contém os arquivos de configuração do Nginx, utilizados para balanceamento de carga e roteamento.

## Conteúdo

- `nginx.conf` - Configuração principal do Nginx para balanceamento das APIs
- `cockroach-lb.conf` - Configuração do balanceador de carga para o CockroachDB

## Funcionalidades

- Balanceamento de carga entre múltiplas instâncias da API
- Roteamento para recursos internos (métricas, health checks, documentação)
- Timeouts otimizados para ambiente distribuído
- Health checks para detectar nós indisponíveis
- Configuração de logging para monitoramento 