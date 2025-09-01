import re
import requests
from functools import lru_cache
from bs4 import BeautifulSoup
import unicodedata

from .variables import URL, wr_available_dictionaries

def fetch_translation(word, dict_code, specific_meanings=[]):
    html_content = fetch_page(word, dict_code)
    if html_content:
        return parse_translation(html_content, specific_meanings)
    else:
        return {}, []

@lru_cache(maxsize=500)
def fetch_page(word, dict_code):
    try:
        response = requests.get(f"{URL}/{dict_code}/{word}", timeout=5)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def remove_pos_tags(soup_element):
    for pos_tag in soup_element.find_all('em', class_='POS2'):
        pos_tag.decompose()

def update_translation(row, translation):
    if row.find(class_="ToWrd"):
        meaning_elements = row.find_all('td')
        if meaning_elements and len(meaning_elements) > 2:
            raw_meaning = meaning_elements[2].get_text().strip()
            new_meanings = extract_and_clean_meanings(raw_meaning)
            for m in new_meanings:
                if m and m not in translation["meanings"]:
                    translation["meanings"].append(m)

    elif row.find(class_="FrEx") or row.find(class_="ToEx"):
        if row.find(class_="ToEx"):
            example_text = row.find('td', class_='ToEx').get_text().strip()
        else:
            example_text = row.find('td', class_='FrEx').get_text().strip()
        cleaned_example = clean_text(example_text)
        if cleaned_example:
            translation["examples"].append(cleaned_example)

def parse_translation(html_content, specific_meanings):
    soup = BeautifulSoup(html_content, "html.parser")
    results = soup.find_all("tr", {'class': ['even', 'odd']})
    translations = {}
    translation_number = 0
    translation = None

    for row in results:
        if "more" in row.get('class', [1]):
            continue

        if row.find(class_="FrWrd"):
            remove_pos_tags(row)
            translation = extract_translation(row)
            translation_number += 1

            # ⛔️ Ignore s'il n'y a aucun meaning
            if translation and translation["meanings"] and (
                specific_meanings == [] or translation_number in specific_meanings
            ):
                translations[translation_number] = translation

        elif row.find(class_="ToWrd") or row.find(class_="FrEx") or row.find(class_="ToEx"):
            if translation and (specific_meanings == [] or translation_number in specific_meanings):
                update_translation(row, translation)

    audio_links = extract_audio_links(soup)
    return merge_translation_entries(translations), audio_links

def merge_translation_entries(translations):
    merged = {}
    keys = sorted(translations.keys())
    i = 0
    new_index = 1

    while i < len(keys):
        current = translations[keys[i]]
        merged_entry = {
            "word": current["word"],
            "definition": current["definition"],
            "meanings": list(current["meanings"]),
            "examples": list(current["examples"]),
        }

        j = i + 1
        while j < len(keys):
            next_entry = translations[keys[j]]
            if not next_entry["word"]:
                # Ajouter les meanings
                for m in next_entry["meanings"]:
                    if m not in merged_entry["meanings"]:
                        merged_entry["meanings"].append(m)

                # Ajouter les exemples
                if next_entry["examples"]:
                    for ex in next_entry["examples"]:
                        if ex not in merged_entry["examples"]:
                            merged_entry["examples"].append(ex)
                    j += 1
                    break  # on s’arrête dès qu’on trouve un objet avec des exemples
                j += 1
            else:
                break

        merged[new_index] = merged_entry
        new_index += 1
        i = j if j > i + 1 else i + 1

    return merged

def extract_translation(row):
    cells = row.find_all('td')
    if len(cells) > 2:
        word_text = cells[0].get_text().strip()
        definition_text = cells[1].get_text().strip()
        meanings_text = cells[2].get_text().strip()

        meanings = extract_and_clean_meanings(meanings_text)

        # ⛔️ Ne retourne rien si aucun meaning n'est propre
        if not meanings:
            return None

        return {
            "word": clean_text(word_text),
            "definition": clean_text(definition_text),
            "meanings": meanings,
            "examples": []
        }
    return None

def extract_audio_links(soup):
    try:
        script = soup.find("div", id="listen_widget").script.string
        audio_urls = script[18:-3].split(',')
        return [URL + link.strip()[1:-1] for link in audio_urls]
    except:
        return []

def extract_and_clean_meanings(raw_text):
    raw_text = unicodedata.normalize("NFC", raw_text)
    raw_text = raw_text.replace("’", "'").replace("‘", "'")
    raw_text = re.sub(r'[\u200b\u200e\u200f\u202a-\u202e\u2060-\u206f]+', '', raw_text)

    raw_text = re.sub(r'\[.*?\]', '', raw_text)
    raw_text = raw_text.replace('+', '').replace('⇒', '')

    parts = re.split(r'[,:;]|(?<=\w)\s+(?=s[\'e]|se|être|devenir|adhérer|venir|aller|tomber|avoir|faire|prendre)', raw_text)

    cleaned_parts = []
    for part in parts:
        part = part.strip()
        if len(part) < 3:
            continue

        if re.search(r'\b(v|adj|n|adv|prep|loc|vi|vt|nm|nf|pron|intj|conj|pl|ind)\b', part, re.IGNORECASE):
            continue

        part = re.sub(r"\bs'e\b", "se", part)
        part = re.sub(r"\b([a-zA-ZÀ-ÿ])'", r"\1'", part)
        # part = re.sub(r"[^\w\sÀ-ÿ\-'’]", '', part)
        part = re.sub(r"[^\w\sÀ-ÿ/\'’\-]", '', part)
        part = re.sub(r'\s{2,}', ' ', part)

        final = part.strip()
        if final and final.lower() not in ["se", "être"]:
            cleaned_parts.append(final)

    return [cleaned_parts[0]] if cleaned_parts else []

def clean_text(text, type_=""):
    text = unicodedata.normalize("NFC", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r'[\u200b\u200e\u200f\u202a-\u202e\u2060-\u206f]+', '', text)

    if type_ == "meanings":
        text = re.sub(r'\[.*?\]', '', text)
        text = text.replace('+', '')
        text = re.sub(r'\b(v|adj|n|adv|prep|loc|vi|vt|nm|nf|pron|intj|conj|pl|ind)\b', '', text)
        text = re.sub(r"\bs'e\b", "se", text)
        text = re.sub(r"\b([a-zA-ZÀ-ÿ])'", r"\1'", text)
        text = re.sub(r"[^\w\sÀ-ÿ\-'’]", '', text)
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()
    else:
        text = text.replace('⇒', '').replace(u'\xa0', u' ').replace(u'\u24d8', u'').strip()
        text = re.sub(r'\s{2,}', ' ', text)
        return text

