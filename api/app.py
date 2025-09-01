from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .scraper import fetch_translation

app = Flask(__name__)
CORS(app)

# Limite par défaut : 30 requêtes par minute par IP
limiter = Limiter(get_remote_address, app=app, default_limits=["30 per minute"])

@app.route("/", methods=["GET"])
def status():
    return jsonify({"status": "API is running"}), 200

@app.route("/translate", methods=["GET"])
@limiter.limit("10 per second")
def translate():
    word = request.args.get("word")
    dict_code = request.args.get("dict")
    specific_meanings = request.args.getlist("meanings", type=int)

    if not word or not dict_code:
        return jsonify({"error": "Missing required parameters: 'word' and 'dict'"}), 400

    translation, audio_links = fetch_translation(word, dict_code, specific_meanings)

    if not translation:
        return jsonify({"error": "Translation not available at the moment."}), 503

    return jsonify({
        "translation": translation,
        "audio_links": audio_links
    })

# Ne pas inclure app.run() sur Vercel
if __name__ == "__main__":
    app.run(debug=True)

