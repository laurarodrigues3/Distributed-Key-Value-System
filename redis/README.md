# Diretório de Configuração Redis

Este diretório contém configurações para o Redis e Redis Sentinel utilizados no sistema.

## Conteúdo

- `sentinel.conf` - Configuração do Redis Sentinel para monitoramento e failover automático

## Funcionalidades

- Configuração do cluster Redis (1 master, 2 réplicas)
- Configuração do Sentinel para alta disponibilidade
- Detecção de falhas e failover automático
- Tempo de detecção de falhas otimizado
- Limitação de memória e políticas de expiração 