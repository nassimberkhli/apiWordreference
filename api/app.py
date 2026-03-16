from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .scraper import fetch_translation

app = Flask(__name__)
CORS(app)

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

    print(f"[translate] word={word} dict={dict_code} meanings={specific_meanings}")

    try:
        translation, audio_links = fetch_translation(word, dict_code, specific_meanings)
        print(
            f"[translate] translation_count={len(translation)} audio_count={len(audio_links)}"
        )

        if not translation:
            return jsonify(
                {
                    "error": "Translation not available at the moment.",
                    "debug": {
                        "word": word,
                        "dict": dict_code,
                        "specific_meanings": specific_meanings,
                        "translation_count": 0,
                    },
                }
            ), 503

        return jsonify({"translation": translation, "audio_links": audio_links})
    except Exception as e:
        print(f"[translate] exception: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
