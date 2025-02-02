#!/usr/bin/env python3
# :)
import csv
import json
import requests
import datetime
import os

def fetch_eur_to_usd():
    """
    Fetch the current EUR -> USD conversion rate from the Frankfurter API.
    Return 1.04 if there's any error.
    """
    url = "https://api.frankfurter.app/latest?from=EUR&to=USD"
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            return data["rates"]["USD"]
    except Exception as e:
        print("Error fetching conversion rate:", e)
    print("Failed to fetch conversion rate, using default 1.04.")
    return 1.04

def fetch_scryfall_cards(set_code, eur_to_usd_rate):
    """
    Fetches all cards from Scryfall for the given set_code (e.g. 'lea' for Alpha).
    Attempts to use 'usd' price; if missing, tries to convert 'eur' -> 'usd' using eur_to_usd_rate.
    Returns a list of dicts with at least: name, collector_number, usd, rarity, thumbnail.
    """
    base_url = "https://api.scryfall.com/cards/search"
    params = {
        "q": f"e:{set_code}",
        "unique": "prints",
        "order": "set",
        "dir": "asc"
    }
    all_cards = []
    url = base_url

    while url:
        resp = requests.get(url, params=params)
        if not resp.ok:
            print(f"Error fetching data for {set_code}:", resp.text)
            break

        data = resp.json()
        for card in data.get("data", []):
            prices = card.get("prices", {})
            usd_price = prices.get("usd")

            # If 'usd' is missing, try converting from 'eur'
            if not usd_price:
                eur_price = prices.get("eur")
                if eur_price:
                    try:
                        converted = float(eur_price) * eur_to_usd_rate
                        usd_price = f"{converted:.2f}"
                    except Exception as e:
                        print(f"Error converting EUR price for '{card.get('name', '')}': {e}")
                        usd_price = ""

            # Clean up collector number (remove #, etc.)
            collector_number = card.get("collector_number", "").replace("#", "").strip()

            # Rarity
            rarity = card.get("rarity", "").lower()

            # Thumbnail image
            image_uris = card.get("image_uris", {})
            thumbnail = image_uris.get("small")
            if not thumbnail:
                # Attempt a fallback; note that the path might be invalid if scryfall doesn't have it
                thumbnail = f"https://img.scryfall.com/cards/small/en/{set_code}/{collector_number}.jpg"

            all_cards.append({
                "name": card.get("name", ""),
                "collector_number": collector_number,
                "usd": usd_price,
                "rarity": rarity,
                "thumbnail": thumbnail
            })

        if data.get("has_more"):
            url = data.get("next_page")
            params = None  # Next page URL includes all params
        else:
            url = None

    return all_cards

def compute_and_assign_market_cap(cards, supply_data):
    """
    Given a list of cards and a dict of supply estimates by rarity (e.g. {"rare": 1100, "uncommon": 4500, ...}),
    compute:
        prints = supply_data[rarity]
        market_cap = usd_price * prints
    If the card's USD price or a matching rarity is missing, leave market_cap empty.
    Returns the updated card list.
    """
    for card in cards:
        rarity = card.get("rarity", "")
        # supply_data might have keys in lowercase: "rare", "uncommon", "common", "land"
        # ensure we use .lower() if needed
        supply = supply_data.get(rarity)
        card["prints"] = supply if supply is not None else ""

        # Compute market cap
        try:
            usd = float(card["usd"]) if card["usd"] else 0.0
            if supply:
                mc = usd * supply
                card["market_cap"] = f"{mc:.2f}"
            else:
                card["market_cap"] = ""
        except ValueError:
            card["market_cap"] = ""
    return cards

def write_csv_for_set(cards, set_name):
    """
    Writes CSV data to 'data_<set_name>.csv'.
    Columns: [name, collector_number, prints, usd, market_cap, thumbnail].
    """
    filename = f"data_{set_name}.csv"
    fieldnames = ["name", "collector_number", "prints", "usd", "market_cap", "thumbnail"]
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for card in cards:
            row = {fn: card.get(fn, "") for fn in fieldnames}
            writer.writerow(row)
    print(f"CSV for {set_name} -> {filename} (total: {len(cards)} cards)")

def main():
    # 1. Load the supply data from prints.json
    if not os.path.exists("prints.json"):
        print("ERROR: prints.json file not found. Exiting.")
        return

    with open("prints.json", "r", encoding="utf-8") as f:
        all_prints_data = json.load(f)
        # Expected: all_prints_data["Alpha"], all_prints_data["Beta"], all_prints_data["Unlimited"]

    # 2. Fetch EUR->USD conversion rate
    eur_to_usd_rate = fetch_eur_to_usd()
    print(f"Using EUR->USD rate: {eur_to_usd_rate:.4f}")

    # 3. Map each 'set_name' to (Scryfall code, supply key in prints.json)
    sets_to_fetch = {
        "alpha":  {
            "scryfall_code": "lea",
            "prints_key": "Alpha"
        },
        "beta": {
            "scryfall_code": "leb",
            "prints_key": "Beta"
        },
        "unlimited": {
            "scryfall_code": "2ed",
            "prints_key": "Unlimited"
        }
    }

    # This will store all sets' data for a combined JSON
    all_results = {}

    # 4. Fetch each set, compute market caps, write CSV
    for set_name, info in sets_to_fetch.items():
        scryfall_code = info["scryfall_code"]  # e.g. 'lea', 'leb', '2ed'
        prints_key = info["prints_key"]        # e.g. 'Alpha', 'Beta', 'Unlimited'

        # supply_data for the set from prints.json
        supply_data = all_prints_data.get(prints_key, {})

        print(f"\n--- Processing {prints_key} ({scryfall_code}) ---")
        cards = fetch_scryfall_cards(scryfall_code, eur_to_usd_rate)
        cards = compute_and_assign_market_cap(cards, supply_data)

        # Write out a CSV file for the set
        write_csv_for_set(cards, set_name)

        # Compute total marketcap
        total_mc = 0.0
        for c in cards:
            mc_str = c.get("market_cap", "")
            if mc_str:
                try:
                    total_mc += float(mc_str)
                except ValueError:
                    pass

        # Put into a dict for JSON
        all_results[set_name] = {
            "cards": cards,
            "total_marketcap": round(total_mc, 2)
        }

    # 5. Write combined crawler output
    with open("crawler_output.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print("\nWrote combined data to crawler_output.json")

    # 6. Write last update time
    now_str = datetime.datetime.now().isoformat()
    with open("last_update.json", "w", encoding="utf-8") as f:
        json.dump({"last_update": now_str}, f)
    print(f"Wrote last update time to last_update.json -> {now_str}")

if __name__ == "__main__":
    main()
