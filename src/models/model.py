import sqlite3
import hashlib
import bcrypt

def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def criar_tabela():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def cadastrar_usuario(usuario, senha):
    hash_senha = gerar_hash_senha(senha)
    try:
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, hash_senha))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verificar_login(usuario, senha):
    hash_senha = gerar_hash_senha(senha)
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, hash_senha))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def get_all_users():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users')
        return [{'username': row[0]} for row in cursor.fetchall()]

def update_user(username, new_password):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        if not cursor.fetchone():
            return False
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('UPDATE users SET password = ? WHERE username = ?', 
                       (hashed_password, username))
        conn.commit()
        return True

def delete_user(username):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        if not cursor.fetchone():
            return False
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        return True