# 📊 Sales Analytics Dashboard

A modern, interactive **Sales Analytics Dashboard** built with **Plotly Dash**, featuring real-time filters, dynamic charts, and full Light/Dark theme support.

![Dashboard Preview](assets/preview.png)

## 🚀 Features

- **Interactive Filters** — Date range, Region, Product Category, Customer Type, Sales Channel, Sales Rep
- **KPI Cards** — Total Revenue, Units Sold, Orders, AOV, Discount Rate
- **9 Dynamic Charts** — Revenue trends, category breakdowns, scatter plots, sunburst diagrams and more
- **Light & Dark Theme** — Toggle between themes with one click, preference saved in browser
- **Responsive Layout** — Works on desktop and tablet screens

## 🛠️ Tech Stack

| Tool | Version |
|---|---|
| [Dash](https://dash.plotly.com/) | 4.4.1 |
| [Plotly](https://plotly.com/) | 7.1.0 |
| [Pandas](https://pandas.pydata.org/) | 3.0.6 |
| [Gunicorn](https://gunicorn.org/) | 26.2.0 |

## 🏃 Run Locally

```bash
# Clone the repository
git clone https://github.com/ChitPannEi08/SalesAnalyticsDashboard.git
cd SalesAnalyticsDashboard

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python dashboardapp.py
```

Then open **http://localhost:8050** in your browser.

## ☁️ Deploy to Render

1. Fork or push this repo to your GitHub account
2. Go to [render.com](https://render.com) and sign in with GitHub
3. Click **New → Web Service** → select this repository
4. Render auto-detects `render.yaml` — click **Create Web Service**
5. Your dashboard will be live at a `*.onrender.com` URL in ~2 minutes!

## 📁 Project Structure

```
SalesAnalyticsDashboard/
├── dashboardapp.py       # Main Dash application
├── sales_data.csv        # Sales dataset
├── requirements.txt      # Python dependencies
├── Procfile              # Gunicorn start command
├── render.yaml           # Render deployment config
└── assets/
    └── custom.css        # Theme & component styles
```

---

Made with ❤️ using [Plotly Dash](https://dash.plotly.com/)
