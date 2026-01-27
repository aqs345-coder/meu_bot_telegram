# flake8: noqa: F405
# type: ignore
from datetime import datetime

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from constants import *


async def mensagem_informativa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (MSG_BOAS_VINDAS)
    await update.message.reply_text(msg)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        MSG_START,
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
