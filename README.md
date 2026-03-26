# Agenda Fácil

## Atividade Inicial do Projeto - Definição e Planejamento

Este repositório contém a etapa inicial do projeto de Quality Assurance, com foco na definição do sistema, organização das ideias e planejamento das próximas fases.

Nesta etapa, o objetivo principal nao e programar, mas sim estruturar o trabalho de forma clara para facilitar o desenvolvimento e os testes futuramente.

## 1. Objetivo da Atividade

O grupo deve iniciar o projeto organizando as ideias, definindo o sistema e estruturando o planejamento inicial.

Essa fase funciona como a base do projeto: quanto melhor ela for construída, mais facil sera a execução das etapas seguintes.

## 2. Tema

**Sistema de Agendamento: atendimento de consultorio**

## 3. Identificação do Grupo

**Nome do grupo:** BUGBUSTERS

### Integrantes

- Vinicius Gabriel Rodrigues Silva
- Vitor Souza Ferreira
- Camila Oliveira Nascimento
- Bruno Menezes Gomes

## 4. Descrição do Sistema

### O que o sistema faz

O sistema permite que pacientes realizem cadastro, façam login e agendem consultas medicas com data e horario disponiveis. Tambem permite visualizar, remarcar e cancelar consultas.

### Quem utilizará o sistema

- Pacientes
- Recepcionistas/clinicas
- Medicos, dependendo do escopo definido pelo grupo

### Qual problema o sistema resolve

O sistema organiza o processo de marcação de consultas, evita conflitos de horarios, reduz erros manuais e facilita o controle dos agendamentos.

## 5. Funcionalidades Principais

- Cadastro de usuario
- Login de usuario
- Agendamento de consulta
- Visualização das consultas agendadas
- Cancelamento de consulta
- Remarcação de consulta
- Consulta de horarios disponiveis
- Cadastro de medicos e especialidades
- Busca por medico ou especialidade
- Confirmação de agendamento

## 6. O que será testado

- No cadastro de paciente e data do exame, os dados devem ser armazenados corretamente, sem permitir informações invalidas ou campos obrigatorios em branco.
- Na verificação de disponibilidade, o sistema deve apresentar apenas horarios realmente livres, evitando conflitos com consultas ja agendadas.
- Na confirmação e cancelamento da consulta, o sistema deve atualizar corretamente o status da consulta, refletindo imediatamente as mudanças no agendamento.
- No cadastro de exames, deve ser possivel registrar novos exames com todas as informações necessarias, sem duplicidade ou erro de dados.
- No cadastro do(a) doutor(a), os dados devem ser inseridos corretamente e ficar disponiveis para associação com consultas e exames.

## 7. Tecnologias e Ferramentas

### Backend

O backend sera desenvolvido em Python, utilizando o framework FastAPI para criação da API REST do sistema.

Para validação de dados e definição dos modelos de entrada e saida, sera utilizado o Pydantic.

Na comunicação com o banco de dados, sera utilizado o SQLAlchemy como ORM, facilitando o mapeamento das tabelas e operações de persistencia.

Para controle de versões do banco de dados, sera utilizado o Alembic, permitindo gerenciar migrations de forma organizada.

### Frontend

O frontend sera desenvolvido com Vue.js, utilizando Nuxt 4 para estruturar a aplicação de forma moderna e organizada.

Para a interface visual, sera utilizado `shadcn/ui`, com foco em componentes reutilizaveis, acessiveis e com aparência profissional.

### Banco de Dados

O banco de dados escolhido sera o PostgreSQL, por ser robusto, confiavel e amplamente utilizado em sistemas reais.

### Conteinerização e Ambiente

Sera utilizado Docker para subir e gerenciar os containers da aplicação, incluindo a API e o banco de dados, facilitando a configuração do ambiente e a padronização do projeto entre os integrantes do grupo.

### Ferramentas de Apoio

- GitHub para versionamento e colaboração do projeto
- VS Code como ambiente de desenvolvimento
- Postman ou Insomnia para testes das rotas da API
- Docker Compose para orquestração dos serviços

## 8. Organização do Grupo

### Responsabilidades

- Desenvolvimento: Vinicius, Bruno e Vitor
- Testes: Camila e Vitor
- Documentação: Camila
- Apresentação: Vitor e Vinicius

## 9. Repositório no GitHub

Conforme solicitado na atividade:

- O repositório do projeto ja foi criado no GitHub
- O nome do projeto e **Agenda Fácil**
- Todos os integrantes ja foram adicionados como colaboradores
- Este arquivo `README.md` foi organizado com as informações iniciais do projeto
