# :)

from flask import Flask, render_template, request
import csv
import json
import os
app = Flask(__name__)
# Detect if running under Apache mod_wsgi (production) or locally
if 'macbook' in os.environ.get('HOME',''):
    DATA_DIR = "/Users/macbookpro_e/PycharmProjects/mtgmarketcap"  # Local development path
else:
    DATA_DIR = "/home/ubuntu/mtgmarketcap"  # Production path


def load_data_for_set(set_name):
    """
    Load CSV data for the specified set (alpha, beta, unlimited).
    Each CSV is expected to be named data_<set_name>.csv, e.g. data_alpha.csv.

    Returns:
        (cards, total_marketcap)
        - cards: a list of dicts (one per card)
        - total_marketcap: float summing the 'market_cap' for all cards
    """
    filename = os.path.join(DATA_DIR, f"data_{set_name}.csv")

    # Debugging: Print the selected file path
    print(f"Loading data from: {filename}")

    if not os.path.exists(filename):
        raise FileNotFoundError(f"CSV file not found: {filename}")

    cards = []
    total_marketcap = 0.0

    # If the file doesn't exist (e.g., you haven't crawled that set yet), just return empty data
    if not os.path.exists(filename):
        return cards, total_marketcap

    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert numeric fields if needed
            # 'prints'
            try:
                row['prints'] = int(row['prints'])
            except (ValueError, TypeError):
                row['prints'] = None

            # 'usd'
            try:
                row['usd'] = float(row['usd']) if row['usd'] else None
            except (ValueError, TypeError):
                row['usd'] = None

            # 'market_cap'
            try:
                row['market_cap'] = float(row['market_cap']) if row['market_cap'] else None
            except (ValueError, TypeError):
                row['market_cap'] = None

            # Accumulate total marketcap
            if row['market_cap'] is not None:
                total_marketcap += row['market_cap']

            cards.append(row)

    return cards, total_marketcap


def load_last_update():
    """
    Load the timestamp from last_update.json, if it exists.
    Returns 'N/A' if unavailable.
    """

    try:
        with open(os.path.join(DATA_DIR, "last_update.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("last_update", "N/A")
    except (FileNotFoundError, json.JSONDecodeError):
        return "N/A"


@app.route('/')
def index():
    # 1. Determine which set is requested, default to 'alpha'
    set_name = request.args.get('set', 'alpha').lower()  # alpha, beta, or unlimited

    # 2. Load the CSV data for this set
    cards, total_marketcap = load_data_for_set(set_name)

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
