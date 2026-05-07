import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from ml_model import load_model
import os
from pathlib import Path
# ← set_page_config function DELETED

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "linkfields_logo 1 1.svg"

def load_css():
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">',
        unsafe_allow_html=True
    )
    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">',
        unsafe_allow_html=True
    )
    st.markdown("""
                    <style>
                        :root {

    --bg: #f8fafc;

    --surface: #ffffff;
    --surface-2: #f1f5f9;

    --border: #e5e7eb;
    --border-dark: #cbd5e1;

    --text: #111827;
    --text-muted: #6b7280;

    --blue: #3454D1;
    --purple: #4F46E5;

    --yellow: #F4B400;
}
.dark {

        /* DARK MODE */
        --bg: #0f172a;
        --surface: #111827;
        --surface-2: #1e293b;

        --border: #334155;
        --border-dark: #475569;

        --text: #f8fafc;
        --text-muted: #cbd5e1;

        --blue: #60a5fa;
        --purple: #a78bfa;
    }
            html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg); }
            #MainMenu, footer, header { visibility: hidden; }
.stApp { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); }
.main .block-container { padding-top: 1.25rem; padding-bottom: 2rem; max-width: 94%; }
section[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);

    padding-top: 0rem !important;
    padding-right: 1.2rem !important;
    padding-bottom: 1rem !important;
    padding-left: 1.2rem !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 0rem !important;
}
    .filter-card {
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 0.8rem;
        margin-bottom: 1rem;
        transition: all 0.2s;
    }
    .filter-card:hover {
        border-color: var(--border-dark);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .filter-title {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--blue);
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .filter-title i { font-size: 0.8rem; width: 1.2rem; }

    section[data-testid="stSidebar"] .stDateInput input,
    section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
        background: white !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 0.6rem 0.8rem !important;
        color: var(--text) !important;
    }
    .stMultiSelect [data-baseweb="tag"] {
        background: rgba(59,130,246,0.1) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(59,130,246,0.3) !important;
        color: var(--blue) !important;
    }

    .nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.55rem 0.85rem;
        border-radius: 10px;
        cursor: pointer;
        font-size: 0.85rem;
        color: var(--text-muted);
        font-weight: 500;
        transition: all 0.15s;
        margin-bottom: 2px;
    }
    .nav-item:hover { background: var(--surface-2); color: var(--text); }
    .nav-item.active { background: rgba(59,130,246,0.1); color: var(--blue); }

    /* hide the raw streamlit nav buttons */
    section[data-testid="stSidebar"] .stButton > button {
        position: absolute;
        opacity: 0;
        height: 50px;
        margin-top: -50px;
        width: 100%;
        cursor: pointer;
    }

        .hero-card {
            background: linear-gradient(135deg, #ffffff, #f8fafc);
            border: 1px solid var(--border);
            border-radius: 32px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        }
        .hero-title {
    font-size: 2rem;
    font-weight: 800;

    background: linear-gradient(
        135deg,
        #3454D1,
        #F4B400
    );

    -webkit-background-clip: text;
    background-clip: text;

    color: transparent;
}
        .hero-subtitle { margin-top: 0.35rem; color: var(--text-muted); }

        .kpi-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.2rem 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.2s;
        }
        .kpi-card:hover {
            border-color: var(--border-dark);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        }
        .kpi-label { font-size: 0.7rem; font-weight: 700; color: var(--blue); text-transform: uppercase; letter-spacing: 0.08em; }
        .kpi-value { font-size: 1.6rem; font-weight: 800; color: var(--text); }
        .kpi-foot { font-size: 0.7rem; color: var(--text-muted); }

        .panel-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1rem 1rem 0.6rem 1rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.2s;
        }
        .panel-card:hover {
            border-color: var(--border-dark);
            box-shadow: 0 6px 16px rgba(0,0,0,0.05);
        }
        .panel-title { font-size: 1.05rem; font-weight: 700; color: var(--text); }
        .panel-subtitle { font-size: 0.8rem; color: var(--text-muted); }

        .stButton > button {
            border-radius: 40px;
            border: none;
            background: linear-gradient(135deg, var(--blue), var(--purple));
            color: white !important;
            font-weight: 600;
            padding: 0.5rem 1.2rem;
            transition: all 0.2s;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .stPlotlyChart, .stPyplot { border-radius: 24px !important; overflow: hidden; }
        div[data-testid="stDataFrame"] {
            border-radius: 24px !important;
            border: 1px solid var(--border) !important;
            background: white !important;
        }
    </style>
    """, unsafe_allow_html=True)


def hero(title: str, subtitle: str):
    st.markdown(f'<div class="hero-card"><div class="hero-title">{title}</div><div class="hero-subtitle">{subtitle}</div></div>', unsafe_allow_html=True)

def kpi_card(label: str, value: str, foot: str = ""):
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-foot">{foot}</div></div>', unsafe_allow_html=True)

def panel_open(title: str, subtitle: str = ""):
    st.markdown(f'<div class="panel-card"><div class="panel-title">{title}</div><div class="panel-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def panel_close():
    st.markdown("</div>", unsafe_allow_html=True)

def polish_plotly(fig, height=380, line_color="#3b82f6", bar_color="#3b82f6"):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=8, r=8, t=18, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,250,252,0.9)",
        font=dict(family="Inter, sans-serif", color="#f1e900"),
        xaxis=dict(showgrid=False, zeroline=False, linecolor="#e2e8f0", tickfont=dict(color="#475569")),
        yaxis=dict(gridcolor="#e2e8f0", zeroline=False, tickfont=dict(color="#475569")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#475569"))
    )
    for trace in fig.data:
        if hasattr(trace, "line") and trace.line is not None:
            trace.line.color = line_color
        if hasattr(trace, "marker") and trace.marker is not None:
            if not isinstance(trace.marker.color, (list, tuple)):
                trace.marker.color = bar_color
    return fig


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.error("DATABASE_URL is not set")
    st.stop()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@st.cache_data
def load_table(name: str) -> pd.DataFrame:
    query = text(f"SELECT * FROM {name}")
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return pd.DataFrame(rows)

@st.cache_data
def load_all_data():
    users = load_table("users")
    activity = load_table("user_activity_log")
    features = load_table("customer_features")
    preds = load_table("customer_predictions")
    try:
        subs = load_table("subscriptions")
    except Exception:
        subs = pd.DataFrame()
    return users, activity, features, preds, subs

@st.cache_data
def convert_for_download(df):
    return df.to_csv().encode("utf-8")

df = load_table("customer_features")
csv = convert_for_download(df)

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="data.csv",
    mime="text/csv",
)

def render_sidebar():
    users, activity, features, preds, subs = load_all_data()

    # ✅ only load model once
    if "model" not in st.session_state:
        st.session_state["model"] = load_model()

    users["id"] = users["id"].astype(str)
    users["created_at"] = pd.to_datetime(users["created_at"], errors="coerce")

    with st.sidebar:

        st.markdown("""
                        <div style="
                            margin-top:-50px;
                        "></div>
                        """, unsafe_allow_html=True)


        st.markdown("""
                        <div style="
                            margin-bottom:20px;
                        "></div>
                        """, unsafe_allow_html=True)

        # st.markdown( 
        #     "### <i class='fas fa-compass'></i> Navigation",
        #     unsafe_allow_html=True
        # ),

        pages = [
            ("Dashboard",      "M3 3h7v7H3zm11 0h7v7h-7zM3 14h7v7H3zm11 0h7v7h-7z"),
            ("ML Predictions", "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"),
            ("Explainability", "M11 11a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm10 10-4.35-4.35"),
        ]

        if "page_nav" not in st.session_state:
            st.session_state["page_nav"] = "Dashboard"

        for label, icon_path in pages:
            is_active = st.session_state["page_nav"] == label
            color = "#006eb2" if is_active else "#475569"
            bg = "background:rgba(59,130,246,0.1);color:#3b82f6;" if is_active else ""
            st.markdown(
                f"""<div class="nav-item {'active' if is_active else ''}" style="{bg}">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                         stroke="{color}" stroke-width="2"
                         stroke-linecap="round" stroke-linejoin="round">
                        <path d="{icon_path}"/>
                    </svg>
                    {label}
                </div>""",
                unsafe_allow_html=True
            )
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state["page_nav"] = label
                st.rerun()

        page = st.session_state["page_nav"]

        st.markdown("---")
        st.markdown("### <i class='fas fa-sliders-h'></i> Filters", unsafe_allow_html=True)

        st.markdown("""<div class="filter-card"><div class="filter-title"><i class='fas fa-calendar-alt'></i> USER CREATION DATE</div></div>""", unsafe_allow_html=True)
        min_date = users["created_at"].min().date() if users["created_at"].notna().any() else datetime.today().date() - timedelta(days=30)
        max_date = users["created_at"].max().date() if users["created_at"].notna().any() else datetime.today().date()
        date_range = st.date_input("", value=(min_date, max_date), min_value=min_date, max_value=max_date, label_visibility="collapsed")

        st.markdown("""<div class="filter-card"><div class="filter-title"><i class='fas fa-user-tag'></i> USER ROLE</div></div>""", unsafe_allow_html=True)
        role_options = sorted(users["role"].dropna().unique().tolist())
        role_filter = st.multiselect("", options=role_options, default=role_options, label_visibility="collapsed")

        st.markdown("""<div class="filter-card"><div class="filter-title"><i class='fas fa-circle'></i> USER STATUS</div></div>""", unsafe_allow_html=True)
        status_options = sorted(users["status"].dropna().unique().tolist())
        status_filter = st.multiselect("", options=status_options, default=status_options, label_visibility="collapsed")

        st.markdown("---")
        st.caption("<i class='fas fa-chart-simple'></i> CEO Growth & Churn Dashboard · v2.0", unsafe_allow_html=True)

    filtered_users = users[
        (users["created_at"].dt.date >= date_range[0]) &
        (users["created_at"].dt.date <= date_range[1]) &
        (users["role"].isin(role_filter)) &
        (users["status"].isin(status_filter))
    ]

    df = users.copy()
    if not features.empty:
        features["user_id"] = features["user_id"].astype(str)
        df = df.merge(features, left_on="id", right_on="user_id", how="left", suffixes=("", "_feat"))
    if not preds.empty:
        preds["user_id"] = preds["user_id"].astype(str)
        df = df.merge(preds, left_on="id", right_on="user_id", how="left", suffixes=("", "_pred"))
    if not subs.empty:
        subs["user_id"] = subs["user_id"].astype(str)
        df = df.merge(subs, left_on="id", right_on="user_id", how="left", suffixes=("", "_sub"))

    filtered_df = df[df["id"].isin(filtered_users["id"])].copy()

    st.session_state["filtered_df"] = filtered_df
    st.session_state["users"] = users
    st.session_state["activity"] = activity

    return filtered_df, page