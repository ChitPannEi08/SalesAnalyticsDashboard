from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Initialize Dash application with title and meta tags
app = Dash(
    __name__,
    title="Sales Analytics Dashboard",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

# Data Ingestion & Preprocessing
df = pd.read_csv('sales_data.csv')
df['Sale_Date'] = pd.to_datetime(df['Sale_Date'])
df['YearMonth'] = df['Sale_Date'].dt.to_period('M').astype(str)
df['Month_Formatted'] = df['Sale_Date'].dt.strftime('%b %Y')
df['Margin_Per_Unit'] = df['Unit_Price'] - df['Unit_Cost']
df['Estimated_Profit'] = df['Sales_Amount'] - (df['Unit_Cost'] * df['Quantity_Sold'])

# Filter options
MIN_DATE = df['Sale_Date'].min().strftime('%Y-%m-%d')
MAX_DATE = df['Sale_Date'].max().strftime('%Y-%m-%d')
REGION_OPTIONS = [{'label': r, 'value': r} for r in sorted(df['Region'].unique())]
CATEGORY_OPTIONS = [{'label': c, 'value': c} for c in sorted(df['Product_Category'].unique())]
CUSTOMER_TYPE_OPTIONS = [{'label': ct, 'value': ct} for ct in sorted(df['Customer_Type'].unique())]
CHANNEL_OPTIONS = [{'label': sc, 'value': sc} for sc in sorted(df['Sales_Channel'].unique())]
REP_OPTIONS = [{'label': rep, 'value': rep} for rep in sorted(df['Sales_Rep'].unique())]

# Theme Configuration & Color Palettes
THEMES = {
    'dark': {
        'template': 'plotly_dark',
        'text': '#f8fafc',
        'text_muted': '#94a3b8',
        'grid': 'rgba(255, 255, 255, 0.08)',
        'line': 'rgba(255, 255, 255, 0.12)',
        'hover_bg': '#1e293b',
        'hover_font': '#f8fafc',
        'hover_border': 'rgba(255, 255, 255, 0.15)',
        'cyan': '#06b6d4',
        'blue': '#3b82f6',
        'indigo': '#6366f1',
        'emerald': '#10b981',
        'amber': '#f59e0b',
        'rose': '#f43f5e',
        'violet': '#8b5cf6',
        'table_header_bg': '#1e293b',
        'table_header_color': '#f8fafc',
        'table_header_border': '1px solid rgba(255, 255, 255, 0.1)',
        'table_data_bg': '#111827',
        'table_data_color': '#cbd5e1',
        'table_data_border': '1px solid rgba(255, 255, 255, 0.05)',
        'table_odd_bg': 'rgba(30, 41, 59, 0.4)',
        'table_selected_bg': 'rgba(56, 189, 248, 0.25)',
        'table_selected_border': '#38bdf8',
        'table_border': '1px solid rgba(255, 255, 255, 0.07)'
    },
    'light': {
        'template': 'plotly_white',
        'text': '#0f172a',
        'text_muted': '#475569',
        'grid': 'rgba(0, 0, 0, 0.06)',
        'line': 'rgba(0, 0, 0, 0.12)',
        'hover_bg': '#ffffff',
        'hover_font': '#0f172a',
        'hover_border': 'rgba(0, 0, 0, 0.12)',
        'cyan': '#0891b2',
        'blue': '#2563eb',
        'indigo': '#4f46e5',
        'emerald': '#059669',
        'amber': '#d97706',
        'rose': '#e11d48',
        'violet': '#7c3aed',
        'table_header_bg': '#f8fafc',
        'table_header_color': '#0f172a',
        'table_header_border': '1px solid #e2e8f0',
        'table_data_bg': '#ffffff',
        'table_data_color': '#334155',
        'table_data_border': '1px solid #f1f5f9',
        'table_odd_bg': '#f8fafc',
        'table_selected_bg': 'rgba(2, 132, 199, 0.12)',
        'table_selected_border': '#0284c7',
        'table_border': '1px solid #e2e8f0'
    }
}

COLOR_SEQUENCES = {
    'dark': [
        THEMES['dark']['cyan'],
        THEMES['dark']['indigo'],
        THEMES['dark']['emerald'],
        THEMES['dark']['amber'],
        THEMES['dark']['rose'],
        THEMES['dark']['violet'],
        THEMES['dark']['blue']
    ],
    'light': [
        THEMES['light']['cyan'],
        THEMES['light']['indigo'],
        THEMES['light']['emerald'],
        THEMES['light']['amber'],
        THEMES['light']['rose'],
        THEMES['light']['violet'],
        THEMES['light']['blue']
    ]
}

def apply_theme(fig, theme='dark', height=360):
    """Applies clean, responsive theme styling to Plotly figures."""
    t = THEMES.get(theme, THEMES['dark'])
    fig.update_layout(
        template=t['template'],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family='Plus Jakarta Sans, sans-serif', color=t['text'], size=12),
        hoverlabel=dict(
            bgcolor=t['hover_bg'],
            font_size=12,
            font_family='Plus Jakarta Sans, sans-serif',
            font_color=t['hover_font'],
            bordercolor=t['hover_border']
        ),
        xaxis=dict(
            gridcolor=t['grid'],
            zerolinecolor=t['grid'],
            showline=True,
            linecolor=t['line']
        ),
        yaxis=dict(
            gridcolor=t['grid'],
            zerolinecolor=t['grid'],
            showline=True,
            linecolor=t['line']
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=t['text'])
        )
    )
    return fig

# Application Layout
app.layout = html.Div(id="app-container", className="app-container theme-dark", children=[
    # --- Top Header ---
    html.Div([
        html.Div([
            html.H1("Sales Analytics Dashboard"),
            html.P("Business Performance Analysis, Revenue Insights & Operational Analytics", className="header-subtitle")
        ], className="header-title-group"),
        html.Div([
            html.Button(
                [
                    html.Span("🌙", id="theme-icon", className="theme-toggle-icon"),
                    html.Span("Dark Mode", id="theme-text", className="theme-toggle-text")
                ],
                id="theme-toggle-btn",
                n_clicks=0,
                className="btn-theme-toggle"
            ),
            dcc.Store(id="theme-store", data="dark", storage_type="local")
        ], className="header-controls")
    ], className="dashboard-header"),

    # --- Filter Control Panel ---
    html.Div([
        html.Div([
            html.Div([
                html.Span("Analytics Filter Controls", className="filter-header-title")
            ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),
            html.Button("Reset Filters", id="reset-btn", n_clicks=0, className="btn-reset")
        ], className="filter-header"),

        html.Div([
            # Date Range Filter
            html.Div([
                html.Label("Date Range", className="filter-label"),
                dcc.DatePickerRange(
                    id='date-range-filter',
                    min_date_allowed=MIN_DATE,
                    max_date_allowed=MAX_DATE,
                    start_date=MIN_DATE,
                    end_date=MAX_DATE,
                    display_format='YYYY-MM-DD',
                    className="date-picker-custom"
                )
            ], className="filter-group"),

            # Region Filter
            html.Div([
                html.Label("Region", className="filter-label"),
                dcc.Dropdown(
                    id='region-filter',
                    options=REGION_OPTIONS,
                    value=[],
                    multi=True,
                    placeholder="All Regions"
                )
            ], className="filter-group"),

            # Category Filter
            html.Div([
                html.Label("Product Category", className="filter-label"),
                dcc.Dropdown(
                    id='category-filter',
                    options=CATEGORY_OPTIONS,
                    value=[],
                    multi=True,
                    placeholder="All Categories"
                )
            ], className="filter-group"),

            # Customer Type Filter
            html.Div([
                html.Label("Customer Type", className="filter-label"),
                dcc.Dropdown(
                    id='customer-filter',
                    options=CUSTOMER_TYPE_OPTIONS,
                    value=[],
                    multi=True,
                    placeholder="All Customer Types"
                )
            ], className="filter-group"),

            # Sales Channel Filter
            html.Div([
                html.Label("Sales Channel", className="filter-label"),
                dcc.Dropdown(
                    id='channel-filter',
                    options=CHANNEL_OPTIONS,
                    value=[],
                    multi=True,
                    placeholder="All Channels"
                )
            ], className="filter-group"),

            # Sales Rep Filter
            html.Div([
                html.Label("Sales Rep", className="filter-label"),
                dcc.Dropdown(
                    id='rep-filter',
                    options=REP_OPTIONS,
                    value=[],
                    multi=True,
                    placeholder="All Sales Reps"
                )
            ], className="filter-group")
        ], className="filter-grid")
    ], className="filter-panel", style={"position": "relative", "zIndex": 100, "overflow": "visible"}),

    # --- KPI Metric Cards ---
    html.Div([
        # Card 1: Total Revenue
        html.Div([
            html.Div([
                html.Span("Total Revenue", className="kpi-title"),
                html.Span("💰", className="kpi-icon")
            ], className="kpi-header"),
            html.Div("$0.00", id="kpi-revenue", className="kpi-value"),
            html.Div("Gross recorded sales", id="kpi-revenue-sub", className="kpi-subtitle")
        ], className="kpi-card cyan"),

        # Card 2: Units Sold
        html.Div([
            html.Div([
                html.Span("Total Units Sold", className="kpi-title"),
                html.Span("📦", className="kpi-icon")
            ], className="kpi-header"),
            html.Div("0", id="kpi-quantity", className="kpi-value"),
            html.Div("Total quantity dispatched", id="kpi-quantity-sub", className="kpi-subtitle")
        ], className="kpi-card emerald"),

        # Card 3: Total Orders
        html.Div([
            html.Div([
                html.Span("Total Orders", className="kpi-title"),
                html.Span("🧾", className="kpi-icon")
            ], className="kpi-header"),
            html.Div("0", id="kpi-orders", className="kpi-value"),
            html.Div("Transactions completed", id="kpi-orders-sub", className="kpi-subtitle")
        ], className="kpi-card indigo"),

        # Card 4: Average Order Value
        html.Div([
            html.Div([
                html.Span("Avg Order Value", className="kpi-title"),
                html.Span("📈", className="kpi-icon")
            ], className="kpi-header"),
            html.Div("$0.00", id="kpi-aov", className="kpi-value"),
            html.Div("Revenue per transaction", id="kpi-aov-sub", className="kpi-subtitle")
        ], className="kpi-card amber"),

        # Card 5: Average Discount
        html.Div([
            html.Div([
                html.Span("Avg Discount", className="kpi-title"),
                html.Span("🏷️", className="kpi-icon")
            ], className="kpi-header"),
            html.Div("0.0%", id="kpi-discount", className="kpi-value"),
            html.Div("Average promotional rate", id="kpi-discount-sub", className="kpi-subtitle")
        ], className="kpi-card rose"),
    ], className="kpi-grid", style={"position": "relative", "zIndex": 1}),

    # --- Analytics Tab Navigation ---
    dcc.Tabs(id="dashboard-tabs", value="tab-overview", className="custom-tabs-container", style={"position": "relative", "zIndex": 1}, children=[
        # Tab 1: Executive Overview
        dcc.Tab(label="📊 Executive Overview", value="tab-overview", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div([
                # Monthly Revenue & Volume Trends
                html.Div([
                    html.Div([
                        html.H3("Monthly Revenue & Transaction Volume", className="chart-title"),
                        html.P("Monthly trajectory showing revenue and sales order volume", className="chart-subtitle")
                    ], className="chart-header"),
                    dcc.Graph(id="chart-monthly-trend", config={"displayModeBar": False})
                ], className="chart-card", style={"marginBottom": "20px"}),

                # 2-column grid: Category Sales & Sales Rep Leaderboard
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("Sales Revenue by Product Category", className="chart-title"),
                            html.P("Total revenue contribution per category", className="chart-subtitle")
                        ], className="chart-header"),
                        dcc.Graph(id="chart-category-revenue", config={"displayModeBar": False})
                    ], className="chart-card"),

                    html.Div([
                        html.Div([
                            html.H3("Sales Rep Performance Leaderboard", className="chart-title"),
                            html.P("Total sales revenue generated by each sales representative", className="chart-subtitle")
                        ], className="chart-header"),
                        dcc.Graph(id="chart-rep-performance", config={"displayModeBar": False})
                    ], className="chart-card"),
                ], className="charts-grid-2")
            ], style={"paddingTop": "16px"})
        ]),

        # Tab 2: Product & Pricing Analytics
        dcc.Tab(label="🏷️ Product & Pricing", value="tab-products", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Unit Price vs. Unit Cost Analysis", className="chart-title"),
                        html.P("Product unit economics and margin distribution across categories (bubble size = Quantity Sold)", className="chart-subtitle")
                    ], className="chart-header"),
                    dcc.Graph(id="chart-price-cost-scatter", config={"displayModeBar": False})
                ], className="chart-card", style={"marginBottom": "20px"}),

                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("Top 10 Product IDs by Revenue", className="chart-title"),
                            html.P("Highest grossing individual product IDs in the catalog", className="chart-subtitle")
                        ], className="chart-header"),
                        dcc.Graph(id="chart-top-products", config={"displayModeBar": False})
                    ], className="chart-card"),

                    html.Div([
                        html.Div([
                            html.H3("Category Quantity vs Discount Profile", className="chart-title"),
                            html.P("Average discount rate and total units sold by category", className="chart-subtitle")
                        ], className="chart-header"),
                        dcc.Graph(id="chart-category-discount", config={"displayModeBar": False})
                    ], className="chart-card"),
                ], className="charts-grid-2")
            ], style={"paddingTop": "16px"})
        ]),

        # Tab 3: Customer & Channel Insights
        dcc.Tab(label="👥 Customer & Channel Insights", value="tab-customers", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("Customer Type Distribution", className="chart-title"),
                            html.P("Revenue share and order volume: New vs Returning Customers", className="chart-subtitle")
                        ], className="chart-header"),
                        dcc.Graph(id="chart-customer-type", config={"displayModeBar": False})
                    ], className="chart-card"),

                    html.Div([
                        html.Div([
                            html.H3("Payment Methods by Sales Channel", className="chart-title"),
                            html.P("Breakdown of payment preferences across Online and Retail", className="chart-subtitle")
                        ], className="chart-header"),
                        dcc.Graph(id="chart-payment-channel", config={"displayModeBar": False})
                    ], className="chart-card"),

                    html.Div([
                        html.Div([
                            html.H3("Regional & Sales Rep Hierarchy", className="chart-title"),
                            html.P("Hierarchical revenue distribution across Regions and Reps", className="chart-subtitle")
                        ], className="chart-header"),
                        dcc.Graph(id="chart-region-sunburst", config={"displayModeBar": False})
                    ], className="chart-card")
                ], className="charts-grid-3")
            ], style={"paddingTop": "16px"})
        ]),

        # Tab 4: Raw Data Explorer
        dcc.Tab(label="📋 Transaction Data Explorer", value="tab-data", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Detailed Sales Records", className="chart-title"),
                        html.P("Explore, search, filter, and sort full transaction details with export capabilities", className="chart-subtitle")
                    ], className="chart-header"),
                    dash_table.DataTable(
                        id='sales-table',
                        columns=[
                            {"name": "Product ID", "id": "Product_ID"},
                            {"name": "Date", "id": "Sale_Date_Str"},
                            {"name": "Category", "id": "Product_Category"},
                            {"name": "Sales Rep", "id": "Sales_Rep"},
                            {"name": "Region", "id": "Region"},
                            {"name": "Sales Amount ($)", "id": "Sales_Amount_Str"},
                            {"name": "Qty", "id": "Quantity_Sold"},
                            {"name": "Unit Price ($)", "id": "Unit_Price_Str"},
                            {"name": "Unit Cost ($)", "id": "Unit_Cost_Str"},
                            {"name": "Discount", "id": "Discount_Str"},
                            {"name": "Customer Type", "id": "Customer_Type"},
                            {"name": "Payment Method", "id": "Payment_Method"},
                            {"name": "Sales Channel", "id": "Sales_Channel"},
                        ],
                        page_size=15,
                        sort_action="native",
                        filter_action="native",
                        export_format="csv"
                    )
                ], className="chart-card")
            ], style={"paddingTop": "16px"})
        ])
    ])
])

# Interactive Callbacks

# Theme Toggle Callback
@app.callback(
    [
        Output('theme-store', 'data'),
        Output('theme-icon', 'children'),
        Output('theme-text', 'children'),
        Output('app-container', 'className')
    ],
    Input('theme-toggle-btn', 'n_clicks'),
    State('theme-store', 'data'),
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme):
    current = current_theme or 'dark'
    new_theme = 'light' if current == 'dark' else 'dark'
    icon = "☀️" if new_theme == 'light' else "🌙"
    text = "Light Mode" if new_theme == 'light' else "Dark Mode"
    class_name = f"app-container theme-{new_theme}"
    return new_theme, icon, text, class_name

# Reset Filters Callback
@app.callback(
    [
        Output('date-range-filter', 'start_date'),
        Output('date-range-filter', 'end_date'),
        Output('region-filter', 'value'),
        Output('category-filter', 'value'),
        Output('customer-filter', 'value'),
        Output('channel-filter', 'value'),
        Output('rep-filter', 'value'),
    ],
    Input('reset-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_all_filters(n_clicks):
    return MIN_DATE, MAX_DATE, [], [], [], [], []


# Master Callback: Update KPIs, Charts, and DataTable
@app.callback(
    [
        # KPI Outputs
        Output('kpi-revenue', 'children'),
        Output('kpi-revenue-sub', 'children'),
        Output('kpi-quantity', 'children'),
        Output('kpi-orders', 'children'),
        Output('kpi-aov', 'children'),
        Output('kpi-discount', 'children'),
        
        # Chart Outputs
        Output('chart-monthly-trend', 'figure'),
        Output('chart-category-revenue', 'figure'),
        Output('chart-rep-performance', 'figure'),
        Output('chart-price-cost-scatter', 'figure'),
        Output('chart-top-products', 'figure'),
        Output('chart-category-discount', 'figure'),
        Output('chart-customer-type', 'figure'),
        Output('chart-payment-channel', 'figure'),
        Output('chart-region-sunburst', 'figure'),
        
        # Table Output & Styles
        Output('sales-table', 'data'),
        Output('sales-table', 'style_header'),
        Output('sales-table', 'style_data'),
        Output('sales-table', 'style_data_conditional'),
        Output('sales-table', 'style_table')
    ],
    [
        Input('date-range-filter', 'start_date'),
        Input('date-range-filter', 'end_date'),
        Input('region-filter', 'value'),
        Input('category-filter', 'value'),
        Input('customer-filter', 'value'),
        Input('channel-filter', 'value'),
        Input('rep-filter', 'value'),
        Input('theme-store', 'data')
    ]
)
def update_dashboard(start_date, end_date, selected_regions, selected_categories,
                     selected_customers, selected_channels, selected_reps, theme):
    active_theme = theme if theme in THEMES else 'dark'
    t = THEMES[active_theme]
    colors = COLOR_SEQUENCES[active_theme]

    # Table styles for active theme
    style_header = {
        'backgroundColor': t['table_header_bg'],
        'color': t['table_header_color'],
        'fontWeight': '700',
        'fontFamily': 'Outfit, sans-serif',
        'fontSize': '0.84rem',
        'border': t['table_header_border'],
        'textAlign': 'left',
        'padding': '12px 14px'
    }
    style_data = {
        'backgroundColor': t['table_data_bg'],
        'color': t['table_data_color'],
        'fontSize': '0.84rem',
        'fontFamily': 'Plus Jakarta Sans, sans-serif',
        'border': t['table_data_border'],
        'padding': '10px 14px'
    }
    style_data_conditional = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': t['table_odd_bg']
        },
        {
            'if': {'state': 'selected'},
            'backgroundColor': t['table_selected_bg'],
            'border': f"1px solid {t['table_selected_border']}"
        }
    ]
    style_table = {
        'overflowX': 'auto',
        'borderRadius': '10px',
        'border': t['table_border']
    }

    # Filter dataset
    filtered_df = df.copy()

    if start_date:
        filtered_df = filtered_df[filtered_df['Sale_Date'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['Sale_Date'] <= pd.to_datetime(end_date)]
    if selected_regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Product_Category'].isin(selected_categories)]
    if selected_customers:
        filtered_df = filtered_df[filtered_df['Customer_Type'].isin(selected_customers)]
    if selected_channels:
        filtered_df = filtered_df[filtered_df['Sales_Channel'].isin(selected_channels)]
    if selected_reps:
        filtered_df = filtered_df[filtered_df['Sales_Rep'].isin(selected_reps)]

    # Handle Empty Filter Result
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No data matching current filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=t['text_muted'])
        )
        empty_fig = apply_theme(empty_fig, theme=active_theme)
        return (
            "$0.00", "0% of total catalog",
            "0", "0", "$0.00", "0.0%",
            empty_fig, empty_fig, empty_fig,
            empty_fig, empty_fig, empty_fig,
            empty_fig, empty_fig, empty_fig,
            [],
            style_header, style_data, style_data_conditional, style_table
        )

    # 1. KPI Calculations
    total_revenue = filtered_df['Sales_Amount'].sum()
    total_quantity = filtered_df['Quantity_Sold'].sum()
    total_orders = len(filtered_df)
    aov = total_revenue / total_orders if total_orders > 0 else 0
    avg_discount = filtered_df['Discount'].mean() * 100
    
    pct_total_rev = (total_revenue / df['Sales_Amount'].sum()) * 100
    
    if total_revenue >= 1_000_000:
        rev_str = f"${total_revenue / 1_000_000:.2f}M"
    else:
        rev_str = f"${total_revenue:,.2f}"

    kpi_rev_sub = f"{pct_total_rev:.1f}% of all-time sales"
    qty_str = f"{total_quantity:,}"
    orders_str = f"{total_orders:,}"
    aov_str = f"${aov:,.2f}"
    discount_str = f"{avg_discount:.1f}%"

    # Charts Creation

    # Chart 1: Monthly Trend (Dual-Axis Revenue + Volume)
    monthly = filtered_df.groupby('YearMonth').agg(
        Revenue=('Sales_Amount', 'sum'),
        Orders=('Product_ID', 'count'),
        Quantity=('Quantity_Sold', 'sum')
    ).reset_index()
    monthly['Month_Label'] = pd.to_datetime(monthly['YearMonth'] + '-01').dt.strftime('%b %Y')

    fig_monthly = go.Figure()
    # Bar for revenue
    fig_monthly.add_trace(go.Bar(
        x=monthly['Month_Label'],
        y=monthly['Revenue'],
        name='Sales Revenue ($)',
        marker=dict(
            color=t['cyan'],
            opacity=0.85,
            line=dict(color=t['cyan'], width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
    ))
    # Line for order volume
    fig_monthly.add_trace(go.Scatter(
        x=monthly['Month_Label'],
        y=monthly['Orders'],
        name='Order Count',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color=t['amber'], width=3),
        marker=dict(size=7, color=t['amber']),
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
    ))

    fig_monthly.update_layout(
        yaxis=dict(title=dict(text='Revenue ($)', font=dict(color=t['cyan']))),
        yaxis2=dict(
            title=dict(text='Order Count', font=dict(color=t['amber'])),
            overlaying='y',
            side='right',
            showgrid=False
        ),
        hovermode='x unified'
    )
    fig_monthly = apply_theme(fig_monthly, theme=active_theme, height=340)

    # --- Chart 2: Category Revenue (Donut / Pie) ---
    cat_rev = filtered_df.groupby('Product_Category')['Sales_Amount'].sum().reset_index()
    fig_cat = px.pie(
        cat_rev,
        names='Product_Category',
        values='Sales_Amount',
        hole=0.55,
        color_discrete_sequence=colors
    )
    fig_cat.update_traces(
        textinfo='percent+label',
        textfont_size=12,
        hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>'
    )
    fig_cat = apply_theme(fig_cat, theme=active_theme, height=320)

    # --- Chart 3: Sales Rep Performance (Horizontal Bar) ---
    rep_perf = filtered_df.groupby('Sales_Rep').agg(
        Revenue=('Sales_Amount', 'sum'),
        Orders=('Product_ID', 'count')
    ).reset_index().sort_values('Revenue', ascending=True)

    fig_rep = go.Figure(go.Bar(
        x=rep_perf['Revenue'],
        y=rep_perf['Sales_Rep'],
        orientation='h',
        marker=dict(
            color=rep_perf['Revenue'],
            colorscale=[[0, t['indigo']], [1, t['cyan']]],
            showscale=False
        ),
        hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>'
    ))
    fig_rep.update_layout(
        xaxis=dict(title='Total Revenue ($)'),
        yaxis=dict(title='Sales Representative')
    )
    fig_rep = apply_theme(fig_rep, theme=active_theme, height=320)

    # --- Chart 4: Unit Price vs Unit Cost (Scatter) ---
    fig_scatter = px.scatter(
        filtered_df,
        x='Unit_Cost',
        y='Unit_Price',
        color='Product_Category',
        size='Quantity_Sold',
        hover_data=['Product_ID', 'Sales_Rep', 'Region', 'Discount', 'Sales_Amount'],
        color_discrete_sequence=colors,
        labels={'Unit_Cost': 'Unit Cost ($)', 'Unit_Price': 'Unit Price ($)'}
    )
    scatter_border = 'rgba(255,255,255,0.7)' if active_theme == 'dark' else 'rgba(0,0,0,0.3)'
    fig_scatter.update_traces(marker=dict(opacity=0.85, line=dict(width=0.75, color=scatter_border)))
    fig_scatter = apply_theme(fig_scatter, theme=active_theme, height=360)

    # --- Chart 5: Top 10 Best Selling Product IDs ---
    top_prods = filtered_df.groupby('Product_ID')['Sales_Amount'].sum().nlargest(10).reset_index()
    top_prods['Product_ID_Label'] = top_prods['Product_ID'].astype(str)
    
    fig_top = go.Figure(go.Bar(
        x=top_prods['Product_ID_Label'],
        y=top_prods['Sales_Amount'],
        marker=dict(
            color=t['emerald'],
            line=dict(color='rgba(255,255,255,0.2)' if active_theme == 'dark' else 'rgba(0,0,0,0.1)', width=1)
        ),
        hovertemplate='<b>Product #%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
    ))
    fig_top.update_layout(
        xaxis=dict(title='Product ID', type='category'),
        yaxis=dict(title='Total Sales ($)')
    )
    fig_top = apply_theme(fig_top, theme=active_theme, height=320)

    # --- Chart 6: Category Discount vs Quantity Profile ---
    cat_profile = filtered_df.groupby('Product_Category').agg(
        AvgDiscount=('Discount', 'mean'),
        TotalQty=('Quantity_Sold', 'sum')
    ).reset_index()
    cat_profile['AvgDiscountPct'] = cat_profile['AvgDiscount'] * 100

    fig_cat_profile = go.Figure()
    fig_cat_profile.add_trace(go.Bar(
        x=cat_profile['Product_Category'],
        y=cat_profile['TotalQty'],
        name='Units Sold',
        marker_color=t['violet'],
        hovertemplate='<b>%{x}</b><br>Units: %{y:,}<extra></extra>'
    ))
    fig_cat_profile.add_trace(go.Scatter(
        x=cat_profile['Product_Category'],
        y=cat_profile['AvgDiscountPct'],
        name='Avg Discount (%)',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color=t['rose'], width=3),
        marker=dict(size=8, color=t['rose']),
        hovertemplate='<b>%{x}</b><br>Avg Discount: %{y:.1f}%<extra></extra>'
    ))
    fig_cat_profile.update_layout(
        yaxis=dict(title='Units Sold'),
        yaxis2=dict(
            title='Avg Discount (%)',
            overlaying='y',
            side='right',
            showgrid=False
        )
    )
    fig_cat_profile = apply_theme(fig_cat_profile, theme=active_theme, height=320)

    # --- Chart 7: Customer Type Breakdown ---
    cust_data = filtered_df.groupby('Customer_Type').agg(
        Revenue=('Sales_Amount', 'sum'),
        Transactions=('Product_ID', 'count')
    ).reset_index()

    fig_cust = px.pie(
        cust_data,
        names='Customer_Type',
        values='Revenue',
        hole=0.55,
        color='Customer_Type',
        color_discrete_map={'Returning': t['cyan'], 'New': t['emerald']}
    )
    fig_cust.update_traces(
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>'
    )
    fig_cust = apply_theme(fig_cust, theme=active_theme, height=320)

    # --- Chart 8: Payment Methods by Sales Channel ---
    pay_chan = filtered_df.groupby(['Sales_Channel', 'Payment_Method'])['Sales_Amount'].sum().reset_index()
    fig_pay = px.bar(
        pay_chan,
        x='Sales_Channel',
        y='Sales_Amount',
        color='Payment_Method',
        barmode='stack',
        color_discrete_sequence=[t['blue'], t['amber'], t['rose']],
        labels={'Sales_Channel': 'Sales Channel', 'Sales_Amount': 'Revenue ($)'}
    )
    fig_pay.update_traces(hovertemplate='<b>%{x} - %{data.name}</b><br>Revenue: $%{y:,.2f}<extra></extra>')
    fig_pay = apply_theme(fig_pay, theme=active_theme, height=320)

    # --- Chart 9: Region & Rep Sunburst Hierarchy ---
    fig_sunburst = px.sunburst(
        filtered_df,
        path=['Region', 'Sales_Rep'],
        values='Sales_Amount',
        color='Region',
        color_discrete_sequence=colors
    )
    fig_sunburst.update_traces(
        hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.2f}<extra></extra>'
    )
    fig_sunburst = apply_theme(fig_sunburst, theme=active_theme, height=320)

    # DataTable Records Preparation
    table_df = filtered_df.copy()
    table_df['Sale_Date_Str'] = table_df['Sale_Date'].dt.strftime('%Y-%m-%d')
    table_df['Sales_Amount_Str'] = table_df['Sales_Amount'].map(lambda x: f"${x:,.2f}")
    table_df['Unit_Price_Str'] = table_df['Unit_Price'].map(lambda x: f"${x:,.2f}")
    table_df['Unit_Cost_Str'] = table_df['Unit_Cost'].map(lambda x: f"${x:,.2f}")
    table_df['Discount_Str'] = table_df['Discount'].map(lambda x: f"{x * 100:.1f}%")

    table_records = table_df[[
        'Product_ID', 'Sale_Date_Str', 'Product_Category', 'Sales_Rep',
        'Region', 'Sales_Amount_Str', 'Quantity_Sold', 'Unit_Price_Str',
        'Unit_Cost_Str', 'Discount_Str', 'Customer_Type', 'Payment_Method',
        'Sales_Channel'
    ]].to_dict('records')

    return (
        rev_str, kpi_rev_sub,
        qty_str, orders_str, aov_str, discount_str,
        fig_monthly, fig_cat, fig_rep,
        fig_scatter, fig_top, fig_cat_profile,
        fig_cust, fig_pay, fig_sunburst,
        table_records,
        style_header, style_data, style_data_conditional, style_table
    )

if __name__ == '__main__':
    app.run(debug=True, port=8050)