# 💰 Finance API — Gerenciador Financeiro

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red) ![Alembic](https://img.shields.io/badge/Alembic-Migrations-orange) ![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker) ![JWT](https://img.shields.io/badge/JWT-Authentication-black)

---

## 📌 Sobre o Projeto

O **Finance API** é uma aplicação backend desenvolvida para centralizar o gerenciamento de finanças pessoais através de uma API REST.

A aplicação permite que usuários autenticados registrem suas **receitas e despesas**, acompanhem seu **saldo mensal**, consultem gastos por categoria e gerenciem uma carteira de **investimentos**.

Para os investimentos, o sistema realiza consultas externas para obter cotações atualizadas de diferentes tipos de ativos, permitindo calcular o valor atual da carteira e o lucro ou prejuízo de cada posição.

O projeto foi desenvolvido com foco em **boas práticas de desenvolvimento backend**, incluindo autenticação JWT, validação de dados, regras de negócio, ORM, migrations, integração com APIs externas e containerização com Docker.

---

# ✨ Principais Funcionalidades

### 🔐 Autenticação e Segurança

* Cadastro de usuários
* Login utilizando JWT
* OAuth2 Password Flow
* Proteção de endpoints privados
* Autenticação através de Bearer Token
* Senhas armazenadas utilizando hash
* Isolamento dos dados entre usuários

### 💵 Controle Financeiro

* Cadastro de receitas
* Cadastro de despesas
* Exclusão de transações
* Classificação por categorias
* Validação de tipos e categorias
* Registro automático de data
* Consulta das próprias transações

### 📊 Relatórios Financeiros

* Resumo mensal de receitas
* Resumo mensal de despesas
* Cálculo automático do saldo
* Consulta de valores por categoria
* Filtros por mês e ano

### 📈 Gerenciamento de Investimentos

* Registro de compras/aportes
* Registro de vendas/resgates
* Histórico de movimentações
* Controle da quantidade de ativos
* Agrupamento das posições por ativo
* Cálculo do patrimônio atual
* Cálculo de lucro e prejuízo

### 🌎 Cotações de Ativos

O sistema consulta cotações externas de acordo com o tipo de ativo:

* 💵 Moedas
* 🪙 Criptomoedas
* 📈 Ações
* 🏢 FIIs

As cotações são utilizadas para atualizar o valor das posições de investimento.

### 🐳 Infraestrutura

* API containerizada com Docker
* PostgreSQL em container
* Docker Compose
* Persistência dos dados através de volume
* Variáveis de ambiente
* Migrations utilizando Alembic

### 📚 Documentação

* Swagger UI
* ReDoc
* OpenAPI
* Endpoints documentados automaticamente pelo FastAPI

---

# 🏗️ Arquitetura do Projeto

```text
Finance-API/
│
├── alembic/
│   └── versions/                  # Histórico das migrations
│
├── app/
│   │
│   ├── routers/                   # Endpoints da API
│   │   ├── auth_routes.py
│   │   ├── transacao_routes.py
│   │   └── investimento_routes.py
│   │
│   ├── services/                  # Serviços e integrações externas
│   │   └── finance_service.py
│   │
│   ├── database.py                # Configuração do banco
│   ├── dependencies.py            # Dependências e autenticação
│   ├── main.py                    # Inicialização da aplicação
│   ├── models.py                  # Modelos SQLAlchemy
│   └── schemas.py                 # Schemas Pydantic
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

# 🛠️ Tecnologias Utilizadas

## Backend

* **Python**
* **FastAPI**
* **Pydantic**
* **SQLAlchemy**

## Banco de Dados

* **PostgreSQL**

## Segurança

* **JWT**
* **OAuth2**
* **pwdlib**

## Integrações

* **HTTPX**
* **AwesomeAPI**
* **yfinance**

## Banco e Migrations

* **Alembic**

## Infraestrutura

* **Docker**
* **Docker Compose**

---

# 🔄 Fluxo da Aplicação

```text
                    Usuário
                       │
                       ▼
                ┌─────────────┐
                │   FastAPI   │
                └──────┬──────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
      Autenticação  Transações  Investimentos
          │            │            │
          │            │            ▼
          │            │      Consulta cotação
          │            │            │
          │            │            ▼
          │            │      APIs externas
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
                 ┌───────────┐
                 │ SQLAlchemy│
                 └─────┬─────┘
                       │
                       ▼
                 ┌───────────┐
                 │ PostgreSQL│
                 └───────────┘
```

---

# 💰 Fluxo Financeiro

O fluxo de uma transação funciona da seguinte maneira:

```text
Usuário autenticado
        ↓
Envia receita/despesa
        ↓
Pydantic valida os dados
        ↓
Regras de negócio são verificadas
        ↓
Transação vinculada ao usuário
        ↓
SQLAlchemy persiste no PostgreSQL
        ↓
Dados disponíveis para consultas
        ↓
Relatórios financeiros
```

---

# 📈 Fluxo dos Investimentos

Para uma compra de ativo:

```text
Usuário informa ticker e valor
             ↓
      API identifica o ativo
             ↓
       Consulta cotação
             ↓
     Calcula quantidade
             ↓
   Registra movimentação
             ↓
       PostgreSQL
```

Para consultar o patrimônio:

```text
Movimentações armazenadas
          ↓
Agrupamento por ativo
          ↓
Quantidade total
          ↓
Consulta da cotação atual
          ↓
Valor atual da posição
          ↓
Lucro / Prejuízo
          ↓
Patrimônio total
```

---

# 🔐 Autenticação

A aplicação utiliza **JWT** para autenticar os usuários.

O fluxo de autenticação é:

```text
Cadastro
   ↓
Senha transformada em hash
   ↓
Dados armazenados
   ↓
Login
   ↓
Validação das credenciais
   ↓
JWT gerado
   ↓
Bearer Token
   ↓
Acesso às rotas protegidas
```

As requisições autenticadas utilizam:

```http
Authorization: Bearer <TOKEN>
```

---

# ⚙️ Configuração

Antes de executar o projeto, crie um arquivo `.env` baseado no `.env.example`.

Exemplo:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DB_NAME=financeapi

SECRET_KEY=sua_chave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Variáveis

| Variável                      | Descrição                   |
| ----------------------------- | --------------------------- |
| `DB_USER`                     | Usuário do PostgreSQL       |
| `DB_PASSWORD`                 | Senha do banco              |
| `DB_HOST`                     | Host do PostgreSQL          |
| `DB_PORT`                     | Porta do PostgreSQL         |
| `DB_NAME`                     | Nome do banco               |
| `SECRET_KEY`                  | Chave utilizada pelo JWT    |
| `ALGORITHM`                   | Algoritmo utilizado no JWT  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de expiração do token |

---

# 🐳 Executando com Docker

## 1. Clone o repositório

```bash
git clone https://github.com/Guipassarim0/Finance-API.git

cd Finance-API
```

---

## 2. Configure o ambiente

Crie o arquivo:

```text
.env
```

Utilizando como referência:

```text
.env.example
```

---

## 3. Inicie os containers

```bash
docker compose up -d --build
```

A aplicação irá iniciar o ambiente contendo:

* FastAPI
* PostgreSQL

---

## 4. Verifique os containers

```bash
docker ps
```

Para acompanhar os logs:

```bash
docker compose logs -f
```

---

## 5. Acesse a API

```text
http://localhost:8000
```

---

# 📖 Documentação da API

O FastAPI disponibiliza automaticamente duas interfaces de documentação.

### Swagger UI

```text
http://localhost:8000/docs
```

Permite visualizar e testar os endpoints diretamente pelo navegador.

### ReDoc

```text
http://localhost:8000/redoc
```

Interface alternativa para consulta da documentação OpenAPI.

---

# 🔑 Primeira utilização

Para começar a utilizar a API:

```text
1. Criar usuário
       ↓
2. Realizar login
       ↓
3. Copiar o access_token
       ↓
4. Autorizar o Swagger
       ↓
5. Registrar uma receita
       ↓
6. Registrar uma despesa
       ↓
7. Consultar o resumo financeiro
       ↓
8. Registrar investimentos
       ↓
9. Consultar a carteira
```

---

# 👤 Autenticação

## Criar usuário

```http
POST /auth/criar_conta
```

### Exemplo

```json
{
    "nome": "Guilherme",
    "email": "guilherme@email.com",
    "senha": "123456"
}
```

---

## Login

```http
POST /auth/login
```

O login retorna um token JWT:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer"
}
```

Após receber o token, utilize o botão **Authorize** do Swagger para acessar os endpoints protegidos.

---

## Usuário autenticado

```http
GET /auth/me
```

Retorna os dados do usuário atualmente autenticado.

---

# 💳 Transações

As transações representam toda movimentação financeira do usuário.

## Criar transação

```http
POST /transacao/criar_transacao
```

Exemplo de receita:

```json
{
    "tipo": "RECEITA",
    "categoria": "SALARIO",
    "valor": 3500,
    "descricao": "Salário"
}
```

Exemplo de despesa:

```json
{
    "tipo": "DESPESA",
    "categoria": "ALIMENTACAO",
    "valor": 45.90,
    "descricao": "Almoço"
}
```

---

## Listar transações

```http
GET /transacao/listar_transacoes
```

Retorna as transações pertencentes ao usuário autenticado.

---

## Excluir transação

```http
DELETE /transacao/deletar_transacao?id=1
```

Antes da exclusão, a API verifica se a transação pertence ao usuário autenticado.

---

# 📊 Relatórios Financeiros

## Resumo mensal

```http
GET /transacao/resumo_tipos_mensal
```

Exemplo:

```text
GET /transacao/resumo_tipos_mensal?mes=8&ano=2026
```

Retorna:

```json
{
    "RECEITA": 5000,
    "DESPESA": 1800,
    "saldo": 3200,
    "mes": 8,
    "ano": 2026
}
```

---

## Resumo por categoria

```http
GET /transacao/resumo_categorias_mensal
```

Permite analisar uma categoria específica dentro de determinado período.

Exemplo:

```text
GET /transacao/resumo_categorias_mensal?mes=8&ano=2026&tipo=DESPESA&categoria=ALIMENTACAO
```

---

# 📂 Categorias

### Receitas

```text
SALARIO
FREELANCE
REEMBOLSO
VENDA
BONUS
PRESENTE
OUTROS
```

### Despesas

```text
MERCADO
ALIMENTACAO
TRANSPORTE
SAUDE
LAZER
ASSINATURAS
MORADIA
CONTAS
PARCELAS
PRESENTE
OUTROS
```

A aplicação possui validações para evitar combinações inválidas entre o tipo da transação e sua categoria.

---

# 📈 Investimentos

O módulo de investimentos permite controlar diferentes tipos de ativos.

Exemplos:

```text
Ações
FIIs
Moedas
Criptomoedas
```

---

## Comprar / Aportar

```http
POST /investimentos/comprar
```

Exemplo:

```json
{
    "ticker": "PETR4",
    "valor_brl": 500
}
```

O sistema consulta a cotação atual do ativo e calcula automaticamente a quantidade adquirida.

---

## Histórico

```http
GET /investimentos/historico
```

Retorna as movimentações de investimento registradas pelo usuário.

---

## Vender / Resgatar

```http
POST /investimentos/vender
```

Exemplo:

```json
{
    "ticker": "PETR4",
    "valor_brl": 200
}
```

O sistema verifica a posição disponível antes de realizar a operação.

---

## Resumo da carteira

```http
GET /investimentos/resumo
```

O endpoint consolida as movimentações e apresenta informações como:

* Quantidade atual
* Total investido
* Cotação atual
* Valor atual
* Lucro ou prejuízo
* Patrimônio total

Exemplo:

```json
{
    "patrimonio_total_atual_brl": 12500.75,
    "total_investido_historico_brl": 11000.00,
    "ativos_agrupados": [
        {
            "ticker": "PETR4",
            "total_investido_brl": 5000.00,
            "total_quantidade": 120.5,
            "cotacao_atual": 43.20,
            "valor_atual_brl": 5205.60,
            "lucro_prejuizo_brl": 205.60
        }
    ]
}
```

---

# 🌎 Integração com Cotações

A aplicação utiliza diferentes fontes para obter informações de mercado.

### 💵 Moedas e Criptomoedas

Utilização da **AwesomeAPI** para consultar cotações.

### 📈 Ações e FIIs

Utilização do **Yahoo Finance**, através da biblioteca `yfinance`.

Para ativos brasileiros, o ticker pode ser convertido para o padrão utilizado pelo Yahoo Finance:

```text
PETR4
   ↓
PETR4.SA
```

---

# 🧠 Regras de Negócio

### Transações

* Valores precisam ser maiores que zero.
* O tipo deve ser uma receita ou despesa válida.
* A categoria precisa ser compatível com o tipo.
* Usuários somente acessam suas próprias transações.
* Relatórios podem ser filtrados por mês e ano.

### Investimentos

* O valor da operação deve ser positivo.
* O ativo precisa possuir cotação disponível.
* Não é possível vender uma quantidade maior que a posição disponível.
* Compras aumentam a quantidade do ativo.
* Vendas reduzem a quantidade do ativo.
* O patrimônio é recalculado utilizando a cotação atual.

---

# 🗄️ Banco de Dados

O projeto utiliza **PostgreSQL** como banco de dados principal.

A comunicação com o banco é realizada através do **SQLAlchemy ORM**.

Principais entidades:

```text
┌──────────────┐
│    Usuario   │
└──────┬───────┘
       │
       ├───────────────┐
       │               │
       ▼               ▼
┌──────────────┐ ┌─────────────────────┐
│  Transacao   │ │ PosicaoInvestimento│
└──────────────┘ └─────────────────────┘
```

Cada transação e operação de investimento está vinculada ao usuário responsável.

---

# 🔄 Migrations

O projeto utiliza **Alembic** para versionar alterações no banco de dados.

Aplicar migrations:

```bash
alembic upgrade head
```

Criar uma migration:

```bash
alembic revision --autogenerate -m "descricao"
```

Verificar versão:

```bash
alembic current
```

Voltar uma migration:

```bash
alembic downgrade -1
```

---

# 🐳 Comandos Docker

### Iniciar

```bash
docker compose up
```

### Iniciar em background

```bash
docker compose up -d
```

### Reconstruir imagens

```bash
docker compose up --build
```

### Parar containers

```bash
docker compose down
```

### Ver containers

```bash
docker ps
```

### Visualizar logs

```bash
docker compose logs -f
```

### Recriar ambiente

```bash
docker compose down

docker compose up -d --build
```

---

# 🧪 Testando a API

O projeto pode ser testado diretamente através do Swagger ou utilizando ferramentas como **Postman**.

### Fluxo sugerido

```text
POST /auth/criar_conta
        ↓
POST /auth/login
        ↓
Autorizar JWT
        ↓
GET /auth/me
        ↓
POST /transacao/criar_transacao
        ↓
GET /transacao/listar_transacoes
        ↓
GET /transacao/resumo_tipos_mensal
        ↓
POST /investimentos/comprar
        ↓
GET /investimentos/historico
        ↓
GET /investimentos/resumo
        ↓
POST /investimentos/vender
```

---

# 🔒 Boas Práticas de Segurança

O projeto utiliza:

* Hash de senhas
* JWT para autenticação
* Bearer Authentication
* Variáveis de ambiente
* Separação dos dados por usuário
* Validação de entrada com Pydantic
* Validação das regras de negócio

---

# 🚧 Próximas Evoluções

Algumas funcionalidades que podem ser adicionadas futuramente:

* [ ] Atualização de transações
* [ ] Paginação
* [ ] Filtros avançados
* [ ] Testes automatizados com Pytest
* [ ] Dashboard financeiro
* [ ] Exportação de relatórios
* [ ] Notificações de movimentações
* [ ] Cache de cotações com Redis
* [ ] Rate Limiting
* [ ] CI/CD com GitHub Actions
* [ ] Deploy automatizado
* [ ] Monitoramento e observabilidade

---


# 👨‍💻 Autor

**Guilherme Passarim**

Desenvolvedor Backend com foco em **Python, FastAPI, APIs REST e PostgreSQL**.

### 🛠️ Também trabalhando com

```text
Python
FastAPI
PostgreSQL
SQLAlchemy
Alembic
JWT
OAuth2
REST APIs
Docker
Docker Compose
AWS
Web Scraping
Consumo de APIs
```

---

## ⭐ Projeto de Portfólio

O **Finance API** demonstra a construção de uma aplicação backend completa, combinando autenticação, persistência de dados, regras de negócio, relatórios financeiros, gerenciamento de investimentos e integração com serviços externos.

O projeto foi desenvolvido com foco em **organização, segurança, escalabilidade e boas práticas de desenvolvimento de APIs REST**.
