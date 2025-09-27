import streamlit as st
from blockchain import Blockchain
from events_data import events as EVENTS_DATA
import os

st.set_page_config(page_title="🛂 Gate Attendant", layout="wide", page_icon="🛂")

st.markdown("""
<style>
body, .main { background-color: #141414; color: white; font-family: 'Helvetica', 'Arial', sans-serif; }
div.stButton > button { background-color:#E50914; color:white; font-weight:bold; border-radius:8px; padding:12px 25px; font-size:16px; transition: transform 0.2s, box-shadow 0.2s; }
div.stButton > button:hover { transform: scale(1.05); box-shadow: 0 0 15px #E50914; }
input, .stTextInput>div>input, .stNumberInput>div>input { background-color:#222; color:white; border-radius:6px; padding:6px; font-size:14px; }
.event-row { display:flex; overflow-x:auto; padding:15px 0; }
.event-card { min-width:220px; margin-right:25px; border-radius:10px; background-color:#1E1E1E; padding:10px; transition: transform 0.2s, box-shadow 0.2s; }
.event-card:hover { transform: scale(1.06); box-shadow:0 0 20px #E50914; cursor:pointer; }
.event-card img { width:100%; aspect-ratio:2/3; border-radius:8px; object-fit:cover; }
.event-caption { font-size:0.85rem; color:#ccc; margin:3px 0; }
.metric-card { background-color:#1E1E1E; padding:15px 20px; border-radius:10px; text-align:center; margin-bottom:15px; }
.metric-card h3 { margin:0; font-size:1.5rem; }
.metric-card p { margin:0; font-size:0.95rem; color:#ccc; }
</style>
""", unsafe_allow_html=True)

# Blockchain
chain = Blockchain()

if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

st.title("🛂 Gate Attendant Verification")
st.subheader("Select Event & Verify Guests")

# Horizontal scrollable cards
st.markdown('<div class="event-row">', unsafe_allow_html=True)
for ename, ev in EVENTS_DATA.items():
    status = chain.get_ticket_status()
    purchased = sum(s.get('purchased',0) for s in status.values() if s.get('event')==ename)
    checked_in = sum(s.get('checked_in',0) for s in status.values() if s.get('event')==ename)
    remaining = purchased - checked_in
    image_path = ev["image"]

    clicked = st.button(f"{ename}", key=f"btn_gate_{ename}")
    if clicked:
        st.session_state.selected_event = ename

    card_html = f"""
    <div class="event-card">
        <img src="{image_path}" alt="{ename}">
        <h4>{ename}</h4>
        <p class="event-caption">{ev['time']}</p>
        <p class="event-caption">{ev['location']}</p>
        <p class="event-caption"><strong>Remaining Entries: {remaining}</strong></p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

choice = st.session_state.selected_event or st.selectbox("Choose Event", list(EVENTS_DATA.keys()))
ev = EVENTS_DATA[choice]

# Verification Form
st.subheader(f"Verify Guests for {choice}")
tid = st.text_input("Ticket ID")
email_v = st.text_input("Ticket Holder Email")
guests = st.number_input("Number of Guests Entering", 1, 10, 1)

if st.button("Verify Entry"):
    status = chain.get_ticket_status()
    if tid not in status:
        st.error("❌ Ticket ID not found")
    elif status[tid].get('email') != email_v:
        st.error("❌ Email does not match")
    elif status[tid].get('checked_in',0) + guests > status[tid].get('purchased',0):
        st.error("❌ Not enough unused entries")
    else:
        with st.spinner("Mining verification block..."):
            chain.add_transaction("VERIFY", status[tid]['event'], tid, email_v, guests)
            proof = chain.proof_of_work(chain.last_block['proof'])
            chain.create_block(proof, chain.hash(chain.last_block))
        st.success(f"✅ Guests verified! Block #{chain.last_block['index']}")

# Event Metrics
st.markdown("---")
st.subheader("Event Metrics")
cols = st.columns(3)
status = chain.get_ticket_status()
sold = sum(s.get('purchased',0) for s in status.values() if s.get('event')==choice)
checked_in = sum(s.get('checked_in',0) for s in status.values() if s.get('event')==choice)
remaining = sold - checked_in

with cols[0]:
    st.markdown(f"<div class='metric-card'><h3>{sold}</h3><p>Tickets Sold</p></div>", unsafe_allow_html=True)
with cols[1]:
    st.markdown(f"<div class='metric-card'><h3>{checked_in}</h3><p>Guests Checked In</p></div>", unsafe_allow_html=True)
with cols[2]:
    st.markdown(f"<div class='metric-card'><h3>{remaining}</h3><p>Remaining Entries</p></div>", unsafe_allow_html=True)
