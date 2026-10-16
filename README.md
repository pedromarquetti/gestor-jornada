# Bem vindo ao Gestão de Jornada

<!--toc:start-->

- [Bem vindo ao Gestão de Jornada](#bem-vindo-ao-gestão-de-jornada)
  - [Objetivo](#objetivo)
    - [Lista de implementação](#lista-de-implementação)
  - [Estrutura do projeto](#estrutura-do-projeto)
  - [Fluxo do aplicativo](#fluxo-do-aplicativo)
  - [Tecnologias](#tecnologias)
  - [Como rodar](#como-rodar)
    - [Dev](#dev)
    - [Variáveis de ambiente](#variáveis-de-ambiente)
    - [Formatação e lint de código (Ruff)](#formatação-e-lint-de-código-ruff)

<!--toc:end-->

Este projeto faz parte do Projeto Integrador da UNIVESP

## Objetivo

Ser um aplicativo Django para cadastro e avaliação de atividades feitas em um
período de trabalho.

### Lista de implementação

> [!NOTE]
> Essa lista pode sofrer modificações e é apenas um guia geral de implementação.

- [ ] **Tela de administração** - Tela utilizada por gestores para avaliar,
      através de gráficos, a produtividade de funcionários.
- [ ] **Tela de cadastro** - Tela para cadastro de produtividade com campos de
      atividade realizada, inicio e término.
- [x] **DB** - Estrutura do banco de dados para armazenamento.
- [ ] **API** - Configuração de API básica para consulta rápida de dados.
- [ ] **Docker** - Configuração de Dockerfile para deploy.

## Estrutura do projeto

O repositório Git e a raiz do projeto Django são o mesmo diretório; todos os
comandos (`manage.py`) rodam a partir dele:

```
/                            <- raiz do projeto: aqui fica o manage.py
├── manage.py                ponto de entrada dos comandos Django
│                            (runserver, migrate, test, ensure_admin...)
├── README.md                este arquivo (roadmap em pt-BR)
├── AGENTS.md                convenções e regras de contribuição
├── requirements.txt         dependências de produção (Django, python-dotenv)
├── requirements-dev.txt     dependências de desenvolvimento (Ruff)
├── pyproject.toml           configuração do Ruff ([tool.ruff])
├── .env                     configurações locais (não versionado)
├── db.sqlite3               banco SQLite local (descartável, 
│                            gerado localmente, não versionado)
│
├── gestorjornada/           pacote do projeto Django (configuração)
│   ├── settings.py          settings únicos; carrega o .env via python-dotenv
│   ├── urls.py              raiz das URLs; hoje só liga /admin/
│   ├── wsgi.py              entry point WSGI (deploy)
│   └── asgi.py              entry point ASGI (deploy)
│
└── jornadas/                app 
    ├── models.py            Role, User (custom) e Task + TaskQuerySet
    ├── admin.py             registro dos models no /admin/
    ├── views.py             views (vazio — UI ainda não implementada)
    ├── apps.py              configuração do app
    ├── migrations/          migrations versionadas (0001 roles, 0002 seed,
    │                        0003 task)
    ├── management/commands/
    │   └── ensure_admin.py  cria/atualiza o superuser a partir do .env
    └── tests/               testes (models, tasks, admin, commands)
```

Resumo por módulo:

| Módulo                 | Responsabilidade                                            |
| ---------------------- | ----------------------------------------------------------- |
| `manage.py`            | CLI do Django — todo comando roda por aqui                  |
| `gestorjornada/`       | "cap": settings, URLs raiz, WSGI/ASGI. Não contém lógica    |
| `jornadas/models.py`   | dados: papéis (`Role`), usuário (`User`) e tarefas (`Task`) |
| `jornadas/admin.py`    | expõe os models na interface de administração               |
| `jornadas/views.py`    | páginas da aplicação (ainda a serem criadas)                |
| `jornadas/migrations/` | versiona o esquema do banco — commitar junto com o model    |
| `jornadas/tests/`      | suíte de testes (`python3 manage.py test`)                  |

## Fluxo do aplicativo

Fluxo ideal da aplicação com base nos perfis definidos por `User.role` (`user`
ou `admin`):

**Usuário (`role = user`)**

1. Acessa a aplicação → Tela de login
2. Faz login → Tela inicial ("Minhas jornadas")
3. Clica em "Nova tarefa" → Formulário (atividade, início, término)
4. Envia o formulário → Django valida que `término > início` (constraint no
   banco)
5. Válido → Task salva vinculada ao próprio usuário
6. Redirecionado ao histórico → Visualiza próprias tarefas, duração e total

**Gestor / Admin (`role = admin`)**

1. Acessa a aplicação → Tela de login (ou `/admin/`)
2. Faz login → Painel do gestor
3. Painel → Consulta tarefas de todos os funcionários
4. Painel → Filtra por período e por funcionário
5. Filtrados → Gera gráficos de produtividade
6. Filtrados → Consulta via API para relatórios

> [!NOTE]
> Estado atual: apenas `/admin/` está implementado em `gestorjornada/urls.py`;
> `jornadas/views.py` e `jornadas/urls.py` (app) ainda não existem. O fluxo
> acima é o alvo da [lista de implementação](#lista-de-implementação). A tela
> `/admin` é a padrão Django

## Tecnologias

- Django
- Sqlite
- Docker

## Como rodar

### Dev

Utilize
[a documentação oficial](https://docs.djangoproject.com/en/6.1/intro/install/)
como base:

- O Git inclui `manage.py`, que é o principal ponto de execução de comandos como
  runserver: `pyton3 manage.py runserver`, que cria um servidor local para
  avaliar as mudanças locais.

### Variáveis de ambiente

Valores de configuração podem ser definidos em um arquivo `.env` na raiz do
projeto (carregado automaticamente via `python-dotenv`). O `.env` **não deve ser
versionado**.

| Variável            | Obrigatória | Padrão  | Descrição                                            |
| ------------------- | ----------- | ------- | ---------------------------------------------------- |
| `ADMIN_USER`        | não         | `admin` | Usuário administrador criado por `ensure_admin`      |
| `ADMIN_PWD`         | sim         | —       | Senha do administrador (use interativa/configuração) |
| `DJANGO_SECRET_KEY` | não*        | —       | Chave secreta; necessária com `DEBUG=False`          |

\* Com `DEBUG=True` e a variável ausente, o Django gera uma chave descartável
por processo — adequado para desenvolvimento, mas sessões não sobrevivem a um
restart.

Após criar o banco ou redefini-lo, crie/atualize o usuário administrador com:

```bash
python3 manage.py ensure_admin
```

### Formatação e lint de código (Ruff)

Utilizamos [Ruff](https://github.com/astral-sh/ruff) (`ruff format` +
`ruff check`) como formatador e linter. Não existe um formatador nativo no
Python ou no Django — o padrão da comunidade é o Black, e o Ruff é a alternativa
mais moderna: formato compatível com o Black (>99,9% idêntico), muito mais
rápido, e que também faz lint e ordenação de imports em uma única ferramenta. A
configuração fica em `pyproject.toml` sob `[tool.ruff]`.

```bash
# dependências de desenvolvimento
python3 -m pip install -r requirements-dev.txt

ruff check .         # lint
ruff check . --fix   # corrige automaticamente
ruff format .        # formata todos os arquivos
ruff format --check .  # verifica no CI sem alterar arquivos
```

**Ordem recomendada:** rode `ruff check --fix` **antes** de `ruff format`
(sempre que o formatador entrar em ação, o lint já esteve atualizado).

> [!NOTE]
> Se usar o VS Code, instale a extensão _Ruff_ e configure como formatador
> padrão com _Format on Save_ para formatar automaticamente ao salvar.
