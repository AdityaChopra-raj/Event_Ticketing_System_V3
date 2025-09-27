import streamlit as st
from blockchain import Blockchain
import pandas as pd

st.set_page_config(page_title="🛂 Gate Attendant Portal", layout="centered", page_icon="🛂")

st.markdown("""
<style>
body, .main { background-color: #141414; color: white; font-family: 'Helvetica', 'Arial', sans-serif; }
div.stButton > button { background-color:#1E90FF; color:white; font-weight:bold; border-radius:5px; padding:10px 20px; transition: transform 0.3s, box-shadow 0.3s; }
div.stButton > button:hover { transform: scale(1.05); box-shadow: 0 0 15px #1E90FF; }
input, .stTextInput>div>input { background-color:#222; color:white; border-radius:5px; padding:5px; }
</style>
""", unsafe_allow_html=True)

chain = Blockchain()  # persistent

st.title("🛂 Gate Attendant Verification Portal")
st.subheader("Scan and Verify Tickets Quickly")

tid = st.text_input("Ticket ID")
email_v = st.text_input("Ticket Holder Email")
guests = st.number_input("Guests entering", 1, 10, 1)

if st.button("Verify Entry", type="primary"):
    status = chain.get_ticket_status()
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

# Optional: Show ledger
if st.checkbox("Show Ticket Status Table"):
    st.subheader("Current Ticket Ledger Status")
    tickets = chain.get_ticket_status()
    if tickets:
        df = pd.DataFrame.from_dict(tickets, orient='index')
        st.dataframe(df)
    else:
        st.info("No tickets in the ledger yet.")
