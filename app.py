import os
import json
from datetime import datetime
import streamlit as st
from PIL import Image
from google import genai

st.set_page_config(page_title="ZUDIO AI | Store Ops Engine", page_icon="◼️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0d0d0d; color: #f5f5f5; }
    .alert-box {
        background-color: #241111; border-left: 4px solid #ff3b3b;
        padding: 14px; border-radius: 4px; margin-bottom: 10px; font-family: monospace;
    }
    .ok-box {
        background-color: #112416; border-left: 4px solid #22c55e;
        padding: 14px; border-radius: 4px; margin-bottom: 10px; font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

if "racks" not in st.session_state:
    st.session_state.racks = {
        "RACK A1 — Men's ₹499 Graphic Tees": {"fill": 78, "backroom": 42, "bin": "B-04"},
        "RACK B2 — Women's ₹299 Tops": {"fill": 64, "backroom": 60, "bin": "B-11"},
        "RACK C3 — Men's ₹799 Cargo Denim": {"fill": 52, "backroom": 19, "bin": "B-02"},
        "RACK D4 — Footwear ₹599 Sneakers": {"fill": 81, "backroom": 35, "bin": "B-19"},
    }
if "queue_mins" not in st.session_state:
    st.session_state.queue_mins = 4
if "alerts" not in st.session_state:
    st.session_state.alerts = []

def dispatch_ai_alert(zone: str, issue: str, action: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.alerts.insert(0, f"[{timestamp}] 🚨 {zone} | {issue} → DISPATCHED: {action}")

col_title, col_store = st.columns([2, 1])
with col_title:
    st.markdown("## ◼️ ZUDIO AI — Store Floor & Queue Intelligence")
    st.caption("Powered by Hominis AI | Zero-Hardware Layer over Existing CCTV & POS")
with col_store:
    store = st.selectbox("Active Pilot Store", [
        "MH-PUN-09 | Wakad High Street, Pune",
        "MH-PUN-04 | Phoenix Marketcity, Pune",
        "MH-MUM-02 | Linking Road, Mumbai"
    ])

st.divider()

k1, k2, k3, k4 = st.columns(4)
avg_fill = int(sum(r["fill"] for r in st.session_state.racks.values()) / len(st.session_state.racks))
k1.metric("Floor Rack Availability", f"{avg_fill}%", "-6% vs 2PM" if avg_fill < 50 else "Optimal")
k2.metric("Avg Billing Queue Wait", f"{st.session_state.queue_mins} mins", "⚠️ Spike" if st.session_state.queue_mins >= 9 else "Normal", delta_color="inverse")
k3.metric("Active Staff Dispatches", str(len(st.session_state.alerts)), "Auto-routed to Handhelds")
k4.metric("Est. Weekend Revenue Saved", "₹1,42,500", "+9.4% conversion")

tab1, tab2, tab3 = st.tabs(["⚡ 1-Click Weekend Rush Simulator", "📷 Live CCTV Vision Analyzer (Real AI)", "🧠 Store Manager AI Copilot"])

with tab1:
    st.subheader("Simulate Saturday 7:00 PM Peak Footfall")
    b1, b2, b3 = st.columns(3)
    if b1.button("🔥 Trigger Denim Rack Surge", use_container_width=True):
        st.session_state.racks["RACK C3 — Men's ₹799 Cargo Denim"]["fill"] = 18
        dispatch_ai_alert(
            "RACK C3 (Men's ₹799 Cargo)",
            "Stock dropped to 18% (Sizes M & L empty)",
            "Runner #3 (Rahul): Pull 15 units from Backroom Bin B-02 within 5 mins."
        )
        st.rerun()

    if b2.button("👥 Trigger Billing Queue Spike", use_container_width=True):
        st.session_state.queue_mins = 12
        dispatch_ai_alert(
            "BILLING ZONE (Counters 1–6)",
            "26 shoppers in queue (~12 min wait)",
            "Floor Lead (Priya): Open Counter #7 & deploy mobile mPOS express lane."
        )
        st.rerun()

    if b3.button("🔄 Reset Store Floor", use_container_width=True):
        st.session_state.racks["RACK C3 — Men's ₹799 Cargo Denim"]["fill"] = 68
        st.session_state.queue_mins = 4
        st.session_state.alerts = []
        st.rerun()

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("#### Live Rack Fill Levels (CCTV + POS Sync)")
        for rack_name, info in st.session_state.racks.items():
            status = "🔴 CRITICAL (<30%)" if info["fill"] < 30 else "🟢 HEALTHY"
            st.markdown(f"**{rack_name}** — `{info['fill']}%` {status} *(Backroom Bin {info['bin']}: {info['backroom']} pcs)*")
            st.progress(info["fill"] / 100)

    with right:
        st.markdown("#### Live Staff Handheld Dispatch Feed")
        if not st.session_state.alerts:
            st.markdown('<div class="ok-box">✅ All racks >30% stocked & billing queues under 8 mins.</div>', unsafe_allow_html=True)
        for alert in st.session_state.alerts:
            st.markdown(f'<div class="alert-box">{alert}</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("Test Real CCTV Frame Analysis")
    st.write("Upload any photo of a clothing rack, retail shelf, or checkout queue (or snap via webcam) to watch Zudio AI inspect it live.")
    img_file = st.file_uploader("Upload Store Frame (JPG/PNG)", type=["jpg", "jpeg", "png"])
    cam_file = st.camera_input("Or capture live camera frame")
    active_img = img_file or cam_file

    if active_img:
        image = Image.open(active_img)
        c_img, c_res = st.columns(2)
        c_img.image(image, caption="CCTV Input Feed", use_container_width=True)
        with c_res:
            if not client:
                st.error("Add GEMINI_API_KEY in Streamlit Secrets to run live vision analysis.")
            elif st.button("🔍 Run Zudio AI Vision Scan", type="primary"):
                with st.spinner("Analyzing shelf density & queue congestion..."):
                    prompt = """You are Zudio AI, an enterprise retail operations computer-vision system built by Hominis AI.
Analyze this retail store image and return a crisp operational report with:
1. Zone Type (Apparel Rack / Checkout Queue / Aisle)
2. Estimated Rack Fill % or Queue Headcount & Wait Time
3. Risk Status (CRITICAL if fill < 30% or wait > 8 mins, else NORMAL)
4. Exact 1-line handheld dispatch instruction for floor staff."""
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=
                    )
                    st.markdown("### AI Vision Output")
                    st.write(response.text)
                    dispatch_ai_alert("LIVE CCTV FEED", "Vision scan completed", "Task pushed to Store Manager handheld.")

with tab3:
    st.subheader("Ask Zudio AI Ops Copilot")
    user_q = st.text_input("Ask about store throughput, shift allocation, or stockouts:",
                           placeholder="e.g., How should we reallocate 8 floor staff for Saturday 6-9 PM peak?")
    if st.button("Ask Copilot") and user_q:
        if not client:
            st.error("Add GEMINI_API_KEY in Streamlit Secrets first.")
        else:
            context = f"Store: {store}. Current Racks: {json.dumps(st.session_state.racks)}. Queue wait: {st.session_state.queue_mins} mins."
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are Zudio AI by Hominis AI, advising Zudio's Head of Retail Ops. Keep answers tactical, concise, and ROI-focused.\nContext: {context}\nQuestion: {user_q}"
            )
            st.write(res.text)
