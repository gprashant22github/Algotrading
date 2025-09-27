# Algo Trading Prototype — JarNox Intern Assignment

## 📌 Overview
This project implements a simple **algorithmic trading prototype** using:
- **SMA (Simple Moving Average) Crossover**
- **RSI (Relative Strength Index)**

It includes a **backtesting engine**, trade logging in **SQLite**, and an interactive **Streamlit dashboard** for visualization.

---

## 🚀 Features
- Historical data fetch via **Yahoo Finance**
- Strategy: **SMA crossover + RSI filter**
- Backtesting with equity curve, signals, and trade execution
- **SQLite trade log** for executed trades
- **Streamlit app** for visualization:
  - Price chart with buy/sell signals
  - Equity curve (portfolio value over time)
  - Trade history table
  - Final P&L, ROI, and portfolio stats

---

## 🛠️ Installation

Clone the repo:
```bash
git clone https://github.com/gprashant22github/Algotrading.git
cd Algotrading

Install dependencies:
pip install -r requirements.txt

▶️ Usage

Run the Streamlit dashboard:

streamlit run app.py


The app will open in your browser (default: http://localhost:8501
).

📊 Results

Sample backtest (SMA + RSI strategy):

Final Portfolio Value: $11,618.16

P&L: $1,618.16

ROI: 16.18%

Screenshots available in the results/
 folder.

📝 Development Approach

I built an algorithmic trading prototype using a rule-based strategy combining SMA (Simple Moving Average) crossover and RSI (Relative Strength Index).
The system fetches historical data via Yahoo Finance, applies strategy logic, backtests performance, and logs trades to a SQLite database.
A Streamlit dashboard was implemented for visualization, showing price charts with signals, portfolio equity curve, and trade history.

Technologies Used

Python for strategy implementation

Pandas & NumPy for data manipulation

yfinance for market data

Streamlit for the interactive dashboard

SQLite for trade logging

Challenges & Learnings

The main challenge was aligning multiple signals (SMA and RSI) without introducing look-ahead bias. Handling missing data and ensuring correct timestamp indexing was also crucial.
I learned how to structure backtest logic, including position sizing, cash management, and trade execution. Another key learning was building a user-friendly visualization layer for strategy validation.
