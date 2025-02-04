# MTG Market Cap

A **Magic: The Gathering** finance tool that estimates the total market capitalization of various MTG card sets based on price and supply data.

## 📌 Features
- Fetches **real-time** card prices from **Scryfall**.
- Uses **historical print run estimates** to calculate supply.
- Computes **market capitalization** for each card.
- Provides **a Flask-powered web dashboard** for visualization.
- Supports **multiple themes** for a customized UI experience.

## 📊 Data Sources
- **Card Prices:** Prices are retrieved from **Scryfall**, which syncs prices from affiliates every **24 hours**.
- **Print Estimates:** Print run estimates are based on **historical data and research**.

## 📖 FAQ
### **Where do print estimates come from?**
The print estimates used in this project are based on the methodology outlined in [this Reddit post](https://www.reddit.com/r/mtgfinance/comments/8d8fvb/the_definitive_guide_to_print_runs/). These estimates rely on historical research and expert analysis.

### **Where do Scryfall prices come from?**
Scryfall syncs prices from its affiliates **every 24 hours**. The lowest available price in a given currency is displayed.

- **TCGplayer:** Uses the **Market Price**, not low, mid, or high.
- **Cardmarket:** Uses the **Trend Price**, **1-day/7-day/30-day averages**, or the suggested price, whichever is available.

For more details, see the [Scryfall pricing page](https://scryfall.com).

## 🛠 Technologies Used
- **Python** (Flask, Requests, JSON Handling)
- **Bootstrap & DataTables** (Frontend UI)
- **Logging & Error Handling** for stability

## 📜 License
This project is licensed under the **MIT License**.

---

💡 **Want to contribute?** Feel free to fork the repository and submit a pull request! 🎉

