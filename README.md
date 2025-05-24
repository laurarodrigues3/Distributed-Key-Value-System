# Sistema Distribuído de Armazenamento Chave-Valor

[![GitHub](https://img.shields.io/badge/GitHub-a80232-brightgreen)](https://github.com/a80232/SPD-SD)

## Índice

- [Sumário](#sumário)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Componentes Principais](#componentes-principais)
- [Fluxo de Dados](#fluxo-de-dados)
- [Funcionalidades](#funcionalidades)
- [Requisitos de Sistema](#requisitos-de-sistema)
- [Instalação e Execução](#instalação-e-execução)
- [Uso da API](#uso-da-api)
- [Aspectos de Sistemas Distribuídos](#aspectos-de-sistemas-distribuídos)
- [Limites e Capacidades](#limites-e-capacidades)
- [Monitoramento e Métricas](#monitoramento-e-métricas)
- [Cloud Deployment](#cloud-deployment)
- [Testes](#testes)
- [Solução de Problemas](#solução-de-problemas)
- [Bibliografia](#bibliografia)

## Sumário

Este projeto implementa um sistema de armazenamento chave-valor distribuído, atendendo aos requisitos da atividade de Sistemas Paralelos e Distribuídos. O sistema armazena, recupera e gerencia pares chave-valor em um ambiente distribuído, lidando com questões fundamentais como tolerância a falhas, consistência, disponibilidade e escalabilidade.

## Arquitetura do Sistema

![Arquitetura do Sistema](architecture_diagram.mmd)

A arquitetura do sistema segue um modelo de micro-serviços distribuídos, composta por múltiplas camadas que trabalham em conjunto:

## Componentes Principais

### 1. Camada de Acesso (Edge Layer)
- **NGINX Load Balancer**: Distribui requisições entre múltiplas instâncias da API, fornecendo balanceamento de carga e alta disponibilidade.

### 2. Camada de Aplicação
- **Servidores API (FastAPI)**: Implementam endpoints RESTful para operações de chave-valor.
- **Consumer Workers**: Processam operações assíncronas de escrita e gerenciam a consistência de dados.

### 3. Camada de Mensageria
- **Cluster RabbitMQ**: Gerencia filas de mensagens duráveis para processamento assíncrono de operações de escrita.

### 4. Camada de Cache
- **Redis Master-Slave com Sentinel**: Fornece cache em memória para operações rápidas de leitura, com failover automático.

### 5. Camada de Persistência
- **Cluster CockroachDB**: Banco de dados distribuído para armazenamento persistente dos pares chave-valor.

## Fluxo de Dados

![Fluxo de Dados](data_flow_diagram.mmd)

### Operação GET (Leitura)
1. Cliente solicita um valor por chave
2. API verifica primeiro no cache Redis
3. Se houver cache miss, a API consulta o CockroachDB
4. Valor é retornado e opcionalmente armazenado no cache

### Operação PUT (Escrita)
1. Cliente envia par chave-valor
2. API atualiza o cache e envia mensagem para fila RabbitMQ
3. Consumer processa a mensagem e persiste no CockroachDB
4. Confirmação é enviada ao cliente

### Operação DELETE (Remoção)
1. Cliente solicita remoção de chave
2. API envia mensagem para fila RabbitMQ
3. Consumer processa a mensagem, remove do CockroachDB e invalida cache
4. Confirmação é enviada ao cliente

## Funcionalidades

O sistema implementa as seguintes operações via API REST:

### Operações Básicas
- **PUT (key, value)**: Armazena um valor associado a uma chave
  - `PUT /kv` com body `{"data": {"key": "foo", "value": "bar"}}`
  
- **GET (key)**: Recupera o valor associado a uma chave
  - `GET /kv?key=foo` → Resposta: `{"data": {"value": "bar"}}`
  
- **DELETE (key)**: Remove um par chave-valor
  - `DELETE /kv?key=foo`

### Funcionalidades Adicionais
- Interface Web para interações diretas
- Health checks para monitoramento de estado
- Estatísticas de cache e métricas de operação
- Documentação Swagger acessível via `/docs`

## Requisitos de Sistema

- **Docker e Docker Compose** (versão 1.29+)
- **Sistema operacional Linux** (ou WSL2 para Windows)
- **Acesso à internet** para download das imagens Docker
- **Hardware mínimo**:
  - 4GB de RAM
  - 2 CPUs
  - 5GB de espaço em disco

## Instalação e Execução

### Método Rápido (Recomendado)

1. Clone o repositório:
   ```bash
   git clone https://github.com/a80232/SPD-SD.git
   cd SPD-SD
   ```

2. Execute o script de inicialização:
   ```bash
   ./start.sh
   ```

   **O que este script faz:**
   - Constrói e inicia todos os containers Docker
   - Aguarda a inicialização dos serviços
   - Executa testes unitários para validação
   - Informa endpoints disponíveis

3. Acesse o sistema:
   - **Interface Web**: [http://localhost](http://localhost)
   - **Swagger API**: [http://localhost/docs](http://localhost/docs)
   - **Health Check**: [http://localhost/health](http://localhost/health)
   - **RabbitMQ UI**: [http://localhost:25673](http://localhost:25673) (admin/admin)
   - **CockroachDB UI**: [http://localhost:8080](http://localhost:8080)

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

**Usando curl:**
```bash
curl -X PUT http://localhost/kv \
  -H "Content-Type: application/json" \
  -d '{"data": {"key": "exemplo", "value": "valor123"}}'
```

**Usando Python:**
```python
import requests
response = requests.put(
    "http://localhost/kv",
    json={"data": {"key": "exemplo", "value": "valor123"}}
)
```

### Exemplo de GET (Obter valor)

**Usando curl:**
```bash
curl http://localhost/kv?key=exemplo
```

**Usando Python:**
```python
import requests
response = requests.get("http://localhost/kv?key=exemplo")
data = response.json()
print(data["data"]["value"])
```

### Exemplo de DELETE (Remover chave-valor)

**Usando curl:**
```bash
curl -X DELETE http://localhost/kv?key=exemplo
```

**Usando Python:**
```python
import requests
response = requests.delete("http://localhost/kv?key=exemplo")
```

## Aspectos de Sistemas Distribuídos

### Concorrência
O sistema gerencia concorrência em múltiplos níveis:

- **Múltiplos nós de API**: Processamento paralelo com balanceamento de carga
- **Transações otimistas**: CockroachDB gerencia transações concorrentes
- **Cache com consistência eventual**: Atualizações assíncronas via invalidação
- **Workers assíncronos**: Processamento paralelo via RabbitMQ

### Escalabilidade
O sistema escala horizontalmente:

- **API stateless**: Adicione/remova nós sob demanda
- **Workers independentes**: Escale consumidores conforme necessidade
- **CockroachDB**: Suporta adição dinâmica de nós
- **Balanceamento de carga**: Distribui tráfego automaticamente

### Tolerância a Falhas
Implementação robusta para garantir resistência a falhas:

- **CockroachDB Cluster**: Replicação com quorum (RF=3)
- **Redis Sentinel**: Failover automático de master para slave
- **RabbitMQ Cluster**: Filas duráveis distribuídas entre nós
- **Health checks**: Monitoramento contínuo de serviços

### Consistência
O sistema implementa consistência eventual com otimizações:

- **Leituras**: Primeiro no cache, depois no banco (consistência eventual)
- **Escritas**: Confirmadas após enfileiramento, processsadas assíncronamente
- **Invalidação de cache**: Após confirmação de escrita no storage
- **TTL para cache**: Valores expiram automaticamente

### Coordenação de Recursos
Mecanismos de coordenação implementados:

- **Locks otimistas**: CockroachDB gerencia conflitos
- **Message brokers**: RabbitMQ para coordenação assíncrona
- **Health checks distribuídos**: Monitoramento entre serviços
- **Dependências de inicialização**: Ordem controlada de startup

## Limites e Capacidades

O sistema foi projetado e testado com os seguintes limites:

| Métrica | Valor | Observação |
|---------|-------|------------|
| Tamanho máximo de chaves | ~64KB | Limitado pelo CockroachDB |
| Tamanho máximo de valores | ~64KB | Limitado pelo CockroachDB |
| Taxa de requisições (cache hit) | ~1000 req/s | Leituras em cache |
| Taxa de requisições (cache miss) | ~100 req/s | Leituras no banco de dados |
| Capacidade de armazenamento | Ilimitada* | *Limitado apenas pelo espaço em disco |
| Limite de memória Redis | 100MB | Configurável via variável de ambiente |
| Número máximo de chaves em cache | 10000 | Configurável via variável de ambiente |
| Número de nós API | 3 | Escalável conforme necessidade |
| Número de nós CockroachDB | 3 | Escalável até centenas de nós |

## Monitoramento e Métricas

O sistema expõe métricas para monitoramento via endpoints HTTP:

- **Latência de API**: Tempo de resposta por endpoint
- **Cache hit/miss ratio**: Eficiência do cache
- **Taxa de processamento de mensagens**: Performance dos workers
- **Operações de banco de dados**: Quantidade e duração
- **Saúde dos serviços**: Status de disponibilidade

**Acessível via:** [http://localhost/metrics](http://localhost/metrics)

## Cloud Deployment

O sistema foi projetado para ser facilmente implantado em ambientes de nuvem. A seguir, apresentamos uma visão geral da estratégia de deployment em cloud.

### Provedores Recomendados

O sistema pode ser implementado em qualquer um dos principais provedores de nuvem:

- **AWS** (Amazon Web Services)
- **Microsoft Azure**
- **Google Cloud Platform (GCP)**

### Mapeamento de Componentes para Serviços Cloud

| Componente       | AWS                      | Azure                   | GCP                      |
|-----------------|--------------------------|-------------------------|--------------------------|
| API/Containers  | ECS/Fargate/EKS         | AKS                     | GKE                      |
| Load Balancing  | ALB                      | Application Gateway     | Cloud Load Balancing     |
| Redis Cache     | ElastiCache              | Azure Cache for Redis   | Memorystore for Redis    |
| CockroachDB     | EC2 Cluster/Aurora       | VM Cluster/CosmosDB     | Compute Engine/Spanner   |
| RabbitMQ        | Amazon MQ                | Service Bus             | Cloud Pub/Sub            |
| Monitoramento   | CloudWatch               | Azure Monitor           | Cloud Monitoring         |

### Processo de Implantação

#### 1. Infraestrutura como Código
- Utilização de Terraform ou CloudFormation/ARM Templates/Deployment Manager
- Definição de rede, segurança e recursos computacionais
- Configuração de serviços gerenciados

#### 2. Containerização e Orquestração
- Kubernetes para orquestração de containers
- Gestão de secrets e configurações com ConfigMaps/Secrets
- Implementação de health checks e auto-healing

#### 3. Alta Disponibilidade
- Implantação em múltiplas zonas de disponibilidade
- Configuração de auto-scaling baseado em métricas
- Implementação de backups automatizados

#### 4. Segurança
- Rede isolada (VPC/VNET)
- Criptografia em trânsito e em repouso
- Autenticação e autorização via IAM
- Proteção contra DDoS e ataques web

### Arquitetura de Referência (AWS)

```
                      ┌───────────────┐
                      │   Route 53    │
                      └───────┬───────┘
                              │
                      ┌───────┴───────┐
                      │      ALB      │
                      └───────┬───────┘
                              │
                  ┌───────────┴──────────┐
                  │                      │
         ┌────────┴─────────┐   ┌────────┴─────────┐
         │  ECS/Fargate     │   │  Auto Scaling    │
         │  (API Containers)│   │  (Consumer Pods) │
         └────────┬─────────┘   └────────┬─────────┘
                  │                      │
     ┌────────────┼──────────────┬──────┴───────────┐
     │            │              │                  │
┌────┴────┐  ┌────┴────┐    ┌────┴────┐        ┌────┴────┐
│ElastiCache│  │Amazon MQ │    │CloudWatch│        │ Aurora  │
│  Redis   │  │ RabbitMQ │    │ Metrics  │        │Database │
└─────────┘  └─────────┘    └─────────┘        └─────────┘
```

### Estimativa de Recursos

Para um deployment típico com capacidade de 1000 req/s:

- **Compute**: 3-5 instâncias de compute (t3.medium ou equivalente)
- **Cache**: Cluster Redis com 2-3 nós (cache.m5.large)
- **Database**: Cluster CockroachDB com 3 nós ou serviço gerenciado equivalente
- **Mensageria**: Cluster RabbitMQ com 2 nós ou serviço gerenciado
- **Armazenamento**: ~50GB para dados, logs e backups

### Benefícios da Implantação em Cloud

- **Elasticidade**: Escala automaticamente conforme a demanda
- **Confiabilidade**: Alta disponibilidade com SLAs de provedor
- **Custo-eficiência**: Pagamento por uso e otimização de recursos
- **Manutenção reduzida**: Serviços gerenciados com patches automáticos
- **Segurança aprimorada**: Proteções em nível de infraestrutura
- **Monitoramento integrado**: Visibilidade completa da operação

## Testes

O sistema inclui testes unitários e de carga:

### Testes Unitários
- **Testes de API**: Verificação das operações básicas
- **Testes de Health**: Validação dos endpoints de saúde
- **Testes de Integração**: Validação end-to-end

Para executar os testes:
```bash
python3 -m unitary_tests.run_tests
```

### Testes de Carga
Utilizando scripts de benchmark, observamos:

- **GET com cache**: ~1000 req/s com latência < 10ms
- **GET sem cache**: ~100 req/s com latência < 50ms
- **PUT/DELETE**: ~200 req/s com latência < 30ms

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
- "Designing Data-Intensive Applications" (Martin Kleppmann, 2017)
- "Building Microservices" (Sam Newman, 2021)

## Autor

- Laura (a80232) - [GitHub](https://github.com/a80232) 