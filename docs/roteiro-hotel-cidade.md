# Roteiro — Cadastro de Cidades e Hotéis

## Objetivo

Construir um cadastro de Cidades e Hotéis atravessando todas
as camadas da aplicação, desde o banco de dados até o frontend.

A relação entre as entidades será:

Cidade 1 -------- N Hotel

Uma cidade pode possuir vários hotéis.
Cada hotel pertence a uma única cidade.

## Entidades

### Cidade

- id: UUID
- nome: string

### Hotel

- id: UUID
- nome: string
- cidade_id: UUID
- cidade_id referencia cidades.id

## Fluxo da implementação

A implementação será realizada em 12 issues, seguindo a ordem
das dependências entre as camadas.

### 1. Roteiro

Documentação da trilha de implementação.

### 2. Modelagem

Definição das entidades Cidade e Hotel, da cardinalidade 1:N
e da localização da chave estrangeira.

### 3. Models SQLAlchemy

Criação dos models Cidade e Hotel utilizando SQLAlchemy,
incluindo o relacionamento entre as entidades.

### 4. Migração Alembic

Criação da migration responsável por criar as tabelas
cidades e hoteis no PostgreSQL.

### 5. Schemas de Cidade

Criação dos schemas de entrada e saída da entidade Cidade.

### 6. Schemas de Hotel

Criação dos schemas de entrada e saída de Hotel.

O schema de entrada receberá cidade_id e o schema de saída
apresentará os dados da cidade de forma aninhada.

### 7. Repository de Cidade

Implementação das operações:

- create
- list

### 8. Repository de Hotel

Implementação das operações:

- create
- list

A consulta deverá utilizar joinedload para carregar a cidade
junto com os hotéis e evitar o problema de N+1 queries.

### 9. Services

Criação da camada de serviços responsável pelas regras de
negócio, mantendo essas regras fora das rotas.

### 10. Rotas de Cidade

Implementação dos endpoints:

POST /api/v1/cidades
GET /api/v1/cidades

### 11. Rotas de Hotel

Implementação dos endpoints:

POST /api/v1/hoteis
GET /api/v1/hoteis

Também será implementado o filtro de hotéis por cidade e o
registro do router no main.py.

### 12. Frontend

O frontend consumirá a API e exibirá o JSON retornado,
sem necessidade de estilização.

## Contrato final da API

### Criar cidade

POST /api/v1/cidades

Exemplo:

{
  "nome": "Fortaleza"
}

### Listar cidades

GET /api/v1/cidades

Exemplo de resposta:

[
  {
    "id": "uuid",
    "nome": "Fortaleza"
  }
]

### Criar hotel

POST /api/v1/hoteis

Exemplo:

{
  "nome": "Hotel Beira-Mar",
  "cidade_id": "uuid-da-cidade"
}

### Listar hotéis

GET /api/v1/hoteis

Exemplo de resposta:

[
  {
    "id": "uuid",
    "nome": "Hotel Beira-Mar",
    "cidade": {
      "id": "uuid",
      "nome": "Fortaleza"
    }
  }
]

## Fluxo dos dados

O fluxo esperado da aplicação será:

Frontend
   ↓
API / Rotas
   ↓
Services
   ↓
Repositories
   ↓
SQLAlchemy Models
   ↓
PostgreSQL

A resposta percorre o caminho inverso até chegar ao frontend.

## Estrutura esperada

apps/
├── services/
│   └── core-service/
│       ├── alembic/
│       │   └── versions/
│       └── app/
│           ├── api/
│           │   └── v1/
│           ├── models/
│           ├── repositories/
│           ├── schemas/
│           └── services/
│
└── frontend/
    └── src/

## Resultado esperado

Ao final das 12 issues, o sistema deverá permitir:

1. Criar cidades.
2. Listar cidades.
3. Criar hotéis vinculados a uma cidade.
4. Listar hotéis.
5. Retornar a cidade relacionada dentro do hotel.
6. Consumir os dados através do frontend.