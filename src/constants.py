# flake8: noqa: E501
from telegram import ReplyKeyboardMarkup

DATA, HORARIO, LOCAL, ATIVIDADE, CONTEUDO, OBJETIVOS, DESCRICAO, DIFICULDADES, ASPECTOS_P, ANEXOS, CONFIRMACAO = range(
    11)

HORARIO_PADRAO = "06:00 às 11:00"

LOCAL_PADRAO = "Armazém Fitness"

ATIVIDADE_PADRAO = "Musculação"

MSG_BOAS_VINDAS = ("👋 **Olá! Seja muito bem-vindo(a) ao seu Assistente de Estágio!**\n\n"
                   "Estou aqui para facilitar sua vida e garantir que cada aprendizado da sua jornada fique bem guardado. 🚀\n\n"
                   "✨ **Vamos começar?**\n"
                   "Para registrar suas atividades de hoje, é só enviar:\n"
                   "▶️ /register\n\n"
                   "❓ **Precisa de uma ajudinha?**\n"
                   "Para ver instruções e dicas, envie:\n"
                   "ℹ️ /help")

MSG_START = ("🚀 *Iniciando Registro de Estágio*\n\n"
             "Em que data (DD/MM/AAAA) você deseja adicionar as informações?\n"
             "_(Dica: você pode digitar 'hoje')_")

MSG_RESUMO = ("📋 *Revise seus dados:*\n\n")


MSG_HELP = ("🤖 **MANUAL DO ASSISTENTE DE ESTÁGIO**\n\n"
            "Aqui está tudo o que você pode fazer:\n\n"

            "📝 **1. Criar Novo Registro**\n"
            "• Clique em '📝 Registrar Dia' ou digite `/register`.\n"
            "• O bot fará perguntas sequenciais (Data, Conteúdo, Objetivos...).\n"
            "• **Regra:** Apenas 1 registro por data é permitido.\n"
            "• Se tentar registrar uma data repetida, o bot oferecerá um atalho para ver/editar o antigo.\n\n"

            "📂 **2. Histórico e Visualização**\n"
            "• Clique em '📂 Ver Histórico' para ver seus registros salvos.\n"
            "• Navegue clicando nos botões das datas (ex: 📅 30/01/2026).\n"
            "• Você verá todos os detalhes, incluindo a foto/anexo.\n\n"

            "✏️ **3. Editar Registros (Novo!)**\n"
            "Errou algo? Não tem problema!\n"
            "1. Vá em '📂 Ver Histórico'.\n"
            "2. Clique na data desejada.\n"
            "3. Clique no botão **'✏️ Editar'**.\n"
            "4. Escolha exatamente qual campo quer alterar (ex: Conteúdo, Horário, Anexo).\n\n"

            "❌ **4. Cancelar a qualquer momento**\n"
            "• Em todas as perguntas, haverá um botão **'❌ Cancelar'** logo abaixo da mensagem.\n"
            "• Clique nele para interromper o cadastro imediatamente sem salvar nada.\n\n"

            "💾 **5. Exportar Dados (Novo!)**\n"
            "• Digite `/export` para baixar todos os seus dados.\n"
            "• Você pode escolher entre apenas planilha (Excel) ou backup completo com fotos.\n\n"

            "💡 **Dicas Extras:**\n"
            "• **Datas:** Aceito formatos como `25/02/2026`, `25/02/26` ou apenas `hoje`.\n"
            "• **Anexos:** Você pode enviar fotos ou arquivos (PDF/DOC) como comprovante.\n"
            "• **Segurança:** Seus dados estão salvos em nuvem segura (PostgreSQL).")

ROTAS = {
    "Data":       (DATA,       "📅 Qual a nova data? (Atual: {})", "data_estagio"),
    "Horário":    (HORARIO,    "⌚ Novo horário (Atual: {})",      "horario"),
    "Local":      (LOCAL,      "📍 Novo local (Atual: {})",        "local"),
    "Atividade":  (ATIVIDADE,  "🏋️‍♂️ Nova atividade (Atual: {})",   "atividade"),
    "Conteúdo":   (CONTEUDO,   "📝 Digite o novo conteúdo:",       None),
    "Objetivos":  (OBJETIVOS,  "🎯 Digite os novos objetivos:",    None),
    "Descrição":  (DESCRICAO,  "📖 Digite a nova descrição:",      None),
    "Dificuldades": (DIFICULDADES, "⚠️ Digite as novas dificuldades:", None),
    "Aspectos":   (ASPECTOS_P, "✨ Digite os novos pontos positivos:", None),
    "Anexo":      (ANEXOS,     "📎 Envie o novo arquivo:",         None),
}

SQL = ("""
            INSERT INTO registros (
                user_id, data_estagio, horario, local, tipo_atividade,
                conteudo, objetivos, descricao, dificuldades, aspectos_positivos, caminho_anexo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)

SQL_UPDATE = ("""
                UPDATE registros SET
                    data_estagio=%s, horario=%s, local=%s, tipo_atividade=%s,
                    conteudo=%s, objetivos=%s, descricao=%s, 
                    dificuldades=%s, aspectos_positivos=%s, caminho_anexo=%s
                WHERE id=%s AND user_id=%s
            """)
TECLADO_INICIAL = ReplyKeyboardMarkup(
    [["📝 Registrar Dia"], ["📂 Ver Histórico"], ["💾 Exportar"]],
    resize_keyboard=True,
    one_time_keyboard=True
)

TECLADO_CANCELAR = ReplyKeyboardMarkup(
    [["❌ Cancelar"]],
    resize_keyboard=True
)

TECLADO_CONFIRMACAO = ReplyKeyboardMarkup(
    [
        ["✅ SALVAR NO BANCO"],
        ["📅 Data", "⌚ Horário"],
        ["📍 Local", "🏋️‍♂️ Atividade"],
        ["📝 Conteúdo", "🎯 Objetivos"],
        ["📖 Descrição", "⚠️ Dificuldades"],
        ["✨ Aspectos", "📎 Anexo"],
        ["❌ Cancelar"]
    ],
    resize_keyboard=True
)
