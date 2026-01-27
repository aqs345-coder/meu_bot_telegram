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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Sou seu Assistente de Estágio. Vamos registrar o dia de hoje?\n"
        "Em que data (DD/MM/AAAA) você deseja adicionar as informações?"
    )
    return DATA


async def receber_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['data_estagio'] = update.message.text
    await update.message.reply_text("Qual foi o conteúdo trabalhado?")
    return CONTEUDO


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registro cancelado.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)

    print('Iniciando o bot...')
    app.run_polling()
