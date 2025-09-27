import streamlit as st
from blockchain import Blockchain
from events_data import events as EVENTS_DATA
import os
import math

st.set_page_config(page_title="🛂 Gate Attendant", layout="wide", page_icon="🛂")

st.markdown("""
<style>
body, .main { background-color: #141414; color: white; font-family: 'Helvetica', 'Arial', sans-serif; }
input, .stTextInput>div>input, .stNumberInput>div>input {
    background-color:#222; color:white; border-radius:6px; padding:6px; font-size:14px;
}
.event-card {
    background-color:#1E1E1E;
    border-radius:12px;
    padding:10px;
    text-align:center;
    transition: transform 0.2s, box-shadow 0.2s;
    cursor:pointer;
}
.event-card:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px #E50914;
}
.button-checkin {
    background-color:#1E90FF; color:white; border:none; border-radius:8px;
    padding:10px 20px; font-size:16px; font-weight:bold; margin-top:10px; cursor:pointer;
    transition: background 0.2s;
}
.button-checkin:hover { background-color:#3aa0ff; }
</style>
""", unsafe_allow_html=True)

# --------------------------
# Blockchain Init
# --------------------------
chain = Blockchain()

if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

st.title("🛂 Gate Attendant Verification")
st.subheader("Select Event & Verify Guests")

# --------------------------
# Responsive Event Cards
# --------------------------
cards_per_row = 3
total_events = len(EVENTS_DATA)
rows_needed = math.ceil(total_events / cards_per_row)
event_names = list(EVENTS_DATA.keys())

for r in range(rows_needed):
    start_idx = r * cards_per_row
    cols = st.columns(cards_per_row)
    for i, col in enumerate(cols):
        idx = start_idx + i
        if idx >= total_events:
            break
        ename = event_names[idx]
        ev = EVENTS_DATA[ename]
        with col:
            img_path = ev['image']
            if os.path.exists(img_path):
                st.image(img_path, width=100)
            st.markdown(f"""
            <div class="event-card" onclick="document.getElementById('select_{ename}').click();">
                <p>{ename}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select", key=f"select_{ename}"):
                st.session_state.selected_event = ename

# --------------------------
# Selected Event Details
# --------------------------
choice = st.session_state.selected_event or st.selectbox("Choose Event", list(EVENTS_DATA.keys()))
ev = EVENTS_DATA[choice]

st.subheader(f"Verify Guests for {choice}")
tid = st.text_input("Ticket ID")
email_v = st.text_input("Ticket Holder Email")
guests = st.number_input("Number of Guests Entering", 1, 10, 1)

checkin_clicked = st.button("Check-In", key="gate_checkin")
if checkin_clicked:
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

# --------------------------
# Event Metrics Summary
# --------------------------
st.markdown("---")
st.write(f"**Event:** {choice}")
st.write(f"Tickets Sold: {sum(s.get('purchased',0) for s in chain.get_ticket_status().values() if s.get('event')==choice)}")
st.write(f"Guests Checked In: {sum(s.get('checked_in',0) for s in chain.get_ticket_status().values() if s.get('event')==choice)}")
