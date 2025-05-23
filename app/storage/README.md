# Diretório de Armazenamento

Este diretório contém as implementações dos diferentes backends de armazenamento para o sistema chave-valor.

## Conteúdo

- `__init__.py` - Inicialização e seleção do backend de armazenamento
- `base.py` - Interface base para todos os backends
- `memory.py` - Implementação em memória (para desenvolvimento/testes)
- `sqlite_backend.py` - Implementação usando SQLite
- `cockroach_backend.py` - Implementação usando CockroachDB

## Funcionalidades

- Interface comum para todos os backends de armazenamento
- Abstração da camada de persistência
- Suporte a diferentes tecnologias de armazenamento
- Operações assíncronas para não bloquear o loop de eventos
- Seleção de backend via variáveis de ambiente 