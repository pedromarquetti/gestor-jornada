# Bem vindo ao Gestão de Jornada

<!--toc:start-->

- [Bem vindo ao Gestão de Jornada](#bem-vindo-ao-gestão-de-jornada)
  - [Objetivo](#objetivo)
    - [Lista de implementação](#lista-de-implementação)
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

- [ ] **Tela de administração** - Tela utilizada por gestores para avaliar,
      através de gráficos, a produtividade de funcionários.
- [ ] **Tela de cadastro** - Tela para cadastro de produtividade com campos de
      atividade realizada, inicio e término.
- [ ] **DB** - Estrutura do banco de dados para armazenamento.
- [ ] **API** - Configuração de API básica para consulta rápida de dados.
- [ ] **Docker** - Configuração de Dockerfile para deploy.

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
