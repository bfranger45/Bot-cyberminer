from flask import Flask, render_template, request, jsonify
import os
from supabase import create_client, Client

app = Flask(__name__)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/estado/<int:user_id>', methods=['GET'])
def obtener_estado(user_id):
    try:
        response = supabase.table('users').select('*').eq('telegram_id', user_id).execute()
        data = response.data
        if data and len(data) > 0:
            return jsonify(data[0])
        else:
            # Crear usuario por defecto si es su primera vez
            nuevo_usuario = {
                'telegram_id': user_id,
                'puntos': 0.0,
                'por_clic': 1,
                'auto_mineria_por_segundo': 0
            }
            supabase.table('users').insert(nuevo_usuario).execute()
            return jsonify(nuevo_usuario)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sincronizar', methods=['POST'])
def sincronizar():
    try:
        data = request.json
        user_id = data.get('user_id')
        puntos = data.get('puntos')
        
        # Actualiza el puntaje en la base de datos de forma limpia
        supabase.table('users').update({'puntos': puntos}).eq('telegram_id', user_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/comprar_mejora', methods=['POST'])
def comprar_mejora():
    try:
        data = request.json
        user_id = data.get('user_id')
        tipo = data.get('tipo')

        res = supabase.table('users').select('*').eq('telegram_id', user_id).execute()
        if not res.data:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'})
        
        user = res.data[0]
        puntos = user['puntos']
        por_clic = user['por_clic']
        auto = user['auto_mineria_por_segundo']

        if tipo == 'clic':
            costo = 50
            if puntos >= costo:
                puntos -= costo
                por_clic += 1
            else:
                return jsonify({'success': False, 'error': 'Puntos insuficientes'})
        elif tipo == 'auto':
            costo = 200
            if puntos >= costo:
                puntos -= costo
                auto += 5
            else:
                return jsonify({'success': False, 'error': 'Puntos insuficientes'})

        supabase.table('users').update({
            'puntos': puntos,
            'por_clic': por_clic,
            'auto_mineria_por_segundo': auto
        }).eq('telegram_id', user_id).execute()

        return jsonify({
            'success': True,
            'user': {
                'puntos': puntos,
                'por_clic': por_clic,
                'auto_mineria_por_segundo': auto
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

