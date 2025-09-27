import streamlit as st
import uuid
import os
from blockchain import Blockchain
from events_data import events as EVENTS_DATA
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="🎟 Cultural Event Ticketing", layout="wide", page_icon="🎟")

# --- Netflix-inspired CSS ---
st.markdown("""
<style>
body, .main { background-color: #141414; color: white; font-family: 'Helvetica', 'Arial', sans-serif; }
div.stButton > button { background-color:#E50914; color:white; font-weight:bold; border-radius:5px; padding:10px 20px; transition: transform 0.3s, box-shadow 0.3s; }
div.stButton > button:hover { transform: scale(1.05); box-shadow: 0 0 15px #E50914; }
.event-row { display: flex; overflow-x: auto; padding: 10px 0; }
.event-card { min-width: 200px; margin-right: 20px; border-radius: 5px; transition: transform 0.3s, box-shadow 0.3s; }
.event-card:hover { transform: scale(1.08); box-shadow: 0 0 25px #E50914; }
.event-card img { width: 100%; aspect-ratio: 2/3; border-radius:5px; object-fit: cover; }
.event-caption { margin-top: 5px; font-size: 0.9rem; color: #ddd; }
input, .stTextInput>div>input { background-color:#222; color:white; border-radius:5px; padding:5px; }
</style>
""", unsafe_allow_html=True)

# --- Initialize Blockchain ---
chain = Blockchain()

# --- Load Email Credentials from Streamlit Secrets ---
EMAIL_ADDRESS = st.secrets.get("email", {}).get("address", None)
EMAIL_PASSWORD = st.secrets.get("email", {}).get("password", None)

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    st.warning("⚠️ Email credentials not found in Streamlit secrets. Email sending will be disabled.")

# --- Email Function ---
def send_email(receiver_email, ticket_id, block_index, event_name):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        st.info("Email not sent (credentials missing).")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = receiver_email
        msg['Subject'] = f"🎟 Your Ticket for {event_name} Confirmed"

        body = f"""
Hello,

Your ticket has been successfully purchased.

Event: {event_name}
Ticket ID: {ticket_id}
Block #: {block_index}

Please present this ticket at the event entry.

Enjoy the event! 🎉
"""
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        st.warning(f"Email could not be sent: {e}")

# --- Safe Image Loader ---
def safe_image(path):
    if os.path.exists(path):
        st.image(path, use_column_width=True)
    else:
        placeholder = "https://placehold.co/300x450/E50914/FFFFFF?text=No+Image"
        st.image(placeholder, use_column_width=True)

# --- Role Selection ---
role = st.radio("Select Mode:", ["Customer Booking", "Gate Attendant"], horizontal=True)

if role == "Customer Booking":
    st.title("🎉 Cultural Event Ticketing")
    st.subheader("Events")
    st.markdown('<div class="event-row">', unsafe_allow_html=True)
    for ename, edata in EVENTS_DATA.items():
        # Tickets remaining
        status = chain.get_ticket_status()
        purchased = sum(s.get('purchased', 0) for s in status.values() if s.get('event')==ename)
        remaining = edata["capacity"] - purchased

        # Image path
        image_path = os.path.join("images", f"{ename}.jpg")

        card_html = f"""
        <div class="event-card">
            <img src="{image_path if os.path.exists(image_path) else ''}" alt="{ename}">
            <h4 style="margin:5px 0 2px 0;">{ename}</h4>
            <p class="event-caption">{edata['time']} – {edata['location']}</p>
            <p class="event-caption">Remaining: {remaining}/{edata['capacity']}</p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Select an Event to Book / Check-In")
    choice = st.selectbox("Choose an event", list(EVENTS_DATA.keys()))
    ev = EVENTS_DATA[choice]

    image_path = os.path.join("images", f"{choice}.jpg")
    safe_image(image_path)
    st.write(f"**Location:** {ev['location']}")
    st.write(f"**Time:** {ev['time']}")
    st.write(ev["description"])
    st.write(f"Capacity: {ev['capacity']}")
    st.write(f"Tickets Sold: {sum(s.get('purchased',0) for s in chain.get_ticket_status().values() if s.get('event')==choice)}")
    st.write(f"Guests Checked In: {sum(s.get('checked_in',0) for s in chain.get_ticket_status().values() if s.get('event')==choice)}")

    tab1, tab2 = st.tabs(["Buy Tickets", "Check-In (Attendant)"])

    # --- Buy Tickets ---
    with tab1:
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        num = st.number_input("Number of tickets", 1, 10, 1)
        if st.button("Purchase"):
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

    # --- Check-In ---
    with tab2:
        tid = st.text_input("Ticket ID", key="checkin_id")
        email_v = st.text_input("Ticket Holder Email", key="checkin_email")
        guests = st.number_input("Guests entering", 1, 10, 1, key="checkin_guests")
        if st.button("Verify Entry"):
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

# --- Gate Attendant ---
else:
    st.title("🛂 Gate Attendant Verification")
    tid = st.text_input("Ticket ID", key="gate_tid")
    email_v = st.text_input("Ticket Holder Email", key="gate_email")
    guests = st.number_input("Guests entering", 1, 10, 1, key="gate_guests")
    if st.button("Verify Entry", type="primary"):
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
