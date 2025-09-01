# 🌍 WordReference API (Custom Version)

This project is a modified version of [n-wissam/wordreference](https://github.com/n-wissam/wordreference).
It provides a simple REST API and CLI to fetch translations, examples, and audio files directly from [WordReference.com](https://www.wordreference.com).

---

## 🚀 Features

* REST API built with **Flask**
* **Rate limiting** with `flask-limiter`
* Fetch translations, definitions, examples, and audio files
* Supports many bilingual dictionaries (EN ↔ FR, EN ↔ ES, etc.)
* CLI tool for translations in the terminal
* **LRU cache** for performance optimization

---

## 📂 Project Structure

```
api/
├── app.py           # Flask API (REST endpoints)
├── cli.py           # Command-line interface
├── presentation.py  # CLI output formatting
├── scraper.py       # WordReference scraping & parsing
├── variables.py     # URL and dictionary codes
requirements.txt     # Dependencies
```

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
python -m venv venv
source venv/bin/activate   # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## ▶️ Usage

### 1. Run the API

```bash
cd api
python app.py
```

The API will be available at:
👉 `http://127.0.0.1:5000`

---

### 2. Available Endpoints

#### Health check

```http
GET /
```

Response:

```json
{ "status": "API is running" }
```

#### Translate a word

```http
GET /translate?word=hello&dict=enfr
```

Parameters:

* `word` *(str, required)*: the word to translate
* `dict` *(str, required)*: dictionary code (e.g., `enfr`, `enes`, `fren`, …)
* `meanings` *(list\[int], optional)*: filter by specific meaning numbers

Example response:

```json
{
  "translation": {
    "1": {
      "word": "hello",
      "definition": "bonjour",
      "meanings": ["greeting", "hi"],
      "examples": ["Hello, how are you?", "Bonjour, comment ça va ?"]
    }
  },
  "audio_links": [
    "https://www.wordreference.com/audio/en/hello.mp3"
  ]
}
```

---

### 3. CLI Usage

List available dictionaries:

```bash
python cli.py -l
```

Translate a word:

```bash
python cli.py enfr hello
```

With audio download:

```bash
python cli.py enfr hello -a
```

---

## 📖 Supported Dictionaries

Examples:

* `enfr` → English ↔ French
* `enes` → English ↔ Spanish
* `fren` → French ↔ English
* `esfr` → Spanish ↔ French

The full list can be found in [`variables.py`](api/variables.py).

---

## 🔒 Rate Limiting

* **30 requests per minute per IP** (global default)
* **10 requests per second per IP** (for `/translate` endpoint)

This helps prevent overloading WordReference.

---

## 🙏 Credits

* Original project: [n-wissam/wordreference](https://github.com/n-wissam/wordreference)
* Modifications & improvements: *your work* 🚀

