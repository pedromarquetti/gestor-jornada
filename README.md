# Bem vindo ao Gestão de Jornada

<!--toc:start-->

- [Bem vindo ao Gestão de Jornada](#bem-vindo-ao-gestão-de-jornada)
  - [Objetivo](#objetivo)
    - [Lista de implementação](#lista-de-implementação)
  - [Tecnologias](#tecnologias)

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
