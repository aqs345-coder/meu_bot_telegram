import sqlite3


def init_db():
    conn = sqlite3.connect('registros_estagio.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_estagio TEXT,
            horario TEXT,
            local TEXT,
            atividade TEXT,
            conteudo TEXT,
            objetivos TEXT,
            descricao TEXT,
            dificuldades TEXT,
            aspectos_positivos TEXT,
            caminho_anexo TEXT
            )
        '''
    )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
