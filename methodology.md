# Methodology for MTG Alpha Card Market Cap Estimation

This document outlines the methodology used to collect price data, estimate print runs, and calculate market capitalization for cards from the Magic: The Gathering Alpha set. The process is automated via a Python script that interacts with the Scryfall API and produces a CSV file with the resulting data.

---

## Data Sources

- **Scryfall API**  
  The primary source of card data is the [Scryfall API](https://api.scryfall.com/). The script queries Scryfall using the following parameters:
  - **Query**: `e:lea` — filters for cards from the Alpha set (set code `lea`).
  - **Unique Parameter**: `unique=prints` — returns every printing variant of the cards.
  - **Ordering**: `order=set` and `dir=asc` — sorts the results in set order.

- **Price Information**  
  Price data is extracted from the `prices` field of each card object returned by the API. This field typically contains several pricing values, such as:
  - **`usd`**: The last known price in US dollars.
  - **`eur`**: The last known price in Euros.
  - Other values (like `tix`) are available but not used in this script.

---

## Price Data and Interpretation

- **Source of Prices**  
  The price information comes directly from Scryfall’s aggregated data. Specifically, the `usd` field represents the most recent price value that Scryfall has on record, which is collected from one or more online marketplaces (for example, TCGPlayer, Card Kingdom, etc.).

- **What Does the Price Represent?**  
  - **Last Known Price**:  
    The "last known price" is an estimate based on the most recent data Scryfall has aggregated. It is **not** necessarily the price from the last completed sale; rather, it is a market value estimate.
  - **Generic Pricing**:  
    The prices provided are general market estimates and do not account for variations due to the condition or quality of the card.
  - **No Quality Metrics**:  
    The API does not include information on card quality (e.g., near-mint, played, graded conditions). All cards are assumed to be in standard condition, and any variation due to grading or physical quality is not reflected in the price.

- **Limitations**  
  - The price is an aggregate estimate and might not match a specific seller’s listing or a final sale price.
  - The conversion from EUR to USD is performed using a fixed rate and may not reflect real-time market fluctuations.
  - No adjustments are made for foil versus non-foil versions or different printings with varying conditions.

- **Scryfall Price**
  - For more information, visit https://scryfall.com/docs/faqs/where-do-scryfall-prices-come-from-7.
---


## Print Run Estimates

- **Source of Estimates**:  
  The script uses estimated print run values derived from a published guide. These values are approximations and are used to scale the card’s price into a “market cap” figure.

- **Assigned Estimates**:
  - **Rare**: 1,100 copies
  - **Uncommon**: 4,500 copies
  - **Common**: 15,900 copies
  - **Land**: 87,000 copies

- These values are stored in the script’s `PRINT_RUN_ESTIMATES` dictionary and are matched to a card's rarity (converted to lowercase).

---

## Market Capitalization Calculation

- **Formula**:  
  The market cap for each card is calculated as:

  \[
  \text{Market Cap} = \text{USD Price} \times \text{Estimated Print Run}
  \]

- **Calculation Process**:
  1. For each card, if a valid USD price is available (directly or via conversion) and a matching print run estimate is found, the script multiplies these two values.
  2. The result is formatted to two decimal places and stored as the market cap.
  3. If the price or the print run is missing, the market cap field is left blank.

---

## Data Processing and CSV Generation

- **Data Fetching**:  
  The script iterates over pages of results from the Scryfall API until all card data for the Alpha set is retrieved.

- **Data Cleaning**:  
  - Collector numbers are cleaned by removing any `#` symbols.
  - Rarity values are converted to lowercase to match keys in the `PRINT_RUN_ESTIMATES` dictionary.

- **CSV Output**:  
  The processed data is exported to a CSV file (`data.csv`) with the following columns:
  - `name`
  - `collector_number`
  - `prints` (estimated print run)
  - `usd` (price in USD)
  - `market_cap` (calculated market capitalization)

---

## Limitations and Considerations

- **API Dependency**:  
  The script relies on the availability and consistency of the Scryfall API. Any changes or downtime may affect data retrieval.

- **Fixed Conversion Rate**:  
  The hard-coded EUR-to-USD conversion rate (1.04) might not reflect current market conditions.

- **Estimated Print Runs**:  
  The print run numbers are approximations and may not be accurate for every card.

- **Quality/Condition Not Accounted For**:  
  The prices shown do not reflect the condition or grading of a card. They are generic estimates assuming standard, ungraded condition.

- **Incomplete Price Data**:  
  Some cards may not have complete price data (missing USD and/or EUR values), which means their market cap cannot be calculated.