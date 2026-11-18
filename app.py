import streamlit as st
import joblib


# Browser tab settings
st.set_page_config(
    page_title="Email Phishing Detector",
    page_icon="📧",
    layout="centered"
)


# Simple styling and button hover animation
st.markdown("""
<style>
    .block-container {
        max-width: 700px;
        padding-top: 3rem;
    }

    div.stButton > button {
        width: 100%;
        background-color: #1f4e79;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem;
        font-size: 18px;
        font-weight: bold;
        transition: transform 0.2s ease, background-color 0.2s ease;
    }

    div.stButton > button:hover {
        background-color: #163a5c;
        transform: scale(1.03);
    }
</style>
""", unsafe_allow_html=True)


# Load the saved model once
@st.cache_resource
def load_saved_model():
    saved_items = joblib.load("models/phishing_model.pkl")
    return saved_items["model"], saved_items["vectorizer"]


model, vectorizer = load_saved_model()


# Start on the input screen
if "page" not in st.session_state:
    st.session_state.page = "input"


# INPUT PAGE
if st.session_state.page == "input":

    st.title("Email Phishing Detector")
    st.write("Paste email details below to check whether an email may be phishing.")

    sender = st.text_input("Sender email address")
    subject = st.text_input("Email subject")
    body = st.text_area("Email body", height=200)

    if st.button("Check Phishing"):

        if not subject.strip() and not body.strip():
            st.warning("Please enter an email subject or email body.")

        else:
            # Combine email information
            email_text = f"{sender} {subject} {body}"

            # Convert the email text to numbers
            email_numbers = vectorizer.transform([email_text])

            # Make a prediction
            prediction = model.predict(email_numbers)[0]
            probabilities = model.predict_proba(email_numbers)[0]

            phishing_index = list(model.classes_).index("phishing")
            phishing_risk = probabilities[phishing_index] * 100

            # Save the result, then switch to the results screen
            st.session_state.prediction = prediction
            st.session_state.phishing_risk = phishing_risk
            st.session_state.page = "results"

            st.rerun()


# RESULTS PAGE
elif st.session_state.page == "results":

    st.title("Phishing Check Result")

    prediction = st.session_state.prediction
    phishing_risk = st.session_state.phishing_risk

    if prediction == "phishing":
        st.error("Likely Phishing")
        st.metric("Phishing Risk Score", f"{phishing_risk:.1f}%")
        st.write(
            "Do not click links or share personal information until you verify the sender."
        )
    else:
        st.success("Likely Legitimate")
        st.metric("Phishing Risk Score", f"{phishing_risk:.1f}%")
        st.write(
            "Still review unexpected emails carefully before clicking links or downloading files."
        )

    st.write("")

    if st.button("Check Another Email"):
        st.session_state.page = "input"
        st.rerun()