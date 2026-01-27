# flake8: noqa: E501
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

load_dotenv()

TOKEN = os.getenv('TOKEN')

# ESTADOS DA CONVERSA
DATA, HORARIO, ATIVIDADE, CONTEUDO, OBJETIVOS, DESCRICAO, DIFICULDADES, ASPECTOS_P, ANEXOS = range(
    9)


async def mensagem_informativa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 Olá! Eu sou o seu Assistente de Estágio.\n\n"
        "No momento, não temos nenhum registro em andamento. "
        "Para começar a anotar as atividades do seu estágio, envie o comando:\n\n"
        "▶️ /start\n\n"
        "Para ver os comandos e as instruções, envie o comando:\n\n"
        "ℹ️ /help"
    )
    await update.message.reply_text(msg)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "🚀 *Iniciando Registro de Estágio*\n\n"
        "Em que data (DD/MM/AAAA) você deseja adicionar as informações?\n"
        "_(Dica: você pode digitar 'hoje')_",
        parse_mode='Markdown'
    )
    return DATA


async def receber_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text.strip().lower()
    data_final = ""

    if texto_usuario in ["hoje", "hj", "today"]:
        data_final = datetime.now().strftime("%d/%m/%Y")

    else:
        formatos = ["%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d%m%Y", "%d.%m.%Y"]

        for formato in formatos:
            try:
                data_obj = datetime.strptime(texto_usuario, formato)
                data_final = data_obj.strftime("%d/%m/%Y")
                break
            except ValueError:
                continue

    if data_final:
        context.user_data['data_estagio'] = data_final
        await update.message.reply_text(f"Data definida como: {data_final}.\n"
                                        f"Qual foi o conteúdo trabalhado?")
        return CONTEUDO

    else:
        await update.message.reply_text(
            "Não entendi a data. 🤔\n"
            "Por favor, digite 'hoje' ou uma data válida (ex: 27/01/2026)."
        )
        return DATA


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registro cancelado.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *Assistente de Diário de Bordo*\n\n"
        "Este bot ajuda você a registrar suas atividades de estágio de forma organizada.\n\n"
        "*Comandos disponíveis:*\n"
        "/start - Inicia um novo registro diário.\n"
        "/cancel - Cancela o registro que está em andamento.\n"
        "/help - Mostra esta mensagem de ajuda.\n\n"
        "*Como funciona:*\n"
        "1. Digite `/start`.\n"
        "2. Responda às perguntas sobre data, conteúdo, objetivos, etc.\n"
        "3. Envie uma foto para finalizar o registro.\n\n"
        "💡 *Dica:* Na hora da data, você pode apenas digitar 'hoje'!"
    )

    await update.message.reply_text(help_text, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('help', help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, mensagem_informativa))

    print('Iniciando o bot...')
    app.run_polling()
