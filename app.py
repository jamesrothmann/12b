import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import io

# Define global variable to hold the PDF file data after form submission
pdf_file = None

# Function to authenticate and create a Google Drive service
def authenticate_and_connect():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["google"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    sheet_service = build('sheets', 'v4', credentials=creds).spreadsheets()
    drive_service = build('drive', 'v3', credentials=creds)
    return sheet_service, drive_service

# Function to update the Google Sheet with the provided data
def update_google_sheet(sheet_service, name_surname, age_group, taxable_income, capital_gains, cash_investment):
    SPREADSHEET_ID = '1otPYh9ik-fMnziWgm5iRVhJnkuIri-QGueLAYJumFDM'
    RANGE_NAME = 'Dashboard!C4:C8'
    values = [
        [name_surname],
        [age_group],
        [taxable_income],
        [capital_gains],
        [cash_investment],
    ]
    body = {'values': values}
    result = sheet_service.values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()
    return result

# Authenticate and create a Google Sheet service and a Google Drive service
sheet_service, drive_service = authenticate_and_connect()

# Streamlit form for user input
with st.form("tax_form"):
    name_surname = st.text_input("Name and Surname")
    age_group = st.selectbox("Select Age Group", options=["Under 65", "65 and older", "75 and older"])
    taxable_income = st.number_input("Taxable Income (before Capital Gains)", value=0.0)
    capital_gains = st.number_input("Capital Gains (if applicable)", value=0.0)
    cash_investment = st.number_input("Cash Investment", value=0.0)
    submitted = st.form_submit_button("Submit")

    if submitted:
        # Update the Google Sheet with the input data
        update_google_sheet(sheet_service, name_surname, age_group, taxable_income, capital_gains, cash_investment)
        
        # Specify the Google Sheet ID and the Export link
        GOOGLE_SHEET_ID = '1otPYh9ik-fMnziWgm5iRVhJnkuIri-QGueLAYJumFDM'
        
        # Request to export the Google Sheet to PDF
        request = drive_service.files().export_media(fileId=GOOGLE_SHEET_ID, mimeType='application/pdf')
        fh = io.BytesIO()
        
        # Download the PDF into memory
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        # Reset file pointer to start
        fh.seek(0)
        
        # Assign the PDF file data to the global variable
        pdf_file = fh.getvalue()

# If the form has been submitted and the PDF file data is set, show the download button
if pdf_file is not None:
    st.download_button(label="Download PDF", data=pdf_file, file_name="dashboard.pdf", mime='application/pdf')
