from datetime import datetime

import streamlit as st

from agent import run_agent

st.set_page_config(page_title="Weather Agent", page_icon="🌦️", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    #MainMenu, footer, header {visibility: hidden;}

    .stApp {
        background: linear-gradient(-45deg, #0f2027, #203a43, #2a5298, #7db9e8);
        background-size: 400% 400%;
        animation: drift 18s ease infinite;
    }

    @keyframes drift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .block-container {
        padding-top: 3rem;
        max-width: 640px;
    }

    .hero-title {
        text-align: center;
        color: #ffffff;
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        text-shadow: 0 2px 12px rgba(0,0,0,0.25);
    }

    .hero-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.85);
        font-size: 1.05rem;
        margin-bottom: 1.6rem;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 999px;
        padding: 0.7rem 1.2rem;
        border: none;
        font-size: 1.05rem;
    }

    /* Main "Get Weather" submit button */
    div[data-testid="stFormSubmitButton"] button {
        border-radius: 999px;
        border: none;
        background: #ffffff;
        color: #1e3c72;
        font-weight: 700;
        padding: 0.6rem 1.2rem;
        width: 100%;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.25);
        color: #1e3c72;
    }

    /* Quick city chip buttons */
    div[data-testid="stButton"] button {
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.5);
        background: rgba(255,255,255,0.08);
        color: #ffffff;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.3rem 0.6rem;
        transition: background 0.15s ease, transform 0.15s ease;
    }

    div[data-testid="stButton"] button:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-1px);
        color: #ffffff;
    }

    .weather-card {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.35);
        backdrop-filter: blur(12px);
        border-radius: 24px;
        padding: 2rem;
        margin-top: 1.5rem;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
    }

    .weather-card-city {
        font-size: 1.3rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-transform: capitalize;
        opacity: 0.9;
    }

    .weather-card-glyph {
        font-size: 3.8rem;
        margin: 0.3rem 0 0.1rem;
    }

    .weather-card-temp {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .weather-card-desc {
        font-size: 1.05rem;
        line-height: 1.5;
        opacity: 0.95;
    }

    .weather-card-time {
        font-size: 0.8rem;
        opacity: 0.65;
        margin-top: 0.8rem;
    }

    .notice-card {
        background: rgba(255, 193, 7, 0.15);
        border: 1px solid rgba(255, 193, 7, 0.45);
        backdrop-filter: blur(12px);
        border-radius: 24px;
        padding: 1.8rem;
        margin-top: 1.5rem;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
    }

    .notice-card-glyph {
        font-size: 2.6rem;
        margin-bottom: 0.4rem;
    }

    .footer-credit {
        text-align: center;
        color: rgba(255,255,255,0.5);
        font-size: 0.8rem;
        margin-top: 2.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="hero-title">🌦️ Weather Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Live weather for cities across India, fetched by an AI agent</div>',
    unsafe_allow_html=True,
)

POPULAR_CITIES = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Kolkata", "Jaipur"]

if "pending_city" not in st.session_state:
    st.session_state.pending_city = None
if "last_city" not in st.session_state:
    st.session_state.last_city = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_steps" not in st.session_state:
    st.session_state.last_steps = []
if "last_error" not in st.session_state:
    st.session_state.last_error = None


def queue_city(city: str):
    st.session_state.pending_city = city


with st.form("search_form", clear_on_submit=False):
    col1, col2 = st.columns([4, 1])
    with col1:
        city_input = st.text_input(
            "City",
            placeholder="Enter a city, e.g. Mumbai, Jaipur, Bengaluru",
            label_visibility="collapsed",
        )
    with col2:
        submitted = st.form_submit_button("Get Weather", use_container_width=True)

chip_cols = st.columns(len(POPULAR_CITIES))
for col, city_name in zip(chip_cols, POPULAR_CITIES):
    with col:
        st.button(city_name, key=f"chip_{city_name}", on_click=queue_city, args=(city_name,))

target_city = None
if submitted and city_input.strip():
    target_city = city_input.strip()
elif st.session_state.pending_city:
    target_city = st.session_state.pending_city
    st.session_state.pending_city = None

if submitted and not city_input.strip():
    st.warning("Please enter a city name.")

if target_city:
    steps = []

    with st.status(f"Checking the skies over {target_city}…", expanded=False) as status:
        def record(step, _steps=steps, _status=status):
            _steps.append(step)
            kind = step.get("step", "")
            if kind == "PLAN":
                _status.write(f"🧭 {step['content']}")
            elif kind == "TOOL":
                _status.write(f"🔧 Looking up weather for **{step.get('input')}**")
            elif kind == "OBSERVE":
                _status.write(f"👀 Got reading: {step['content']}")

        try:
            result = run_agent(f"What is the weather in {target_city}?", on_step=record)
            status.update(label="Done", state="complete")
            st.session_state.last_city = target_city
            st.session_state.last_result = result
            st.session_state.last_steps = steps
            st.session_state.last_error = None
        except Exception as e:
            status.update(label="Something went wrong", state="error")
            st.session_state.last_error = str(e)
            st.session_state.last_result = None
            st.session_state.last_steps = steps

if st.session_state.last_error:
    st.error(f"Couldn't fetch the weather: {st.session_state.last_error}")

if st.session_state.last_result:
    reading = next(
        (s["content"] for s in reversed(st.session_state.last_steps) if s.get("step") == "OBSERVE"),
        None,
    )
    is_bad_reading = reading is None or reading.lower().startswith("error")

    if not is_bad_reading:
        parts = reading.split()
        glyph, temp = parts[0], " ".join(parts[1:])
        st.markdown(
            f"""
            <div class="weather-card">
                <div class="weather-card-city">{st.session_state.last_city}</div>
                <div class="weather-card-glyph">{glyph}</div>
                <div class="weather-card-temp">{temp}</div>
                <div class="weather-card-desc">{st.session_state.last_result}</div>
                <div class="weather-card-time">Last checked at {datetime.now().strftime('%I:%M %p')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="notice-card">
                <div class="notice-card-glyph">⚠️</div>
                <div class="weather-card-desc">{st.session_state.last_result}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("🧠 See the agent's reasoning"):
        for step in st.session_state.last_steps:
            st.json(step)

st.markdown('<div class="footer-credit">Powered by wttr.in &amp; OpenAI</div>', unsafe_allow_html=True)
