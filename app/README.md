# Diretório da API (app)

Este diretório contém o código da API REST que implementa o serviço de armazenamento chave-valor.

## Conteúdo

- `main.py` - Ponto de entrada da aplicação, implementa os endpoints REST
- `cache.py` - Implementação do cliente de cache Redis
- `mq.py` - Cliente para comunicação com o RabbitMQ
- `metrics.py` - Configuração de métricas para monitoramento
- `health_check.py` - Implementação dos health checks
- `requirements.txt` - Dependências Python necessárias
- `storage/` - Implementações de backends de armazenamento

## Tecnologias

- FastAPI - Framework para APIs REST
- Redis - Cache distribuído
- RabbitMQ - Fila de mensagens
- CockroachDB - Armazenamento persistente

## Endpoints Principais

- `GET /kv?key=<key>` - Recuperar um valor
- `PUT /kv` - Armazenar um par chave-valor
- `DELETE /kv?key=<key>` - Remover um par chave-valor 