# flake8: noqa: E501
# ESTADOS DA CONVERSA
DATA, HORARIO, LOCAL, ATIVIDADE, CONTEUDO, OBJETIVOS, DESCRICAO, DIFICULDADES, ASPECTOS_P, ANEXOS = range(
    10)

MSG_BOAS_VINDAS = ("👋 Olá! Eu sou o seu Assistente de Estágio.\n\n"
                   "No momento, não temos nenhum registro em andamento. "
                   "Para começar a anotar as atividades do seu estágio, envie o comando:\n\n"
                   "▶️ /register\n\n"
                   "Para ver os comandos e as instruções, envie o comando:\n\n"
                   "ℹ️ /help")

MSG_START = ("🚀 *Iniciando Registro de Estágio*\n\n"
             "Em que data (DD/MM/AAAA) você deseja adicionar as informações?\n"
             "_(Dica: você pode digitar 'hoje')_")

MSG_HELP = ("🤖 *Assistente de Diário de Bordo*\n\n"
            "Este bot ajuda você a registrar suas atividades de estágio de forma organizada.\n\n"
            "*Comandos disponíveis:*\n"
            "/register - Inicia um novo registro diário.\n"
            "/cancel - Cancela o registro que está em andamento.\n"
            "/help - Mostra esta mensagem de ajuda.\n\n"
            "*Como funciona:*\n"
            "1. Digite `/register`.\n"
            "2. Responda às perguntas sobre data, conteúdo, objetivos, etc.\n"
            "3. Envie uma foto para finalizar o registro.\n\n"
            "💡 *Dica:* Na hora da data, você pode apenas digitar 'hoje'!")
