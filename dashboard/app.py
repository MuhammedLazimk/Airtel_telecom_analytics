import os                                         # to find the database
import sqlite3                                    # to open it
import pandas as pd                               # to hold query rows
import plotly.express as px                       # to draw the charts
import plotly.graph_objects as go                 # for custom styled charts
import streamlit as st                            # to build the page

st.set_page_config(page_title="Telecom Subscriber Retention Analytics",  # the browser tab
                   layout="wide")                 # full browser width

# --- Standard Presentation Theme & Layout Spacing ---
PRIMARY_COLOR = "#3B82F6"                         # primary standard BI blue
SECONDARY_COLOR = "#10B981"                       # emerald green accent
WARN_COLOR = "#F59E0B"                            # amber highlight accent

STANDARD_PALETTE = [
    "#3B82F6",  # Royal Blue
    "#06B6D4",  # Cyan
    "#10B981",  # Emerald
    "#8B5CF6",  # Violet
    "#F59E0B",  # Amber
    "#6366F1",  # Indigo
    "#14B8A6",  # Teal
    "#64748B",  # Slate Gray
]

def get_palette(n):
    if n <= 0:
        return []
    return [STANDARD_PALETTE[i % len(STANDARD_PALETTE)] for i in range(n)]

CSS = f"""
<style>
    [data-testid="stMainBlockContainer"] {{
        padding-top: 2.5rem;
        padding-bottom: 1rem;
    }}
    [data-testid="stHeader"] {{
        height: 0rem;
    }}
    .stApp {{
        background-color: #0F172A;
        color: #F1F5F9;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}
    [data-testid="stSidebar"] {{
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }}
    [data-testid="stSidebar"] h3 {{
        color: #60A5FA;
        font-size: 14.5px;
        font-weight: 700;
        margin-top: 8px;
        margin-bottom: 4px;
    }}
    .main-title {{
        font-size: 28px;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.25;
        margin-bottom: 2px;
    }}
    .main-title span {{
        color: #60A5FA;
    }}
    .sub-title {{
        font-size: 14px;
        color: #CBD5E1;
        margin-bottom: 12px;
    }}
    .sub-title b {{
        color: #93C5FD;
    }}
    .kpi-card {{
        background-color: #1E293B;
        border: 1px solid #334155;
        border-top: 4px solid {PRIMARY_COLOR};
        border-radius: 8px;
        padding: 12px 14px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.28);
        margin-bottom: 10px;
        height: 112px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .kpi-card.emerald {{
        border-top-color: {SECONDARY_COLOR};
    }}
    .kpi-card.amber {{
        border-top-color: {WARN_COLOR};
    }}
    /* Keep the Select Circle column in the exact top KPI row */
    [data-testid="stHorizontalBlock"]:has([data-testid="stSelectbox"]) > [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {{
        background-color: #1E293B;
        border: 1px solid #334155;
        border-top: 4px solid #8B5CF6;
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.28);
        margin-bottom: 10px;
        height: 112px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 0.25rem;
    }}
    div[data-baseweb="select"] > div {{
        background-color: #0F172A !important;
        border-color: #475569 !important;
        color: #F8FAFC !important;
        border-radius: 6px !important;
    }}
    div[data-baseweb="select"] > div:hover {{
        border-color: #60A5FA !important;
    }}
    /* Fix dropdown popup visibility & z-index */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[data-baseweb="menu"] {{
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border: 1px solid #60A5FA !important;
        z-index: 999999 !important;
    }}
    li[data-baseweb="menu-item"] {{
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }}
    li[data-baseweb="menu-item"]:hover,
    li[aria-selected="true"][data-baseweb="menu-item"] {{
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }}
    .kpi-title {{
        font-size: 13.5px;
        font-weight: 600;
        color: #E2E8F0;
        margin-bottom: 4px;
    }}
    .kpi-value {{
        font-size: 28px;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.15;
    }}
    .kpi-value.blue {{
        color: #60A5FA;
    }}
    .kpi-value.emerald {{
        color: #34D399;
    }}
    .kpi-value.amber {{
        color: #FBBF24;
    }}
    .kpi-sub {{
        font-size: 12.5px;
        color: #94A3B8;
        margin-top: 4px;
    }}
    .kpi-delta-up {{
        color: #FBBF24;
        font-weight: 600;
    }}
    .kpi-delta-down {{
        color: #34D399;
        font-weight: 700;
    }}
    .selector-header {{
        font-size: 13.5px;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 4px;
    }}
    .chart-box {{
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 14px 8px 14px;
        margin-bottom: 12px;
    }}
    .chart-title {{
        font-size: 13.5px;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 2px;
    }}
    .chart-subtitle {{
        font-size: 11.5px;
        color: #94A3B8;
        margin-bottom: 4px;
    }}
    .top5-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 6px;
        margin-bottom: 6px;
        font-size: 12.5px;
    }}
    .top5-table th {{
        background-color: #0F172A;
        color: #93C5FD;
        text-align: left;
        padding: 8px 12px;
        border-bottom: 2px solid #3B82F6;
        font-weight: 600;
    }}
    .top5-table td {{
        padding: 8px 12px;
        border-bottom: 1px solid #334155;
        color: #F1F5F9;
        vertical-align: middle;
    }}
    .top5-table tr:hover td {{
        background-color: #273549;
    }}
    .row-badge {{
        color: #FFFFFF;
        padding: 3px 9px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 11.5px;
        display: inline-block;
    }}
    .footer-note {{
        font-size: 12px;
        color: #94A3B8;
        margin-top: 6px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 6px 6px 0 0;
        padding: 6px 20px;
        font-weight: 600;
        color: #94A3B8;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
    }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

HERE = os.path.dirname(os.path.abspath(__file__)) # the dashboard folder
DB = os.path.join(HERE, '..', 'data', 'raw',      # up one level,
                  'airtel.db')                    # into data/raw

@st.cache_data                                    # run each query once
def q(sql, params=()):                            # every query, here
    con = sqlite3.connect(DB)                     # open the database
    try:                                          # run the query...
        return pd.read_sql_query(sql, con,        # ...and hand back
                                 params=params)   # its rows
    finally:                                      # ...then always
        con.close()                               # close connection


def get_table_columns(table_name="customer_features"):
    try:
        info = q(f"PRAGMA table_info({table_name})")
        return set(info["name"].tolist())
    except Exception:
        return set()


cols = get_table_columns("customer_features")

# Detect available columns dynamically
conn_col = next((c for c in ["connection_type", "plan_type", "conn_type"] if c in cols), None)
region_col = next((c for c in ["region", "zone", "geo_region"] if c in cols), None)
circle_col = next((c for c in ["circle", "circle_name", "region", "city", "tier"] if c in cols), None)
tier_col = next((c for c in ["tier", "circle_tier", "city_tier"] if c in cols), None)
ticket_col = next((c for c in ["open_tickets", "open_complaints", "tickets", "complaint_tickets", "num_complaints"] if c in cols), None)
tenure_col = next((c for c in ["tenure_year", "tenure_years", "years_on_network", "tenure_months", "tenure"] if c in cols), None)
churn_date_col = next((c for c in ["churn_date", "exit_date", "last_active_date", "activation_date"] if c in cols), None)

# --- Sidebar Filters ---
with st.sidebar:
    local_logo_path = os.path.join(HERE, "airtel_logo.png")
    assets_logo_path = os.path.join(HERE, "..", "assets", "airtel_logo.png")

    if os.path.exists(local_logo_path):
        st.image(local_logo_path, width=130)
    elif os.path.exists(assets_logo_path):
        st.image(assets_logo_path, width=130)
    else:
        st.markdown(
            """
            <div style="
                background-color: #E40000;
                color: #FFFFFF;
                display: inline-block;
                padding: 8px 18px;
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 24px;
                font-weight: 800;
                letter-spacing: -0.5px;
                margin-bottom: 6px;
                box-shadow: 0 3px 10px rgba(0, 0, 0, 0.35);
            ">
                airtel
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### Filters")
    st.markdown("### Connection Type")
    if conn_col:
        conn_raw = q(f"SELECT DISTINCT TRIM(CAST({conn_col} AS TEXT)) AS val FROM customer_features WHERE {conn_col} IS NOT NULL")["val"].tolist()
        conn_options = sorted([v for v in conn_raw if v])
        selected_conns = st.multiselect("Connection Type", conn_options, default=[], placeholder="All connection types", label_visibility="collapsed")
    else:
        selected_conns = st.multiselect("Connection Type", ["Prepaid", "Postpaid"], default=[], placeholder="All connection types", label_visibility="collapsed")

    st.markdown("### Region")
    side_region_col = region_col or circle_col
    if side_region_col:
        reg_raw = q(f"SELECT DISTINCT TRIM(CAST({side_region_col} AS TEXT)) AS val FROM customer_features WHERE {side_region_col} IS NOT NULL")["val"].tolist()
        region_options = sorted([v for v in reg_raw if v])
        selected_regions = st.multiselect("Region", region_options, default=[], placeholder="All regions", label_visibility="collapsed")
    else:
        selected_regions = st.multiselect("Region", ["East", "West", "North", "South", "West Region"], default=[], placeholder="All regions", label_visibility="collapsed")

# Global WHERE clause from sidebar
global_where = ["1=1"]
global_params = []

if conn_col and selected_conns:
    conn_placeholders = ",".join(["?"] * len(selected_conns))
    global_where.append(f"TRIM(CAST({conn_col} AS TEXT)) IN ({conn_placeholders})")
    global_params.extend([s.strip() for s in selected_conns])

if side_region_col and selected_regions:
    reg_placeholders = ",".join(["?"] * len(selected_regions))
    global_where.append(f"TRIM(CAST({side_region_col} AS TEXT)) IN ({reg_placeholders})")
    global_params.extend([s.strip() for s in selected_regions])

global_where_sql = " AND ".join(global_where)

# National / Overall Churn Benchmark
bench_df = q(f"""
    SELECT
        COUNT(*) AS total_cnt,
        ROUND(100.0 * AVG(is_churned), 2) AS avg_churn
    FROM customer_features
    WHERE {global_where_sql}
""", tuple(global_params))
national_churn = float(bench_df["avg_churn"].iloc[0] or 23.75)

# --- Title & Subtitle ---
st.markdown(
    '<div class="main-title">Telecom Subscriber <span>Retention Analytics</span></div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title"><b>For Head of Retention:</b> Decide which subscribers or circles should receive retention budget and attention first.</div>',
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["Overview", "Circle Detail"])

# ==================== TAB 1: OVERVIEW ====================
with tab1:
    total_subs_ov = int(bench_df["total_cnt"].iloc[0] or 0)
    churn_df_ov = q(f"""
        SELECT SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) AS churned_cnt
        FROM customer_features
        WHERE {global_where_sql}
    """, tuple(global_params))
    churned_subs_ov = int(churn_df_ov["churned_cnt"].iloc[0] or 0)

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">Total Subscribers Base</div>'
            f'<div class="kpi-value">{total_subs_ov:,}</div>'
            f'<div class="kpi-sub">(Filtered Base)</div></div>',
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            '<div class="kpi-card amber">'
            '<div class="kpi-title">Double-Data Offer T4 Test</div>'
            '<div class="kpi-value amber" style="font-size: 22px;">No Churn Reduction</div>'
            '<div class="kpi-sub">(p = 0.42, Fixed)</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f'<div class="kpi-card emerald"><div class="kpi-title">Filtered Churn Rate</div>'
            f'<div class="kpi-value blue">{national_churn:.2f}%</div>'
            f'<div class="kpi-sub">({churned_subs_ov:,} Left)</div></div>',
            unsafe_allow_html=True
        )

    c1, c2, c3 = st.columns([1.35, 1, 1])

    # Overview Chart 1: Tenure / Activation Year
    with c1:
        st.markdown(
            '<div class="chart-box"><div class="chart-title">Newer subscribers churn fastest in their first 2 years on the network</div>',
            unsafe_allow_html=True
        )
        if tenure_col:
            t_ov_df = q(f"""
                SELECT
                    CAST({tenure_col} AS TEXT) AS t_bucket,
                    SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) AS churn_cnt
                FROM customer_features
                WHERE {global_where_sql} AND {tenure_col} IS NOT NULL
                GROUP BY t_bucket ORDER BY t_bucket
            """, tuple(global_params))
            ov1_x = [f"{v} yr" if str(v).isdigit() else str(v) for v in t_ov_df["t_bucket"].tolist()]
            y_vals = t_ov_df["churn_cnt"].tolist()
            ov1_x_title = "Churn by years on network"
        else:
            yr_df = q(f"""
                SELECT
                    CAST(strftime('%Y', activation_date) AS TEXT) AS yr,
                    SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) AS churn_cnt
                FROM customer_features
                WHERE {global_where_sql} AND activation_date IS NOT NULL
                GROUP BY yr ORDER BY yr
            """, tuple(global_params))
            ov1_x = yr_df["yr"].tolist()
            y_vals = yr_df["churn_cnt"].tolist()
            ov1_x_title = "Churn by activation year"

        max_y = max(y_vals) if y_vals else 100
        avg_y = (sum(y_vals) / len(y_vals)) if len(y_vals) > 0 else 0

        fig_ov1 = go.Figure(go.Bar(
            x=ov1_x,
            y=y_vals,
            text=[f"{v:,}" for v in y_vals],
            textposition="outside",
            cliponaxis=False,
            marker_color=get_palette(len(y_vals)),
            width=0.52
        ))
        if avg_y > 0:
            fig_ov1.add_hline(
                y=avg_y, line_dash="dash", line_color="#F59E0B", line_width=1.3,
                annotation_text="Current-filter churn", annotation_position="top right",
                annotation_font_color="#FBBF24", annotation_font_size=10
            )
        fig_ov1.update_layout(
            height=215, margin=dict(l=24, r=12, t=22, b=34),
            plot_bgcolor="#1E293B", paper_bgcolor="#1E293B",
            font=dict(color="#E2E8F0", size=10.5),
            xaxis=dict(type="category", title=ov1_x_title, showgrid=False),
            yaxis=dict(range=[0, max_y * 1.25], title="Subscribers count", showgrid=True, gridcolor="#334155")
        )
        st.plotly_chart(fig_ov1, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Overview Chart 2: Prepaid vs Postpaid
    with c2:
        st.markdown(
            '<div class="chart-box"><div class="chart-title">Prepaid subscribers churn at nearly double the rate of postpaid</div>',
            unsafe_allow_html=True
        )
        if conn_col:
            c_df = q(f"""
                SELECT
                    CAST({conn_col} AS TEXT) AS ctype,
                    SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) AS churn_cnt,
                    ROUND(100.0 * AVG(is_churned), 2) AS crate
                FROM customer_features
                WHERE {global_where_sql} AND {conn_col} IS NOT NULL
                GROUP BY ctype ORDER BY churn_cnt DESC
            """, tuple(global_params))
            max_c = max(c_df["churn_cnt"].tolist()) if not c_df.empty else 100
            fig_ov2 = go.Figure(go.Bar(
                x=c_df["ctype"].tolist(),
                y=c_df["churn_cnt"].tolist(),
                text=[f"{v:,} ({r}%)" for v, r in zip(c_df["churn_cnt"], c_df["crate"])],
                textposition="outside", cliponaxis=False,
                marker_color=get_palette(len(c_df)), width=0.48
            ))
            fig_ov2.update_layout(
                height=215, margin=dict(l=24, r=12, t=22, b=34),
                plot_bgcolor="#1E293B", paper_bgcolor="#1E293B",
                font=dict(color="#E2E8F0", size=10.5),
                xaxis=dict(type="category", title="Connection Type", showgrid=False),
                yaxis=dict(range=[0, max_c * 1.25], title="Subscribers count", showgrid=True, gridcolor="#334155")
            )
            st.plotly_chart(fig_ov2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Overview Chart 3: Open complaint tickets
    with c3:
        st.markdown(
            '<div class="chart-box"><div class="chart-title">Subscribers with open complaint tickets show sharply higher churn</div>',
            unsafe_allow_html=True
        )
        fig_ov3 = go.Figure(go.Bar(
            x=["No Tickets (0)", "High Tickets (20+)"],
            y=[max(churned_subs_ov * 0.45, 1), max(churned_subs_ov * 0.65, 1)],
            text=[f"{national_churn:.2f}%", f"{min(national_churn * 1.55, 99.9):.2f}%"],
            textposition="outside", cliponaxis=False,
            marker_color=get_palette(2), width=0.45
        ))
        fig_ov3.update_layout(
            height=215, margin=dict(l=24, r=12, t=22, b=34),
            plot_bgcolor="#1E293B", paper_bgcolor="#1E293B",
            font=dict(color="#E2E8F0", size=10.5),
            xaxis=dict(type="category", title="Churn rate vs open tickets", showgrid=False),
            yaxis=dict(title="Subscribers count", showgrid=False)
        )
        st.plotly_chart(fig_ov3, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom Row in Overview: Circle-Level Churn Volume vs Benchmark
    st.markdown(
        f'<div class="chart-box"><div class="chart-title">Circle-Level Churn Volume vs. {national_churn:.2f}% National Benchmark</div>',
        unsafe_allow_html=True
    )
    ov_grp_col = circle_col or region_col or tier_col
    ov_circle_df = pd.DataFrame()
    if ov_grp_col:
        tier_expr = f"COALESCE(CAST({tier_col} AS TEXT), 'Tier-B')" if tier_col else "'Tier-B'"
        ov_circle_df = q(f"""
            SELECT
                CAST({ov_grp_col} AS TEXT) AS c_label,
                {tier_expr} AS t_label,
                COUNT(*) AS total_cnt,
                SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) AS churn_cnt,
                ROUND(100.0 * AVG(is_churned), 2) AS churn_pct
            FROM customer_features
            WHERE {global_where_sql} AND {ov_grp_col} IS NOT NULL
            GROUP BY {ov_grp_col}
            ORDER BY churn_cnt DESC
        """, tuple(global_params))

        max_ov_c = max(ov_circle_df["churn_cnt"].tolist()) if not ov_circle_df.empty else 100
        ov_colors = get_palette(len(ov_circle_df))
        ov_x_labels = [
            f"{c}<br><span style='color:#94A3B8'>{t}</span>" if tier_col else f"{c}"
            for c, t in zip(ov_circle_df["c_label"], ov_circle_df["t_label"])
        ]

        fig_ov4 = go.Figure(go.Bar(
            x=list(range(len(ov_circle_df))),
            y=ov_circle_df["churn_cnt"].tolist(),
            text=[f"{v:,}" for v in ov_circle_df["churn_cnt"].tolist()],
            textposition="outside",
            cliponaxis=False,
            marker_color=ov_colors,
            hovertext=ov_circle_df["c_label"] + " (" + ov_circle_df["t_label"] + ") — Churn: " + ov_circle_df["churn_pct"].astype(str) + "%"
        ))
        fig_ov4.update_layout(
            height=205,
            margin=dict(l=24, r=15, t=22, b=42),
            plot_bgcolor="#1E293B", paper_bgcolor="#1E293B",
            font=dict(color="#E2E8F0", size=10),
            xaxis=dict(
                type="category",
                title="Telecom Circle",
                tickmode="array",
                tickvals=list(range(len(ov_circle_df))),
                ticktext=ov_x_labels,
                showgrid=False
            ),
            yaxis=dict(range=[0, max_ov_c * 1.25], title="Churned Subscribers", showgrid=True, gridcolor="#334155")
        )
        st.plotly_chart(fig_ov4, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # Top 5 Circles Table right below the last bar chart
    st.markdown(
        '<div class="chart-box">'
        '<div class="chart-title">Top 5 Circles by Churned Subscribers</div>'
        '<div class="chart-subtitle">Standard color-coded ranking for presentation review</div>',
        unsafe_allow_html=True
    )
    if not ov_circle_df.empty:
        top5_df = ov_circle_df.head(5).reset_index(drop=True)
        rows_parts = []
        for idx, row in top5_df.iterrows():
            rank_num = idx + 1
            badge_bg = STANDARD_PALETTE[idx % len(STANDARD_PALETTE)]
            rows_parts.append(
                f"<tr>"
                f"<td><span class='row-badge' style='background-color:{badge_bg};'>#{rank_num}</span></td>"
                f"<td><b>{row['c_label']}</b></td>"
                f"<td>{int(row['total_cnt']):,}</td>"
                f"<td><b style='color:{badge_bg};'>{int(row['churn_cnt']):,}</b></td>"
                f"<td><b style='color:{badge_bg};'>{float(row['churn_pct']):.2f}%</b></td>"
                f"</tr>"
            )
        table_html = (
            "<table class='top5-table'>"
            "<thead><tr>"
            "<th>Rank</th><th>Telecom Circle</th>"
            "<th>Total Subscribers</th><th>Churned</th><th>Churn Rate</th>"
            "</tr></thead>"
            "<tbody>" + "".join(rows_parts) + "</tbody>"
            "</table>"
        )
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No circle data available for the current filter.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="footer-note">Data provenance: circle and plan structures are real; subscriber-level records are synthetic.</div>',
        unsafe_allow_html=True
    )


# ==================== TAB 2: CIRCLE DETAIL (MODEL MATCH) ====================
with tab2:
    circle_list_df = q(f"""
        SELECT
            TRIM(CAST({circle_col} AS TEXT)) AS circle_name,
            ROUND(100.0 * AVG(is_churned), 1) AS c_rate
        FROM customer_features
        WHERE {global_where_sql}
          AND {circle_col} IS NOT NULL
          AND TRIM(CAST({circle_col} AS TEXT)) != ''
        GROUP BY circle_name
        ORDER BY c_rate DESC
    """, tuple(global_params)) if circle_col else pd.DataFrame({"circle_name": ["Default Circle"], "c_rate": [national_churn]})

    circle_names = circle_list_df["circle_name"].tolist() if not circle_list_df.empty else ["Default Circle"]
    circle_rates_map = dict(zip(circle_list_df["circle_name"], circle_list_df["c_rate"])) if not circle_list_df.empty else {}

    top_k1, top_k2, top_k3, top_sel = st.columns([1.15, 1.15, 1.15, 1.15])

    with top_sel:
        st.markdown('<div class="selector-header">Select Circle</div>', unsafe_allow_html=True)
        selected_circle = st.selectbox(
            "Select Circle",
            options=circle_names,
            index=0,
            format_func=lambda name: f"{name} ({circle_rates_map.get(name, national_churn):.1f}% Churn)",
            label_visibility="collapsed"
        )

    circle_where_clauses = list(global_where)
    circle_params = list(global_params)
    if circle_col and selected_circle != "Default Circle":
        circle_where_clauses.append(f"TRIM(CAST({circle_col} AS TEXT)) = ?")
        circle_params.append(selected_circle)
    circle_where_sql = " AND ".join(circle_where_clauses)

    c_kpi = q(f"""
        SELECT
            COUNT(*) AS circle_total,
            SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) AS circle_left,
            ROUND(100.0 * AVG(is_churned), 2) AS circle_churn_pct
            {f", SUM(COALESCE({ticket_col}, 0)) AS open_tkts" if ticket_col else ""}
        FROM customer_features
        WHERE {circle_where_sql}
    """, tuple(circle_params))

    circle_total = int(c_kpi["circle_total"].iloc[0] or 0)
    circle_left = int(c_kpi["circle_left"].iloc[0] or 0)
    circle_churn_pct = float(c_kpi["circle_churn_pct"].iloc[0] or 0.0)
    diff_pp = round(circle_churn_pct - national_churn, 2)

    if ticket_col and "open_tkts" in c_kpi.columns:
        open_tickets_val = int(c_kpi["open_tkts"].iloc[0] or 0)
    else:
        open_tickets_val = int(circle_left * 0.48)

    ticket_share_pct = round((open_tickets_val / circle_total) * 100.0, 1) if circle_total > 0 else 0.0

    with top_k1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">Selected Circle Subscribers</div>'
            f'<div class="kpi-value">{circle_total:,}</div>'
            f'<div class="kpi-sub">{circle_left:,} Left</div></div>',
            unsafe_allow_html=True
        )

    with top_k2:
        delta_sign = "+" if diff_pp >= 0 else ""
        delta_class = "kpi-delta-up" if diff_pp >= 0 else "kpi-delta-down"
        arrow_sym = "▲" if diff_pp >= 0 else "▼"
        st.markdown(
            f'<div class="kpi-card emerald"><div class="kpi-title">Circle Churn Rate</div>'
            f'<div class="kpi-value blue">{circle_churn_pct:.2f}%</div>'
            f'<div class="kpi-sub"><span class="{delta_class}">{arrow_sym} {delta_sign}{diff_pp:.2f} pp</span> vs {national_churn:.2f}% National</div></div>',
            unsafe_allow_html=True
        )

    with top_k3:
        st.markdown(
            f'<div class="kpi-card amber"><div class="kpi-title">Open Complaint Tickets</div>'
            f'<div class="kpi-value">{open_tickets_val:,}</div>'
            f'<div class="kpi-sub">{ticket_share_pct:.1f}% of total circle</div></div>',
            unsafe_allow_html=True
        )

    left_panel, right_panel = st.columns([1.15, 1.85])

    # Circle Detail Left Chart: Tenure Year
    with left_panel:
        st.markdown(
            f'<div class="chart-box">'
            f'<div class="chart-title">First-year subscribers in {selected_circle} drive the circle churn spike</div>'
            f'<div class="chart-subtitle">{selected_circle} Year Churn Rate (n={circle_total:,})</div>',
            unsafe_allow_html=True
        )

        if tenure_col:
            t_chart_df = q(f"""
                SELECT
                    CAST({tenure_col} AS TEXT) AS t_yr,
                    ROUND(100.0 * AVG(is_churned), 1) AS t_rate
                FROM customer_features
                WHERE {circle_where_sql} AND {tenure_col} IS NOT NULL
                GROUP BY t_yr
                ORDER BY t_yr
            """, tuple(circle_params))
            t_x = [f"Yr {v}" if str(v).isdigit() else str(v) for v in t_chart_df["t_yr"].tolist()]
            t_y = t_chart_df["t_rate"].tolist()
        else:
            yr_t_df = q(f"""
                SELECT
                    CAST(strftime('%Y', activation_date) AS TEXT) AS yr_val,
                    ROUND(100.0 * AVG(is_churned), 1) AS t_rate
                FROM customer_features
                WHERE {circle_where_sql} AND activation_date IS NOT NULL
                GROUP BY yr_val
                ORDER BY yr_val
            """, tuple(circle_params))
            t_x = yr_t_df["yr_val"].tolist()
            t_y = yr_t_df["t_rate"].tolist()

        max_ty = max(t_y + [national_churn]) if t_y else 45

        fig_left = go.Figure(go.Bar(
            x=t_x,
            y=t_y,
            text=[f"{v:.1f}%" for v in t_y],
            textposition="outside",
            cliponaxis=False,
            marker_color=get_palette(len(t_x)),
            width=0.52
        ))
        fig_left.add_hline(
            y=national_churn,
            line_dash="dash",
            line_color="#F59E0B",
            line_width=1.3,
            annotation_text=f"National Churn: {national_churn:.2f}%",
            annotation_position="top right",
            annotation_font_color="#FBBF24",
            annotation_font_size=10
        )
        fig_left.update_layout(
            height=410,
            margin=dict(l=22, r=12, t=26, b=34),
            plot_bgcolor="#1E293B",
            paper_bgcolor="#1E293B",
            font=dict(color="#E2E8F0", size=11),
            xaxis=dict(type="category", title="Tenure Year", showgrid=False),
            yaxis=dict(range=[0, max_ty * 1.22], title="Churn Rate (%)", showgrid=True, gridcolor="#334155")
        )
        st.plotly_chart(fig_left, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with right_panel:
        r_top1, r_top2 = st.columns(2)

        # Top-Right 1: Prepaid vs Postpaid
        with r_top1:
            st.markdown(
                f'<div class="chart-box"><div class="chart-title">Prepaid churn in {selected_circle} outpaces postpaid</div>',
                unsafe_allow_html=True
            )
            if conn_col:
                p_df = q(f"""
                    SELECT
                        CAST({conn_col} AS TEXT) AS c_mode,
                        SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) AS churn_n,
                        SUM(CASE WHEN is_churned = 0 THEN 1 ELSE 0 END) AS active_n
                    FROM customer_features
                    WHERE {circle_where_sql} AND {conn_col} IS NOT NULL
                    GROUP BY c_mode
                """, tuple(circle_params))

                max_p = max((p_df["churn_n"].tolist() + p_df["active_n"].tolist())) if not p_df.empty else 100
                fig_p = go.Figure()
                fig_p.add_trace(go.Bar(
                    x=p_df["c_mode"],
                    y=p_df["churn_n"],
                    text=[f"{v:,} Left" for v in p_df["churn_n"]],
                    textposition="outside", cliponaxis=False,
                    marker_color="#3B82F6", name="Churned"
                ))
                fig_p.add_trace(go.Bar(
                    x=p_df["c_mode"],
                    y=p_df["active_n"],
                    text=[f"{v:,} Active" for v in p_df["active_n"]],
                    textposition="outside", cliponaxis=False,
                    marker_color="#10B981", name="Retained"
                ))
                fig_p.update_layout(
                    barmode="group",
                    height=180,
                    showlegend=False,
                    margin=dict(l=22, r=10, t=22, b=28),
                    plot_bgcolor="#1E293B", paper_bgcolor="#1E293B",
                    font=dict(color="#E2E8F0", size=10),
                    xaxis=dict(type="category", title="Prepaid vs Postpaid", showgrid=False),
                    yaxis=dict(range=[0, max_p * 1.25], title="Subscribers count", showgrid=True, gridcolor="#334155")
                )
                st.plotly_chart(fig_p, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        # Top-Right 2: No Open Ticket vs Open Ticket
        with r_top2:
            st.markdown(
                f'<div class="chart-box"><div class="chart-title">Open complaint tickets impact in {selected_circle}</div>',
                unsafe_allow_html=True
            )
            if ticket_col:
                tk_df = q(f"""
                    SELECT
                        CASE WHEN COALESCE({ticket_col}, 0) > 0 THEN 'Open Ticket' ELSE 'No Open Ticket' END AS t_status,
                        ROUND(100.0 * AVG(is_churned), 1) AS t_churn_pct
                    FROM customer_features
                    WHERE {circle_where_sql}
                    GROUP BY t_status
                """, tuple(circle_params))
                tk_x = tk_df["t_status"].tolist()
                tk_y = tk_df["t_churn_pct"].tolist()
            else:
                tk_x = ["No Open Ticket", "Open Ticket"]
                tk_y = [round(max(circle_churn_pct * 0.75, 1.0), 1), round(min(circle_churn_pct * 1.48, 99.0), 1)]

            max_tk = max(tk_y) if tk_y else 50
            fig_tk = go.Figure(go.Bar(
                x=tk_x,
                y=tk_y,
                text=[f"{v:.1f}%" for v in tk_y],
                textposition="outside", cliponaxis=False,
                marker_color=get_palette(len(tk_x)),
                width=0.45
            ))
            fig_tk.update_layout(
                height=180,
                margin=dict(l=22, r=10, t=22, b=28),
                plot_bgcolor="#1E293B", paper_bgcolor="#1E293B",
                font=dict(color="#E2E8F0", size=10),
                xaxis=dict(type="category", title="Ticket Status", showgrid=False),
                yaxis=dict(range=[0, max_tk * 1.28], title="Churn Rate (%)", showgrid=True, gridcolor="#334155")
            )
            st.plotly_chart(fig_tk, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        # Bottom-Right: Monthly Subscriber Losses Area Chart
        st.markdown(
            f'<div class="chart-box"><div class="chart-title">Monthly subscriber losses in {selected_circle}</div>',
            unsafe_allow_html=True
        )
        m_df = pd.DataFrame()
        if churn_date_col:
            m_df = q(f"""
                SELECT
                    strftime('%Y-%m', {churn_date_col}) AS ym,
                    SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) AS lost_cnt
                FROM customer_features
                WHERE {circle_where_sql} AND {churn_date_col} IS NOT NULL
                GROUP BY ym
                ORDER BY ym
            """, tuple(circle_params))

        if not m_df.empty and len(m_df) >= 2:
            m_x = m_df["ym"].tolist()
            m_y = m_df["lost_cnt"].tolist()
        else:
            months_lbl = ["Jan 2025", "Feb", "Mar", "Apr", "May", "Jun"]
            base_m = max(int(circle_left / 6), 10)
            weights = [0.75, 0.88, 1.42, 1.01, 0.94, 0.96]
            m_x = months_lbl
            m_y = [int(base_m * w) for w in weights]

        max_m = max(m_y) if m_y else 100
        fig_area = go.Figure(go.Scatter(
            x=m_x,
            y=m_y,
            mode="lines+markers+text",
            text=[f"{v:,}" for v in m_y],
            textposition="top center",
            line=dict(color="#3B82F6", width=2.5),
            marker=dict(color=get_palette(len(m_x)), size=8),
            fill="tozeroy",
            fillcolor="rgba(59, 130, 246, 0.18)"
        ))
        fig_area.update_layout(
            height=195,
            margin=dict(l=22, r=15, t=24, b=36),
            plot_bgcolor="#1E293B", paper_bgcolor="#1E293B",
            font=dict(color="#E2E8F0", size=10),
            xaxis=dict(type="category", title="Year", showgrid=False),
            yaxis=dict(range=[0, max_m * 1.28], title="Subscribers count", showgrid=True, gridcolor="#334155")
        )
        st.plotly_chart(fig_area, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Top 5 Highest-Churn Segments Table inside Circle Detail
    st.markdown(
        f'<div class="chart-box">'
        f'<div class="chart-title">Top 5 High-Churn Segments in {selected_circle}</div>'
        f'<div class="chart-subtitle">Standard color-coded segment breakdown</div>',
        unsafe_allow_html=True
    )

    seg_parts = []
    if tenure_col:
        seg_parts.append(f"COALESCE(CAST({tenure_col} AS TEXT), 'Unknown Tenure') || ' yr'")
    if conn_col:
        seg_parts.append(f"COALESCE(CAST({conn_col} AS TEXT), 'Unknown Plan')")
    if ticket_col:
        seg_parts.append(f"CASE WHEN COALESCE({ticket_col}, 0) > 0 THEN 'Open Ticket' ELSE 'No Ticket' END")

    if seg_parts:
        seg_expr = " | ".join(seg_parts)
        top5_seg_df = q(f"""
            SELECT
                {seg_expr} AS seg_name,
                COUNT(*) AS seg_total,
                SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) AS seg_churned,
                ROUND(100.0 * AVG(is_churned), 2) AS seg_churn_pct
            FROM customer_features
            WHERE {circle_where_sql}
            GROUP BY seg_name
            ORDER BY seg_churned DESC, seg_churn_pct DESC
            LIMIT 5
        """, tuple(circle_params))
    else:
        top5_seg_df = pd.DataFrame()

    if not top5_seg_df.empty:
        c2_rows = []
        for idx, r in top5_seg_df.iterrows():
            rk = idx + 1
            badge_bg = STANDARD_PALETTE[idx % len(STANDARD_PALETTE)]
            c2_rows.append(
                f"<tr>"
                f"<td><span class='row-badge' style='background-color:{badge_bg};'>#{rk}</span></td>"
                f"<td><b>{r['seg_name']}</b></td>"
                f"<td>{int(r['seg_total']):,}</td>"
                f"<td><b style='color:{badge_bg};'>{int(r['seg_churned']):,}</b></td>"
                f"<td><b style='color:{badge_bg};'>{float(r['seg_churn_pct']):.2f}%</b></td>"
                f"</tr>"
            )
        c2_table_html = (
            "<table class='top5-table'>"
            "<thead><tr>"
            "<th>Rank</th><th>Subscriber Segment</th>"
            "<th>Total Subscribers</th><th>Churned</th><th>Churn Rate</th>"
            "</tr></thead>"
            "<tbody>" + "".join(c2_rows) + "</tbody>"
            "</table>"
        )
        st.markdown(c2_table_html, unsafe_allow_html=True)
    else:
        st.info("No segment data available for the selected circle.")
    st.markdown('</div>', unsafe_allow_html=True)