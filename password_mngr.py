from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (site TEXT, encrypted_password TEXT)''')
    conn.commit()
    conn.close()

class PasswordManager:
    def __init__(self, secret_key):
        self.fernet = Fernet(secret_key)

    def save_password(self, site, password):
        encrypted_password = self.fernet.encrypt(password.encode()).decode()
        conn = sqlite3.connect("passwords.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO passwords (site, encrypted_password) VALUES (?, ?)", (site, encrypted_password))
        conn.commit()
        conn.close()
        return f"Password for {site} saved and encrypted."

    def retrieve_password(self, site):
        conn = sqlite3.connect("passwords.db")
        cursor = conn.cursor()
        cursor.execute("SELECT encrypted_password FROM passwords WHERE site = ?", (site,))
        result = cursor.fetchone()
        conn.close()

        if result:
            encrypted_password = result[0]
            decrypted_password = self.fernet.decrypt(encrypted_password.encode()).decode()
            return f"Decrypted Password for {site}: {decrypted_password}"
        else:
            return f"Password not found for {site}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save_password", methods=["POST"])
def save_password():
    site = request.form.get("site")
    password = request.form.get("password")
    result = password_manager.save_password(site, password)
    return result

@app.route("/retrieve_password", methods=["POST"])
def retrieve_password():
    site = request.form.get("retrieve-site")
    result = password_manager.retrieve_password(site)
    return result

if __name__ == "__main__":
    secret_key = Fernet.generate_key()
    password_manager = PasswordManager(secret_key)
    init_db()
    app.run()
