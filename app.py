import streamlit as st
import boto3
import uuid
import os
import pandas as pd
from decimal import Decimal
from dotenv import load_dotenv
import gnupg

# Load environment variables
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")
GPG_PASSPHRASE = os.getenv("GPG_PASSPHRASE", "defaultsecurepass")

# AWS Clients
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

rekognition_client = boto3.client(
    "rekognition",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

sns_client = boto3.client(
    "sns",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# DynamoDB Tables
user_table = dynamodb.Table('CCminiUsers')
metrics_table = dynamodb.Table('CCminiMetrics')

# GPG setup
gpg = gnupg.GPG()
gpg.encoding = 'utf-8'

# Streamlit UI
st.title("🔒 Secure Login and 🖼 Image Scanner")

# --- LOGIN ---
st.subheader("🔑 Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Login")

session_state = st.session_state

if "logged_in" not in session_state:
    session_state.logged_in = False

if login_button:
    if username and password:
        try:
            response = user_table.get_item(Key={"Username": username})
            user = response.get('Item')
        except Exception as e:
            st.error(f"⚠️ Error accessing user data: {str(e)}")
            st.stop()

        if user and user['Password'] == password:
            st.success("✅ Logged in successfully!")

            # Send login SMS
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=f"Hello {username}, you've logged in!",
                Subject="Login Success"
            )
            session_state.logged_in = True
            session_state.username = username
            session_state.phone = user['PhoneNumber']
        else:
            st.error("❌ Invalid credentials")
    else:
        st.warning("⚠ Please enter username and password.")

# --- AFTER LOGIN ---
if session_state.logged_in:
    st.subheader("📤 Upload and Scan your Image")

    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        unique_id = str(uuid.uuid4())
        temp_filename = f"{unique_id}.jpg"
        encrypted_filename = f"{temp_filename}.gpg"

        # Save uploaded image locally
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.image(temp_filename, caption="Uploaded Image", use_container_width=True)

        # 🔐 Encrypt the file using GPG
        with open(temp_filename, "rb") as f:
            encrypted = gpg.encrypt_file(
                f,
                recipients=None,
                symmetric='AES256',
                passphrase=GPG_PASSPHRASE,
                output=encrypted_filename
            )

        if not encrypted.ok:
            st.error(f"❌ Image encryption failed: {encrypted.stderr}")
            os.remove(temp_filename)
            st.stop()

        # ✅ Upload encrypted file to S3
        s3_client.upload_file(encrypted_filename, S3_BUCKET, encrypted_filename)
        st.success("🔐 Encrypted image uploaded to S3!")

        # ✅ Upload raw image to S3 (for Rekognition)
        s3_client.upload_file(temp_filename, S3_BUCKET, temp_filename)
        st.success("✅ Raw image uploaded to S3 for Rekognition!")

        # Rekognition Label Detection
        try:
            response = rekognition_client.detect_labels(
                Image={"S3Object": {"Bucket": S3_BUCKET, "Name": temp_filename}},
                MaxLabels=10,
                MinConfidence=70
            )
        except Exception as e:
            st.error(f"❌ Rekognition failed: {str(e)}")
            os.remove(temp_filename)
            os.remove(encrypted_filename)
            st.stop()

        labels = {label['Name']: Decimal(str(label['Confidence'])) for label in response['Labels']}

        st.subheader("📝 Detected Labels:")
        for name, confidence in labels.items():
            st.write(f"- {name} ({float(confidence):.2f}%)")

        st.subheader("📊 Confidence Chart")
        st.bar_chart(pd.DataFrame([float(v) for v in labels.values()], index=labels.keys(), columns=["Confidence"]))

        # Save metrics to DynamoDB
        metrics_table.put_item(
            Item={
                "ImageID": temp_filename,
                "Username": session_state.username,
                "LabelsDetected": len(labels),
                "Labels": list(labels.keys()),
                "ConfidenceScores": list(labels.values())
            }
        )
        st.success("💾 Metrics saved to DynamoDB!")

        # Send metrics SNS
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f"Hello {session_state.username}, your image '{temp_filename}' was processed with {len(labels)} labels detected!",
            Subject="Image Scan Completed"
        )
        st.success("📩 Metrics Notification Sent!")

        delete_from_s3 = st.checkbox("Delete uploaded files from S3 after processing?", value=True)
        if delete_from_s3:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=temp_filename)
            s3_client.delete_object(Bucket=S3_BUCKET, Key=encrypted_filename)
            st.info("🗑 Uploaded files deleted from S3.")

        os.remove(temp_filename)
        os.remove(encrypted_filename)
