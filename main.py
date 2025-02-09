import json
import logging
import os

from flask import Flask, render_template, request

app = Flask(__name__)

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Detect if running under Apache mod_wsgi (production) or locally
if 'macbook' in os.environ.get('HOME', ''):
    DATA_DIR = "/Users/macbookpro_e/PycharmProjects/mtgmarketcap"  # Local development path
else:
    DATA_DIR = "/home/ubuntu/mtgmarketcap"  # Production path


def load_data_for_set(set_name):
    """
    Load JSON data for the specified set from card_market_cap.json.
    Returns:
        (cards, total_marketcap)
        - cards: a list of dicts (one per card)
        - total_marketcap: float summing the 'market_cap' for all cards
    """
    filename = os.path.join(DATA_DIR, "card_market_cap.json")
    logging.debug(f"Loading data from: {filename}")

    if not os.path.exists(filename):
        logging.error(f"JSON file not found: {filename}")
        raise FileNotFoundError(f"JSON file not found: {filename}")

    with open(filename, "r", encoding="utf-8") as json_file:
        all_data = json.load(json_file)

    if not all_data:
        logging.warning("Loaded JSON file is empty.")
    else:
        logging.debug(f"JSON keys in first record: {list(all_data[0].keys())}")
        logging.debug(f"First record content: {json.dumps(all_data[0], indent=2)}")

    # Ensure set names are correct
    available_sets = set(card.get("set", "").lower() for card in all_data if "set" in card)
    logging.debug(f"Available sets: {available_sets}, Requested: {set_name}")

    # Extract relevant set data
    set_data = [card for card in all_data if card.get("set", "").lower() == set_name]
    logging.debug(f"Found {len(set_data)} cards for set: {set_name}")

    if not set_data:
        logging.warning(f"No cards found for set: {set_name}")

    # Convert market_cap values and calculate total market cap
    total_marketcap = 0.0
    for card in set_data:
        try:
            market_cap = float(card.get("market_cap", 0)) if card.get("market_cap") not in ["N/A", None] else 0.0
            total_marketcap += market_cap
        except ValueError:
            logging.warning(f"Invalid market_cap value for card: {card.get('name', 'Unknown')}")

    logging.debug(f"Total market cap for {set_name}: {total_marketcap}")
    return set_data, total_marketcap


def load_last_update():
    """
    Load the timestamp from last_update.json, if it exists.
    Returns 'N/A' if unavailable.
    """
    try:
        filename = os.path.join(DATA_DIR, "last_update.json")
        logging.debug(f"Loading last update timestamp from: {filename}")
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("last_update", "N/A")
    except (FileNotFoundError, json.JSONDecodeError):
        logging.warning("last_update.json not found or contains invalid JSON.")
        return "N/A"


@app.route('/')
def index():
    # 1. Determine which set is requested, default to 'lea'
    set_name = request.args.get('set', 'lea').lower()
    logging.info(f"Requested set: {set_name}")

    # 2. Load the JSON data for this set
    try:
        cards, total_marketcap = load_data_for_set(set_name)
    except FileNotFoundError:
        return "Error: Data file not found.", 500

    # 3. Load the last update timestamp
    last_update = load_last_update()

    # 4. Render the template, passing all the data
    return render_template(
        'index.html',
        cards=cards,
        set_name=set_name,
        total_marketcap=total_marketcap,
        last_update=last_update
    )


if __name__ == '__main__':
    app.run(debug=True)
