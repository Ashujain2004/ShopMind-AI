# ShopMind AI — Pure Python + AI/ML

A small-business AI assistant built with Python.

## Features
- Inventory management
- Sales and expense tracking
- SQLite local database
- Sales forecasting with Random Forest
- Reorder recommendation
- Best/slow-moving products
- Dashboard charts
- Hinglish AI assistant
- Optional OpenAI API integration

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app creates `shopmind.db` automatically and seeds demo data on first run.

## Optional AI
Copy `.env.example` to `.env` and add your API key. Without an API key the app still works with a local rule-based assistant.

## Important
The ML forecast is a decision-support estimate, not a guarantee. Replace demo data with real shop sales before using predictions commercially.
