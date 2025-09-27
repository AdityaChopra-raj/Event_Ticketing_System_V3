import streamlit as st
import uuid
import os
from blockchain import Blockchain
from events_data import events as EVENTS_DATA
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="🎟 Cultural Event Ticketing", layout="wide", page_icon="🎟")

# --------------------------
# CSS: Netflix Dark Theme + Hover Effect + Rounded Buttons
# --------------------------
st.markdown("""
<style>
body, .main { background-color: #141414; color: white; font-family: 'Helvetica', 'Arial', sans-serif; }
input, .stTextInput>div>input, .stNumberInput>div>input { background-color:#222; color:white; border-radius:6px; padding:6px; font-size:14px; }

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

.button-buy {
    background-color:#E50914; color:white; border:none; border-radius:8px;
    padding:10px 20px; font-size:16px; font-weight:bold; margin-top:10px; cursor:pointer;
    transition: background 0.2s;
}
.button-buy:hover { background-color:#ff1a2b; }

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

# --------------------------
# Email Setup
# --------------------------
EMAIL_ADDRESS = st.secrets.get("email", {}).get("address", None)
EMAIL_PASSWORD = st.secrets.get("email", {}).get("password", None)

def send_email(receiver_email, ticket_id, block_index, event_name):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        st.info("Email sending skipped (credentials missing).")
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = receiver_email
        msg['Subject'] = f"🎟 Ticket Confirmation: {event_name}"
        body = f"Hello,\n\nEvent: {event_name}\nTicket ID: {ticket_id}\nBlock #: {block_index}\n\nEnjoy! 🎉"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        st.warning(f"Email could not be sent: {e}")

# --------------------------
# Session state
# --------------------------
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

role = st.radio("Select Mode:", ["Customer Booking", "Gate Attendant"], horizontal=True)

# --------------------------
# Customer Booking
# --------------------------
if role == "Customer Booking":
    st.title("🎉 Cultural Event Ticketing")
    st.subheader("Available Events")

    cols = st.columns(len(EVENTS_DATA))
    for i, (ename, ev) in enumerate(EVENTS_DATA.items()):
        with cols[i]:
            img_path = ev['image']
            if os.path.exists(img_path):
                st.image(img_path, width=100, output_format="auto")
            st.markdown(f"""
            <div class="event-card" onclick="document.getElementById('select_{ename}').click();">
                <p>{ename}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select", key=f"select_{ename}"):
                st.session_state.selected_event = ename

    st.markdown("---")
    st.subheader("Event Details & Actions")

    choice = st.session_state.selected_event or st.selectbox("Choose an event", list(EVENTS_DATA.keys()))
    ev = EVENTS_DATA[choice]

    if os.path.exists(ev['image']):
        st.image(ev['image'], use_column_width=True)
    st.write(f"**Location:** {ev['location']}")
    st.write(f"**Time:** {ev['time']}")
    st.write(ev["description"])
    st.write(f"Capacity: {ev['capacity']}")
    st.write(f"Tickets Sold: {sum(s.get('purchased',0) for s in chain.get_ticket_status().values() if s.get('event')==choice)}")
    st.write(f"Guests Checked In: {sum(s.get('checked_in',0) for s in chain.get_ticket_status().values() if s.get('event')==choice)}")

    tab1, tab2 = st.tabs(["Buy Tickets", "Check-In (Attendant)"])

    # Buy Tickets
    with tab1:
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        num = st.number_input("Number of tickets", 1, 10, 1)
        buy_clicked = st.button("Buy Ticket", key="buy_button")
        if buy_clicked:
            if not name or not email:
                st.error("Name and Email required")
            else:
                sold = sum(s.get('purchased',0) for s in chain.get_ticket_status().values() if s.get('event')==choice)
                if sold + num > ev["capacity"]:
                    st.error("Not enough capacity!")
                else:
                    with st.spinner("Mining block..."):
                        tid = str(uuid.uuid4())[:8]
                        chain.add_transaction("PURCHASE", choice, tid, email, num)
                        proof = chain.proof_of_work(chain.last_block['proof'])
                        chain.create_block(proof, chain.hash(chain.last_block))
                    st.success(f"✅ Ticket purchased! Ticket ID: {tid} | Block #{chain.last_block['index']}")
                    send_email(email, tid, chain.last_block['index'], choice)

    # Check-In
    with tab2:
        tid = st.text_input("Ticket ID", key="checkin_id")
        email_v = st.text_input("Ticket Holder Email", key="checkin_email")
        guests = st.number_input("Guests entering", 1, 10, 1, key="checkin_guests")
        checkin_clicked = st.button("Check-In", key="checkin_button")
        if checkin_clicked:
            status = chain.get_ticket_status()
            if tid not in status:
                st.error("Ticket ID not found")
            elif status[tid].get('email') != email_v:
                st.error("Email does not match")
            elif status[tid].get('checked_in',0) + guests > status[tid].get('purchased',0):
                st.error("Not enough unused entries")
            else:
                with st.spinner("Mining verification block..."):
                    chain.add_transaction("VERIFY", status[tid]['event'], tid, email_v, guests)
                    proof = chain.proof_of_work(chain.last_block['proof'])
                    chain.create_block(proof, chain.hash(chain.last_block))
                st.success(f"✅ Guests verified! Block #{chain.last_block['index']}")

# Gate Attendant
else:
    st.title("🛂 Gate Attendant Verification")
    tid = st.text_input("Ticket ID", key="gate_tid")
    email_v = st.text_input("Ticket Holder Email", key="gate_email")
    guests = st.number_input("Guests entering", 1, 10, 1, key="gate_guests")
    verify_clicked = st.button("Check-In", key="gate_checkin")
    if verify_clicked:
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
