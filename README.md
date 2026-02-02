# 🤖 Assistente de Diário de Bordo - Telegram Bot

Este é um bot de Telegram avançado, desenvolvido em **Python**, projetado para gerenciar o ciclo de vida completo de registros de estágio. Diferente de bots simples de resposta automática, este projeto implementa uma **Máquina de Estados Finita** para guiar o usuário, persistência de dados em nuvem via **PostgreSQL** e uma interface interativa baseada em botões (Inline Keyboards).

![Trecho do módulo principal]

<p align="center">
  <img src="https://github.com/user-attachments/assets/b6a0edb2-0a67-4c04-9f46-3318e9c71b42" width="600" alt="Demonstração do Bot">
</p>

![Trecho do conversa inicial]

<p align="center">
  <img src="https://github.com/user-attachments/assets/65fa5297-1b93-466f-982e-e47372e595b9" width="600" alt="Demonstração do Bot">
</p>

## 🚀 Objetivo

Facilitar o preenchimento diário do diário de bordo com validação de dados em tempo real, garantindo a integridade das informações (objetivos, dificuldades, anexos) e permitindo a gestão completa (criação, leitura, edição e exclusão) diretamente pela interface do chat.

## 🧠 Complexidade e Arquitetura

O projeto foi estruturado seguindo princípios de **Clean Code** e modularização, separando responsabilidades entre conexão de banco, lógica de negócios e handlers de interface.

- **Gerenciamento de Estado (ConversationHandler):** O bot utiliza um fluxo complexo que permite ao usuário navegar entre etapas, cancelar operações a qualquer momento (`allow_reentry`) e retomar contextos.
- **Interatividade Assíncrona (Callbacks):** Uso intensivo de `CallbackQueryHandler` para criar menus dinâmicos, paginação de histórico e ações de edição/exclusão sem poluir o chat com novas mensagens.
- **Integridade de Dados:** Implementação de constraints SQL para impedir registros duplicados no mesmo dia e validação robusta de formatos de data.
- **Robustez e Logs:** Sistema de logging configurado (`RotatingFileHandler`) para rastreamento de erros em produção e tratamento de exceções em todas as interações com o banco de dados.
- **Keep-Alive System:** Implementação de um servidor Flask em thread paralela para manter o bot ativo em ambientes de deploy Serverless (como Render Free Tier).

## 🛠️ Tecnologias e Stack

- **Linguagem:** Python 3.11+
- **Core Framework:** `python-telegram-bot` (Wrapper assíncrono da API do Telegram).
- **Banco de Dados:** **PostgreSQL** (Hospedado no Neon Tech).
- **Driver SQL:** `psycopg2-binary` para conexões seguras e performáticas.
- **Infraestrutura:** Deploy configurado para **Render** (Web Service).
- **Monitoramento:** `logging` nativo com rotação de arquivos.
- **Outros:** `python-dotenv` (Segurança), `Flask` (Health check).

## 📋 Funcionalidades Implementadas (CRUD Completo)

### 📝 Criação (Create)

- [x] **Fluxo Guiado:** Perguntas sequenciais para coleta de dados.
- [x] **Tratamento de Datas:** Reconhece "hoje", "hj" e formatos numéricos variados.
- [x] **Upload de Anexos:** Gestão de fotos e documentos com renomeação automática baseada em ID e Timestamp.

### 📂 Leitura (Read)

- [x] **Histórico Interativo:** Listagem de registros anteriores via botões Inline.
- [x] **Visualização Detalhada:** Exibição formatada dos dados recuperados do banco, incluindo download da foto associada.

### ✏️ Edição (Update)

- [x] **Edição Granular:** O usuário pode alterar campos específicos (ex: apenas "Conteúdo" ou "Horário") de um registro passado.
- [x] **Carregamento de Contexto:** O bot recupera os dados antigos e preenche a memória para facilitar a edição.

### 🗑️ Exclusão (Delete)

- [x] **Exclusão Segura:** Sistema de confirmação em duas etapas para evitar cliques acidentais.
- [x] **Limpeza Completa:** Remove o registro do banco SQL e apaga o arquivo físico do servidor.

## 📂 Estrutura do Projeto

```text
├── src/
│   ├── main.py           # Entry point, configuração do bot e Keep-Alive
│   ├── handlers.py       # Lógica de negócios (CRUD) e tratamento de mensagens
│   ├── database.py       # Gerenciamento de conexão PostgreSQL e Init do DB
│   ├── constants.py      # Textos, Queries SQL e Estados da Conversa
│   ├── logger_setup.py   # Configuração profissional de Logs
│   └── keep_alive.py     # Servidor Flask para manter o bot online
├── .env                  # Variáveis de ambiente (Token, DB URL)
├── requirements.txt      # Dependências do projeto
└── Procfile              # Configuração de deploy para o Render

```
