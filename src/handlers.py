
import os
import sqlite3
from datetime import datetime

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from constants import *

TECLADO_INICIAL = ReplyKeyboardMarkup(
    [["📝 Registrar Dia"]],
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
        ["📅 Editar Data", "⌚ Horário"],
        ["📍 Local", "🏋️‍♂️ Atividade"],
        ["📝 Conteúdo", "🎯 Objetivos"],
        ["📖 Descrição", "⚠️ Dificuldades"],
        ["✨ Aspectos", "📎 Editar Anexo"],
        ["❌ Cancelar"]
    ],
    resize_keyboard=True
)


async def exibir_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    status_anexo = "✅ Recebido" if d.get('caminho_anexo') else "❌ Pendente"

    msg = (
        f"📋 **REVISÃO DO REGISTRO**\n\n"
        f"📅 **Data:** {d.get('data_estagio')}\n"
        f"⌚ **Horário:** {d.get('horario')}\n"
        f"📍 **Local:** {d.get('local')}\n"
        f"🏋️‍♂️ **Atividade:** {d.get('atividade')}\n"
        f"📝 **Conteúdo:** {d.get('conteudo_trabalhado')}\n"
        f"🎯 **Objetivos:** {d.get('objetivos_aula')}\n"
        f"📖 **Descrição:** {d.get('descricao')}\n"
        f"⚠️ **Dificuldades:** {d.get('dificuldades')}\n"
        f"✨ **Positivos:** {d.get('aspectos_positivos')}\n"
        f"📎 **Anexo:** {status_anexo}\n\n"
        f"O que deseja fazer?"
    )

    await update.message.reply_text(
        msg,
        parse_mode='Markdown',
        reply_markup=TECLADO_CONFIRMACAO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        MSG_BOAS_VINDAS,
        parse_mode='Markdown',
        reply_markup=TECLADO_INICIAL
    )


async def initiate_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['horario'] = HORARIO_PADRAO
    context.user_data['local'] = LOCAL_PADRAO
    context.user_data['atividade'] = ATIVIDADE_PADRAO

    await update.message.reply_text(
        MSG_START,
        parse_mode='Markdown',
        reply_markup=TECLADO_CANCELAR
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


async def receber_conteudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if len(texto_usuario) < 5:
        await update.message.reply_text(
            "Que pouquinho. Vamos detalhar melhor o conteúdo trabalhado?\n"
        )
        return CONTEUDO

    context.user_data['conteudo_trabalhado'] = texto_usuario
    await update.message.reply_text(
        f"📝 Anotei: '{texto_usuario}'\n\n"
        "Agora, fale sobre os objetivos da aula/atividade.\n"
    )
    return OBJETIVOS


async def receber_objetivos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if len(texto_usuario) < 5:
        await update.message.reply_text(
            "Que pouquinho. Vamos detalhar melhor os objetivos da aula?\n"
        )
        return OBJETIVOS

    context.user_data['objetivos_aula'] = texto_usuario
    await update.message.reply_text(
        f"📝 Anotei: '{texto_usuario}'\n\n"
        "Agora, descreva as experiências.\n"
    )
    return DESCRICAO


async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if len(texto_usuario) < 5:
        await update.message.reply_text(
            "Que pouquinho. Vamos detalhar melhor as experiências (observações, práticas, etc.)?\n"
        )
        return DESCRICAO

    context.user_data['descricao'] = texto_usuario
    await update.message.reply_text(
        f"📝 Anotei: '{texto_usuario}'\n\n"
        "Agora, fale sobre as dificuldades enfrentadas.\n"
    )
    return DIFICULDADES


async def receber_dificuldades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if len(texto_usuario) < 5:
        await update.message.reply_text(
            "Que pouquinho. Vamos detalhar melhor as dificuldades enfrentadas?\n"
        )
        return DIFICULDADES

    context.user_data['dificuldades'] = texto_usuario
    await update.message.reply_text(
        f"📝 Anotei: '{texto_usuario}'\n\n"
        "Agora, fale sobre os aspectos positivos.\n"
    )
    return ASPECTOS_P


async def receber_aspectos_positivos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if len(texto_usuario) < 5:
        await update.message.reply_text(
            "Que pouquinho. Vamos detalhar melhor os aspectos positivos?\n"
        )
        return ASPECTOS_P

    context.user_data['aspectos_positivos'] = texto_usuario
    await update.message.reply_text(
        f"📝 Anotei: '{texto_usuario}'\n\n"
        f"Agora, me envie os anexos para {context.user_data['data_estagio']}.\n"
    )
    return ANEXOS


async def receber_anexos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    arquivo = None
    extensao = ""

    if update.message.photo:
        arquivo_id = update.message.photo[-1].file_id
        arquivo = await context.bot.get_file(arquivo_id)
        extensao = ".jpg"

    elif update.message.document:
        arquivo_id = update.message.document.file_id
        arquivo = await context.bot.get_file(arquivo_id)
        nome_orig = update.message.document.file_name
        extensao = os.path.splitext(nome_orig)[1]

    else:
        await update.message.reply_text("Por favor, envie uma imagem ou um documento válido.")
        return ANEXOS

    pasta_anexos = "anexos_estagio"
    os.makedirs(pasta_anexos, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{user.id}_{timestamp}{extensao}"
    caminho_completo = os.path.join(pasta_anexos, nome_arquivo)

    await arquivo.download_to_drive(caminho_completo)

    context.user_data['caminho_anexo'] = caminho_completo
    context.user_data['editando'] = True

    await update.message.reply_text("✅ Anexo recebido!")
    await exibir_resumo(update, context)
    return CONFIRMACAO


async def confirmar_ou_editar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opcao = update.message.text
    dados = context.user_data

    if "✅ SALVAR" in opcao:
        return await salvar_no_banco_final(update, context)
    if "Cancelar" in opcao:
        return await cancel(update, context)

    for palavra_chave, (estado, mensagem, campo_valor) in ROTAS.items():
        if palavra_chave in opcao:
            if campo_valor:
                valor_atual = dados.get(campo_valor, 'Não definido')
                await update.message.reply_text(mensagem.format(valor_atual))
            else:
                await update.message.reply_text(mensagem)
            return estado

    await update.message.reply_text("Opção inválida. Use o teclado abaixo.")
    return CONFIRMACAO


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registro cancelado.", reply_markup=TECLADO_INICIAL)
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (MSG_HELP)

    await update.message.reply_text(help_text, parse_mode='Markdown')
