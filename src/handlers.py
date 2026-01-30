
import os
import sqlite3
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from constants import (ANEXOS, ASPECTOS_P, ATIVIDADE_PADRAO, CONFIRMACAO,
                       CONTEUDO, DATA, DESCRICAO, DIFICULDADES, HORARIO_PADRAO,
                       LOCAL_PADRAO, MSG_BOAS_VINDAS, MSG_HELP, MSG_START,
                       OBJETIVOS, ROTAS, TECLADO_CANCELAR, TECLADO_CONFIRMACAO,
                       TECLADO_INICIAL)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        MSG_BOAS_VINDAS,
        parse_mode='Markdown',
        reply_markup=TECLADO_INICIAL
    )


async def listar_registros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        conn = sqlite3.connect("registros_estagio.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, data_estagio FROM registros WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )

        registros = cursor.fetchall()
        conn.close()

        if not registros:
            await update.message.reply_text(
                "📭 **Nenhum registro encontrado.**\n"
                "Comece clicando em '📝 Registrar Dia'!",
                parse_mode='Markdown'
            )
            return

        teclado = []
        for reg in registros:
            id_reg = reg[0]
            data_reg = reg[1]
            teclado.append([InlineKeyboardButton(
                f"📅 {data_reg}", callback_data=f"Ver {id_reg}")])

        reply_markup = InlineKeyboardMarkup(teclado)

        await update.message.reply_text(
            "📂 **Seus Registros:**\nClique em uma data para ver os detalhes:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    except Exception as e:
        print(f"Erro ao listar os registros: {e}")
        await update.message.reply_text(f"❌ Erro ao buscar registros.")


async def exibir_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = context.user_data
    status_anexo = "✅ Recebido" if dados.get('caminho_anexo') else "❌ Pendente"

    msg = (
        f"📋 **REVISÃO DO REGISTRO**\n\n"
        f"📅 **Data:** {dados.get('data_estagio')}\n"
        f"⌚ **Horário:** {dados.get('horario')}\n"
        f"📍 **Local:** {dados.get('local')}\n"
        f"🏋️‍♂️ **Atividade:** {dados.get('atividade')}\n"
        f"📝 **Conteúdo:** {dados.get('conteudo_trabalhado')}\n"
        f"🎯 **Objetivos:** {dados.get('objetivos_aula')}\n"
        f"📖 **Descrição:** {dados.get('descricao')}\n"
        f"⚠️ **Dificuldades:** {dados.get('dificuldades')}\n"
        f"✨ **Aspectos:** {dados.get('aspectos_positivos')}\n"
        f"📎 **Anexo:** {status_anexo}\n\n"
        f"O que deseja fazer?\n\n"
        f"Para alterar alguma informação, clique na opção correspondente."
    )

    await update.message.reply_text(
        msg,
        parse_mode='Markdown',
        reply_markup=TECLADO_CONFIRMACAO)


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

    if not data_final:
        await update.message.reply_text(
            "Não entendi a data. 🤔\n"
            "Por favor, digite 'hoje' ou uma data válida (ex: 27/01/2026)."
        )
        return DATA

    context.user_data['data_estagio'] = data_final

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Data atualizada!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

    await update.message.reply_text(
        f"📝 Anotei: '{data_final}'\n\n"
        "Agora, fale sobre os conteúdos trabalhados.\n"
    )
    return CONTEUDO


async def receber_conteudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Conteúdo atualizado!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

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

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Objetivos atualizados!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

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

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Descrição atualizada!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

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

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Dificuldades atualizadas!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

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

    context.user_data['editando'] = True

    if context.user_data.get('caminho_anexo'):
        await exibir_resumo(update, context)
        return CONFIRMACAO

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


async def receber_horario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['horario'] = update.message.text
    await update.message.reply_text("✅ Horário atualizado!")
    await exibir_resumo(update, context)
    return CONFIRMACAO


async def receber_local(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['local'] = update.message.text
    await update.message.reply_text("✅ Local atualizado!")
    await exibir_resumo(update, context)
    return CONFIRMACAO


async def receber_atividade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['atividade'] = update.message.text
    await update.message.reply_text("✅ Atividade atualizada!")
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


async def salvar_no_banco_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = context.user_data
    user = update.effective_user

    try:
        conn = sqlite3.connect("registros_estagio.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO registros (
                user_id, data_estagio,
                horario, local, atividade,
                conteudo, objetivos, descricao,
                dificuldades, aspectos_positivos, caminho_anexo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.id, dados.get('data_estagio'),
                dados.get('horario'), dados.get(
                    'local'), dados.get('atividade'),
                dados.get('conteudo_trabalhado'), dados.get(
                    'objetivos_aula'), dados.get('descricao'),
                dados.get('dificuldades'), dados.get(
                    'aspectos_positivos'), dados.get('caminho_anexo')
            )
        )
        conn.commit()
        conn.close()

        await update.message.reply_text("✅ Registro salvo com sucesso!", reply_markup=TECLADO_INICIAL)
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text("Erro ao salvar o registro.")
        print(e)
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registro cancelado.", reply_markup=TECLADO_INICIAL)
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (MSG_HELP)

    await update.message.reply_text(help_text, parse_mode='Markdown')
