# Risk Analytics Dashboard (FinatriX)

## Overview
Risk Analytics Dashboard (FinatriX) is a Python-based application designed to analyze and visualize portfolio risk and performance metrics. The project combines quantitative finance techniques with interactive visualizations to help users understand financial risk exposure and portfolio behavior.

## Key Features
- Value-at-Risk (VaR) and Expected Shortfall (ES) analysis  
- Daily Profit & Loss (P&L) and Net Asset Value (NAV) tracking  
- Volatility and drawdown analysis  
- Sector-wise exposure visualization  
- Stress testing under hypothetical market scenarios  
- Interactive dashboard using Streamlit and Plotly  

## Tech Stack
- **Programming Language:** Python  
- **Libraries:** pandas, numpy, matplotlib, plotly  
- **Dashboard Framework:** Streamlit  
- **Version Control:** Git  

## Project Structure
risk-analytics-dashboard/
├── main.py # Backend risk calculations and data processing
├── d.py # Streamlit dashboard
├── data/ # Sample datasets (optional)
├── requirements.txt
├── README.md
└── .gitignore


## How to Run
1. Clone the repository:
```bash
git clone https://github.com/your-username/risk-analytics-dashboard.git
cd risk-analytics-dashboard

2.Install dependencies:
pip install -r requirements.txt

3.Run the backend script:
python main.py

4.Launch the dashboard:
streamlit run d.py

