import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Base de datos temporal en memoria (para producción se conecta con Supabase)
usuarios = {}

def obtener_usuario(user_id):
    if user_id not in usuarios:
        usuarios[user_id] = {
            "puntos": 0,
            "por_clic": 1,
            "auto_mineria_por_segundo": 0
        }
    return usuarios[user_id]

@app.route("/")
def index():
    # Renderiza la interfaz gráfica del juego
    return render_template("index.html")

@app.route("/api/estado/<user_id>", methods=["GET"])
def obtener_estado(user_id):
    user = obtener_usuario(user_id)
    return jsonify(user)

@app.route("/api/click", methods=["POST"])
def registrar_click():
    data = request.json or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "ID invalido"}), 400

    user = obtener_usuario(user_id)
    user["puntos"] += user["por_clic"]
    return jsonify({"success": True, "puntos": user["puntos"]})

@app.route("/api/comprar_mejora", methods=["POST"])
def comprar_mejora():
    data = request.json or {}
    user_id = data.get("user_id")
    tipo = data.get("tipo") # "clic" o "auto"

    user = obtener_usuario(user_id)

    if tipo == "clic" and user["puntos"] >= 50:
        user["puntos"] -= 50
        user["por_clic"] += 1
        return jsonify({"success": True, "user": user})
    
    elif tipo == "auto" and user["puntos"] >= 200:
        user["puntos"] -= 200
        user["auto_mineria_por_segundo"] += 5
        return jsonify({"success": True, "user": user})

    return jsonify({"success": False, "error": "Puntos insuficientes"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

