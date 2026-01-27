# 🤖 Assistente de Diário de Bordo - Telegram Bot

Este é um bot de Telegram desenvolvido em **Python** para automatizar a coleta de informações e a organização de registros diários de estágio. O bot guia o usuário através de um fluxo de perguntas, armazena as respostas em um banco de dados local (JSON) e organiza as fotos enviadas.

![Trecho do módulo principal]
<img width="720" height="1080" alt="image" src="https://github.com/user-attachments/assets/b6a0edb2-0a67-4c04-9f46-3318e9c71b42" />


## 🚀 Objetivo

Facilitar o preenchimento diário do diário de bordo, garantindo que nenhum detalhe (objetivos, dificuldades, aspectos positivos) seja esquecido, permitindo a posterior exportação dos dados para um modelo oficial em Word.

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **python-telegram-bot:** Framework para interação com a API do Telegram.
- **python-dotenv:** Gestão de variáveis de ambiente e segurança de tokens.
- **JSON:** Armazenamento persistente de dados.

## 📋 Funcionalidades

- [x] **Tratamento inteligente de datas:** Reconhece entradas como "hoje", "hj" ou diversos formatos numéricos.
- [x] **Fluxo de Conversação (ConversationHandler):** Guia o usuário passo a passo.
- [x] **Captura de Anexos:** Recebe e organiza fotos das atividades.
- [x] **Dados Automáticos:** Registra horário e local de preenchimento de forma autônoma.
- [x] **Segurança:** Uso de arquivos `.env` para proteção de credenciais.

## 📂 Estrutura do Projeto

```text
├── main.py           # Ponto de entrada e configuração do bot
├── handlers.py       # Lógica das funções e comandos
├── constants.py      # Definição de estados e textos fixos
├── .env              # (Oculto) Token da API do Telegram
├── .gitignore        # Arquivos ignorados pelo Git
└── registros_estagio.json # Banco de dados local
```
