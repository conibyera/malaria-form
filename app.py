import streamlit as st
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Fields for the form
fields = [
    "Do you have fever?", "Are you vomiting?", "Are you coughing?", "Do you have diarrhoea?", "Do you have headache", "Are you experiencing body pain?", 
    "Do you have abdominal pain?", "Have you lost your appetite?", "Are you feeling body weakness?", "Do you see blood in your urine?", 
    "Do you feel dizziness?", "Do you have epigastric pain?", "Do you have eye pain?", "Do you have fungal infection?", 
    "Do you have generalized rash?", "Do you have joint pain?", "Do you experience numbness?", "Do you feel pain when urinating?", 
    "Do you experience palpitations?", "Do you have vaginal discharge? (if a female)", "Do you have running nose", "Do you have scabies?", 
    "Do you have chest pain?", "Do you have ear pain?", "Do you have back pain?", 
    "Have you been treated for malaria recently (within the last two weeks)?", "Do you have other signs or symptoms not included in the questionnaire?"
]

def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Form Submission", ln=True, align='C')

    for key, value in data.items():
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    pdf_file = "form_submission.pdf"
    pdf.output(pdf_file)
    return pdf_file

def send_email(pdf_file, recipient_email):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "New Form Submission"

    body = "Please find the attached PDF with the form submission."
    message.attach(MIMEText(body, "plain"))

    with open(pdf_file, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(pdf_file)}",
        )
        message.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

def main():
    st.title(" Rapid Malaria Clinical Assessment Submission Form")
    
    with st.form("submission_form"):
        form_data = {}

        # Add Participant ID field with a maximum length of 12 digits
        participant_id = st.text_input(
            "Participant ID (Max 12 digits)",
            max_chars=12,  # Limit input length
        )
        form_data["Participant ID"] = participant_id

        # Create fields with Yes/No options (default to No)
        for field in fields:
            if field == "Others":
                response = st.radio(field, options=["No", "Yes"], index=0, key=field)
                if response == "Yes":
                    form_data[field] = response
                    others_details = st.text_area("Please specify details for 'Others'", key="others_details")
                    form_data["Others Details"] = others_details
                else:
                    form_data[field] = response
            else:
                form_data[field] = st.radio(field, options=["No", "Yes"], index=0, key=field)

        submitted = st.form_submit_button("Submit")

        if submitted:
            # Validate Participant ID: check if it is numeric and up to 12 digits
            if not participant_id:
                st.error("Participant ID is required.")
            elif not participant_id.isdigit():
                st.error("Participant ID must only contain digits.")
            elif len(participant_id) > 12:
                st.error("Participant ID must not exceed 12 digits.")
            else:
                pdf_file = create_pdf(form_data)
                recipient_email = st.text_input("Enter recipient email:", "diagai2024@gmail.com")
                if recipient_email:
                    send_email(pdf_file, recipient_email)
                    os.remove(pdf_file)  # Clean up the temporary PDF file


if __name__ == "__main__":
    main()
