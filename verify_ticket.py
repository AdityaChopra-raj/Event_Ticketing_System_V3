import streamlit as st
from blockchain import Blockchain
from events_data import events as EVENTS_DATA
import pandas as pd
import os

st.set_page_config(page_title="🛂 Gate Attendant Portal", layout="centered", page_icon="🛂")

# --- Netflix/Blue theme CSS ---
st.markdown("""
<style>
body, .main { background-color: #141414; color: white; font-family: 'Helvetica', 'Arial', sans-serif; }
div.stButton > button { background-color:#1E90FF; color:white; font-weight:bold; border-radius:5px; padding:10px 20px; transition: transform 0.3s, box-shadow 0.3s; }
div.stButton > button:hover { transform: scale(1.05); box-shadow: 0 0 15px #1E90FF; }
input, .stTextInput>div>input { background-color:#222; color:white; border-radius:5px; padding:5px; }
.event-row { display: flex; overflow-x: auto; padding: 10px 0; }
.event-card { min-width: 200px; margin-right: 20px; border-radius: 5px; transition: transform 0.3s, box-shadow 0.3s; }
.event-card:hover { transform: scale(1.08); box-shadow: 0 0 25px #1E90FF; }
.event-card img { width: 100%; aspect-ratio: 2/3; border-radius:5px; object-fit: cover; }
.event-caption { margin-top: 5px; font-size: 0.9rem; color: #ddd; }
</style>
""", unsafe_allow_html=True)

# --- Initialize blockchain ---
chain = Blockchain()

st.title("🛂 Gate Attendant Verification Portal")
st.subheader("Scan and Verify Tickets Quickly")

# --- Show Mini Dashboard ---
st.markdown("### 🎫 Event Ticket Stats")
status = chain.get_ticket_status()
dashboard_data = []

for ename, edata in EVENTS_DATA.items():
    sold = sum(s.get('purchased',0) for s in status.values() if s.get('event')==ename)
    checked_in = sum(s.get('checked_in',0) for s in status.values() if s.get('event')==ename)
    remaining = edata['capacity'] - sold
    dashboard_data.append({
        "Event": ename,
        "Capacity": edata['capacity'],
        "Tickets Sold": sold,
        "Guests Checked In": checked_in,
        "Remaining Capacity": remaining
    })
st.dataframe(pd.DataFrame(dashboard_data))

# --- Show Event Images ---
st.markdown("### 📸 Event Images")
st.markdown('<div class="event-row">', unsafe_allow_html=True)
for ename in EVENTS_DATA:
    image_path = os.path.join("images", f"{ename}.jpg")
    st.markdown(f"""
    <div class="event-card">
        <img src="{image_path if os.path.exists(image_path) else ''}" alt="{ename}">
        <h4 style="margin:5px 0 2px 0;">{ename}</h4>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Verification Form ---
st.markdown("---")
st.subheader("Verify Ticket Entry")
tid = st.text_input("Ticket ID")
email_v = st.text_input("Ticket Holder Email")
guests = st.number_input("Number of Guests Entering", 1, 10, 1)

if st.button("Verify Entry", type="primary"):
    if not tid:
        st.error("Please enter a Ticket ID")
    elif tid not in status:
        st.error("❌ Ticket ID not found")
    elif status[tid].get('email') != email_v:
        st.error("❌ Email does not match")
    elif status[tid].get('checked_in',0) + guests > status[tid].get('purchased',0):
        st.error("❌ Not enough unused entries for this ticket")
    else:
        with st.spinner("Mining verification block..."):
            chain.add_transaction("VERIFY", status[tid]['event'], tid, email_v, guests)
            proof = chain.proof_of_work(chain.last_block['proof'])
            chain.create_block(proof, chain.hash(chain.last_block))
        st.success(f"✅ Guests verified! Block #{chain.last_block['index']}")
