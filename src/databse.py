import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "A variável de ambiente 'DATABASE_URL' não está definida.")
    return psycopg2.connect(url)


def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_estagio VARCHAR(20),
                horario VARCHAR(50),
                local VARCHAR(100),
                tipo_atividade VARCHAR(100),
                conteudo TEXT,
                objetivos TEXT,
                descricao TEXT,
                dificuldades TEXT,
                aspectos_positivos TEXT,
                caminho_anexo TEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Tabela PostgreeSQL verificada.")

    except Exception as e:
        print(f"Erro ao verificar tabale: {e}")


if __name__ == '__main__':
    init_db()
