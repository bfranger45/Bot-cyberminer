from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

# Configuración de Supabase con las variables de entorno de Render
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route("/")
def index():
    # Renderiza la interfaz grafica del juego
    return render_template("index.html")

@app.route("/api/estado/<int:user_id>", methods=["GET"])
def obtener_usuario(user_id):
    try:
        response = supabase.table('players').select("*").eq('telegram_id', user_id).execute()
        if response.data:
            db_user = response.data[0]
            # Mapeamos los campos de la base de datos a las variables que usa tu interfaz
            user_data = {
                "puntos": db_user['balance'],
                "por_clic": db_user['click_power'],
                "auto_mineria_por_segundo": db_user['auto_power']
            }
            return jsonify(user_data)
        else:
            # Si el usuario no existe en Supabase, lo creamos con valores iniciales
            new_user = {
                "telegram_id": user_id,
                "balance": 0.0,
                "click_power": 1,
                "auto_power": 0
            }
            supabase.table('players').insert(new_user).execute()
            return jsonify({
                "puntos": 0.0,
                "por_clic": 1,
                "auto_mineria_por_segundo": 0
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/click", methods=["POST"])
def registrar_click():
    data = request.json or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "ID invalido"}), 400
    
    try:
        # Obtenemos el usuario actual de Supabase
        response = supabase.table('players').select("*").eq('telegram_id', user_id).execute()
        if response.data:
            current = response.data[0]
            nuevo_puntos = current['balance'] + current['click_power']
            
            # Actualizamos en la base de datos
            supabase.table('players').update({"balance": nuevo_puntos}).eq('telegram_id', user_id).execute()
            return jsonify({"success": True, "puntos": nuevo_puntos})
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/comprar_mejora", methods=["POST"])
def comprar_mejora():
    data = request.json or {}
    user_id = data.get("user_id")
    tipo = data.get("tipo") # "clic" o "auto"
    
    if not user_id:
        return jsonify({"error": "ID invalido"}), 400

    try:
        response = supabase.table('players').select("*").eq('telegram_id', user_id).execute()
        if not response.data:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        current = response.data[0]
        puntos = current['balance']
        click_power = current['click_power']
        auto_power = current['auto_power']
        
        if tipo == "clic" and puntos >= 50:
            puntos -= 50
            click_power += 1
        elif tipo == "auto" and puntos >= 200:
            puntos -= 200
            auto_power += 5
        else:
            return jsonify({"success": False, "error": "Puntos insuficientes"}), 400
            
        # Guardamos los cambios en Supabase
        supabase.table('players').update({
            "balance": puntos,
            "click_power": click_power,
            "auto_power": auto_power
        }).eq('telegram_id', user_id).execute()
        
        user_response = {
            "puntos": puntos,
            "por_clic": click_power,
            "auto_mineria_por_segundo": auto_power
        }
        return jsonify({"success": True, "user": user_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

