import json
import requests
import logging

# Configure logging to save to a file and print to console
log_filename = "crawler.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Load the JSON data
file_path = "prints.json"

with open(file_path, "r", encoding="utf-8") as file:
    cards_data = json.load(file)

# Scryfall API endpoint for querying cards by collector number
SCRYFALL_SEARCH_URL = "https://api.scryfall.com/cards"  # Adjusted for direct lookup
EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/EUR"

# Fetch EUR to USD conversion rate
def get_eur_to_usd_rate():
    try:
        response = requests.get(EXCHANGE_RATE_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("rates", {}).get("USD", 1)  # Default to 1 if not found
    except requests.RequestException as e:
        logging.error(f"Error fetching exchange rate: {e}")
    return 1

EUR_TO_USD_RATE = get_eur_to_usd_rate()
logging.info(f'EUR to USD rate: {EUR_TO_USD_RATE}')

# Output JSON structure
output_data = []

def fetch_card_details(set_code, collector_number):
    """Fetches card details from Scryfall API using set code and collector number."""
    url = f"{SCRYFALL_SEARCH_URL}/{set_code}/{collector_number}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching card details for set '{set_code}', collector number '{collector_number}': {e}")
    return None

for card in cards_data:
    card_name = card["name"].split(" - ")[0].strip()  # Extract actual name without variations
    set_code = card["set"]
    collector_number = card["#"]
    print_count = int(card["prints"])

    logging.info(f"Processing card: {card_name} (Set: {set_code}, Collector #: {collector_number})")
    card_details = fetch_card_details(set_code, collector_number)

    if card_details:
        # Extract price data
        price_usd = card_details.get("prices", {}).get("usd")
        price_eur = card_details.get("prices", {}).get("eur")

        # Convert EUR to USD if necessary
        if price_usd is None and price_eur is not None:
            try:
                price_eur = float(price_eur)
                price_usd = f"{price_eur * EUR_TO_USD_RATE:.2f}"
            except (ValueError, TypeError):
                logging.warning(f"Invalid EUR price for '{card_name}', skipping conversion.")
                price_usd = "N/A"
        elif price_usd is None:
            price_usd = "N/A"

        # Extract image URL
        image_url = card_details.get("image_uris", {}).get("small", "N/A")

        # Calculate market cap (Price * Printed Count)
        try:
            market_cap = float(price_usd) * print_count if price_usd != "N/A" else "N/A"
        except ValueError:
            market_cap = "N/A"

        output_data.append({
            "name": card_name,
            "set": set_code,
            "print_count": print_count,
            "latest_price_usd": price_usd,
            "image_thumbnail": image_url,
            "market_cap": market_cap
        })
    else:
        logging.warning(f"No details found for '{card_name}' in set '{set_code}', collector number '{collector_number}'.")

# Save output to a JSON file
output_file_path = "card_market_cap.json"

with open(output_file_path, "w", encoding="utf-8") as output_file:
    json.dump(output_data, output_file, indent=4)

logging.info(f"Processed {len(output_data)} cards. Data saved to {output_file_path}")
