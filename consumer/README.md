# Diretório de Consumidores (consumer)

Este diretório contém o código dos workers que processam mensagens da fila RabbitMQ e executam operações de escrita no banco de dados.

## Conteúdo

- `worker.py` - Implementação do worker consumidor de mensagens
- `Dockerfile` - Configuração para construção da imagem Docker
- `__init__.py` - Inicialização do módulo Python
- `requirements.txt` - Dependências Python necessárias
- `metrics.py` - Configuração de métricas para monitoramento

## Funcionalidades

- Processamento assíncrono de operações PUT e DELETE
- Comunicação com o banco de dados CockroachDB
- Invalidação do cache Redis após atualizações
- Monitoramento de saúde e métricas
- Health checks para orquestração de containers 