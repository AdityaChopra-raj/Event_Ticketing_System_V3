import streamlit as st
from blockchain import Blockchain
from events_data import events as EVENTS_DATA

st.set_page_config(page_title="🛂 Gate Attendant", layout="wide", page_icon="🛂")

st.markdown("""
<style>
body, .main { background-color: #141414; color: white; font-family: 'Helvetica', 'Arial', sans-serif; }
div.stButton > button { display:none; }
.event-row { display:flex; overflow-x:auto; padding:15px 0; }
.event-card { min-width:100px; height:100px; margin-right:20px; border-radius:12px; background-color:#1E1E1E; padding:5px; display:flex; flex-direction:column; align-items:center; justify-content:center; transition: transform 0.2s, box-shadow 0.2s; }
.event-card:hover { transform: scale(1.1); box-shadow:0 0 15px #E50914; cursor:pointer; }
.event-card img { width:80px; height:80px; border-radius:12px; object-fit:cover; }
.event-caption { font-size:0.7rem; color:#ccc; margin-top:5px; text-align:center; }
input, .stTextInput>div>input, .stNumberInput>div>input { background-color:#222; color:white; border-radius:6px; padding:6px; font-size:14px; }
.metric-card { background-color:#1E1E1E; padding:15px 20px; border-radius:10px; text-align:center; margin-bottom:15px; }
.metric-card h3 { margin:0; font-size:1.5rem; }
.metric-card p { margin:0; font-size:0.95rem; color:#ccc; }
</style>
""", unsafe_allow_html=True)

chain = Blockchain()
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

st.title("🛂 Gate Attendant Verification")
st.subheader("Select Event & Verify Guests")

# Event cards
st.markdown('<div class="event-row">', unsafe_allow_html=True)
for ename, ev in EVENTS_DATA.items():
    clicked = st.button(f"{ename}", key=f"btn_gate_{ename}")
    if clicked:
        st.session_state.selected_event = ename

    card_html = f"""
    <div class="event-card" onclick="document.querySelector('#btn_gate_{ename} button').click();">
        <img src="{ev['image']}" alt="{ename}">
        <p class="event-caption">{ename}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

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
