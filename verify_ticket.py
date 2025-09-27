import streamlit as st
from blockchain import Blockchain
from events_data import events as EVENTS_DATA
import os

st.set_page_config(page_title="🛂 Gate Attendant", layout="wide", page_icon="🛂")

st.markdown("""
<style>
body, .main { background-color: #141414; color: white; font-family: 'Helvetica', 'Arial', sans-serif; }
div.stButton > button { display:none; }
input, .stTextInput>div>input, .stNumberInput>div>input { background-color:#222; color:white; border-radius:6px; padding:6px; font-size:14px; }
</style>
""", unsafe_allow_html=True)

chain = Blockchain()
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

st.title("🛂 Gate Attendant Verification")
st.subheader("Select Event & Verify Guests")

# Side-by-side cards
cols = st.columns(len(EVENTS_DATA))
for i, (ename, ev) in enumerate(EVENTS_DATA.items()):
    with cols[i]:
        clicked = st.button(f"{ename}", key=f"btn_gate_{ename}")
        if clicked:
            st.session_state.selected_event = ename

        img_path = ev['image']
        if os.path.exists(img_path):
            st.image(img_path, width=80)
        st.caption(ename)

choice = st.session_state.selected_event or st.selectbox("Choose Event", list(EVENTS_DATA.keys()))
ev = EVENTS_DATA[choice]

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
