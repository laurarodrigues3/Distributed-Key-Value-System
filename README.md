# Sistema Distribuído de Armazenamento Chave-Valor

[![GitHub]](https://github.com/a80232/SPD-SD)

## Sumário

Este projeto implementa um sistema de armazenamento de chave-valor distribuído, capaz de armazenar, recuperar e gerenciar pares chave-valor em um ambiente distribuído. O sistema foi projetado para lidar com as principais questões de sistemas distribuídos, incluindo tolerância a falhas, consistência, disponibilidade e escalabilidade.

## Arquitetura do Sistema

![Arquitetura do Sistema] 

O sistema é composto pelos seguintes componentes:

1. **Frontend**:
   - Interface web HTML/JavaScript acessível via navegador
   - API REST para acesso programático

2. **API Nodes**:
   - Múltiplas instâncias da API para balanceamento de carga
   - Implementado com FastAPI (Python)
   - Exposição de endpoints REST: PUT, GET, DELETE
   - Health checks para monitorização

3. **Message Queue (RabbitMQ)**:
   - Cluster com 3 nós para alta disponibilidade
   - Utilizado para processamento assíncrono de operações de escrita
   - Filas duráveis para garantir persistência das operações

4. **Consumers (Workers)**:
   - Processadores assíncronos das mensagens
   - Executam operações de escrita no banco de dados
   - Invalidam cache conforme necessário

5. **Cache Layer (Redis)**:
   - Cluster Redis com 1 master, 2 réplicas e 3 sentinelas
   - Armazenamento em memória para operações rápidas de leitura
   - Mecanismo de failover automático com Redis Sentinel

6. **Storage Layer (CockroachDB)**:
   - Cluster CockroachDB com 3 nós
   - Armazenamento persistente de dados
   - Suporte nativo para distribuição e replicação de dados

7. **Load Balancers (Nginx)**:
   - Distribuição de tráfego para múltiplas instâncias de API
   - Health checks para detecção de falhas
   - Balanceamento para nós do CockroachDB

## Funcionalidades Implementadas

O sistema oferece as seguintes operações através de sua API REST:

- **PUT (key, value)**: Armazena um valor associado a uma chave
  - `PUT /kv` com body `{"data": {"key": "foo", "value": "bar"}}`
  
- **GET (key)**: Recupera o valor associado a uma chave
  - `GET /kv?key=foo`
  
- **DELETE (key)**: Remove um par chave-valor
  - `DELETE /kv?key=foo`
  
Adicionalmente, o sistema fornece:

- Interface Web para interações diretas
- Health checks para monitoramento de estado
- Estatísticas de cache e métricas de operação
- Documentação Swagger acessível via `/docs`

## Requisitos de Sistema

- Docker e Docker Compose
- Sistema operacional Linux (ou WSL para Windows)
- Acesso à internet para download das imagens Docker
- Mínimo de 4GB de RAM e 2 CPUs para desempenho adequado

## Instalação e Execução

### Instalação Rápida

1. Clone o repositório:
   ```bash
   git clone https://github.com/a80232/SPD-SD.git
   cd SPD-SD
   ```

2. Execute o script de inicialização:
   ```bash
   ./start.sh
   ```

   Este script irá:
   - Construir e iniciar todos os containers
   - Executar testes unitários para validação
   - Verificar a saúde dos serviços

3. Acesse o sistema:
   - Interface Web: [http://localhost](http://localhost)
   - Swagger API: [http://localhost/docs](http://localhost/docs)
   - Health Check: [http://localhost/health](http://localhost/health)

### Instalação Manual

Se preferir executar manualmente:

1. Clone o repositório:
   ```bash
   git clone https://github.com/a80232/SPD-SD.git
   cd SPD-SD
   ```

2. Inicie os containers:
   ```bash
   docker compose up -d
   ```

3. Verifique o estado dos serviços:
   ```bash
   docker compose ps
   ```

4. Execute os testes unitários:
   ```bash
   python3 -m unitary_tests.run_tests
   ```

## Uso da API

### Exemplo de PUT (Armazenar chave-valor)

```bash
curl -X PUT http://localhost/kv \
  -H "Content-Type: application/json" \
  -d '{"data": {"key": "exemplo", "value": "valor123"}}'
```

### Exemplo de GET (Obter valor)

```bash
curl http://localhost/kv?key=exemplo
```

### Exemplo de DELETE (Remover chave-valor)

```bash
curl -X DELETE http://localhost/kv?key=exemplo
```

## Aspectos de Sistemas Distribuídos

### Concorrência

O sistema lida com concorrência em vários níveis:

1. **Múltiplos nós de API**: Processamento paralelo de requisições
2. **Banco de dados distribuído**: CockroachDB gerencia transações concorrentes
3. **Cache com consistência eventual**: Atualizações assíncronas após operações de escrita
4. **Workers assíncronos**: Processamento paralelo de operações de escrita via RabbitMQ

### Escalabilidade

O sistema foi projetado para escalar horizontalmente:

1. **API stateless**: Permite adicionar/remover nós conforme necessário
2. **Workers independentes**: Consumidores podem ser escalados independentemente
3. **CockroachDB**: Suporta adição de novos nós para escalar armazenamento
4. **Balanceamento de carga**: Nginx distribui tráfego entre instâncias disponíveis

### Tolerância a Falhas

Mecanismos implementados para garantir funcionamento mesmo com falhas:

1. **CockroachDB Cluster**: Replicação de dados com quorum para evitar perda de dados
2. **Redis Sentinel**: Monitoramento e failover automático do Redis master
3. **RabbitMQ Cluster**: Filas duráveis distribuídas entre nós
4. **Health checks**: Monitoramento constante de saúde dos serviços
5. **Graceful shutdown**: Fechamento adequado de conexões e recursos

### Consistência

O sistema adota um modelo de consistência eventual com otimizações:

1. **Leituras**: Primeiramente buscam no cache, depois no banco de dados
2. **Escritas**: Confirmadas após enfileiramento, processadas assincronamente
3. **Invalidação de cache**: Executada após confirmação de escrita no storage
4. **TTL para cache**: Valores em cache expiram automaticamente após período configurado

### Coordenação de Recursos

Aspectos de coordenação implementados:

1. **Locks otimistas**: CockroachDB gerencia conflitos de escrita
2. **Message brokers**: RabbitMQ para coordenação de operações assíncronas
3. **Health checks distribuídos**: Monitoramento de estado entre serviços
4. **Dependências de inicialização**: Ordem de startup para garantir dependências

## Limites e Capacidades

- **Tamanho máximo de chaves/valores**: Limitado pelo backend do CockroachDB (~64KB por valor)
- **Taxa de requisições**: ~1000 req/s para leituras em cache, ~100 req/s para leituras no banco de dados
- **Capacidade de armazenamento**: Limitada apenas pelo espaço em disco dos nós CockroachDB
- **Limite de memória Redis**: 100MB por instância (configurável via variável de ambiente)
- **Máximo de chaves em cache**: 10000 (configurável via variável de ambiente)

## Monitoramento e Métricas

O sistema expõe métricas para monitoramento via Prometheus:

- **Latência de API**: Tempo de resposta para cada endpoint
- **Cache hit/miss ratio**: Eficiência do cache
- **Taxa de processamento de mensagens**: Performance dos workers
- **Operações de banco de dados**: Quantidade e duração de operações
- **Saúde dos serviços**: Status de disponibilidade

Acessível via: [http://localhost/metrics](http://localhost/metrics)

## Testes

O sistema inclui testes unitários para validação:

- **Testes de API**: Verificação das operações PUT, GET, DELETE
- **Testes de Health**: Validação dos endpoints de health check
- **Testes de carga**: Scripts para benchmarking do sistema

Para executar os testes:
```bash
python3 -m unitary_tests.run_tests
```

## Solução de Problemas

### Problemas comuns e soluções:

1. **API inacessível**:
   - Verifique o status dos containers: `docker compose ps`
   - Verifique logs: `docker compose logs api`

2. **Erro de conexão ao banco de dados**:
   - Verifique o status do CockroachDB: `docker compose logs cockroach1`
   - Reinicie o serviço: `docker compose restart cockroach-init`

3. **Problemas de cache**:
   - Verifique status Redis: `docker compose logs redis-master`
   - Reinicie o Redis: `docker compose restart redis-master`

4. **Falha nos testes**:
   - Verifique se todos os serviços estão rodando: `docker compose ps`
   - Reinicie o sistema completo: `docker compose down && docker compose up -d`

## Bibliografia

- CockroachDB Documentation: [https://www.cockroachlabs.com/docs/](https://www.cockroachlabs.com/docs/)
- Redis Documentation: [https://redis.io/documentation](https://redis.io/documentation)
- RabbitMQ Documentation: [https://www.rabbitmq.com/documentation.html](https://www.rabbitmq.com/documentation.html)
- FastAPI Documentation: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- Docker Documentation: [https://docs.docker.com/](https://docs.docker.com/)
- Nginx Documentation: [https://nginx.org/en/docs/](https://nginx.org/en/docs/)

## Contribuidor

- Laura (a80232) - [GitHub](https://github.com/a80232) 