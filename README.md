# 🔒 Encrypted Image Upload App (Streamlit + AWS)

This project is a secure, cloud-native application built using **Streamlit** for the front-end and **Amazon Web Services (AWS)** for backend services. It enables users to upload images, which are encrypted, stored on **Amazon S3**, and associated metadata is recorded in **DynamoDB**. Notifications are sent via **SNS**, and **IAM** is used for secure access control.

---

## 🚀 Features

- 📤 Upload images via a clean Streamlit interface
- 🔐 Images are encrypted using GPG before upload
- ☁️ Encrypted files are stored on **Amazon S3**
- 🗃️ User and image metadata saved to **DynamoDB**
- 🔔 Email/SMS notifications sent using **Amazon SNS**
- 🔐 Role-based access control via **IAM**
- 🌐 Hosted securely using **Amazon EC2**

---

## 🧰 Technologies Used

| Layer             | Service/Tool         |
|------------------|----------------------|
| Front-End        | Streamlit            |
| Hosting          | AWS EC2              |
| Storage          | AWS S3               |
| Notification     | AWS SNS              |
| Database         | AWS DynamoDB         |
| Access Control   | AWS IAM              |
| Encryption       | python-gnupg, GPG    |
| Scripting        | Python 3.x           |

---

## 🗂️ Project Structure

```
project-root/
│
├── app/                         # Streamlit front-end app
│   └── main.py                  # Main application logic
│
├── encryption/
│   ├── encrypt_utils.py         # GPG encryption/decryption helpers
│
├── aws/
│   ├── s3_utils.py              # Upload/download to S3
│   ├── dynamodb_utils.py        # DynamoDB interactions
│   ├── sns_utils.py             # SNS notifications
│   └── iam_setup.md             # IAM setup instructions
│
├── requirements.txt             # Python dependencies
└── README.md                    # Project overview (this file)
```

---

## 🧪 How It Works

1. **User uploads an image** through the Streamlit UI.
2. Image is **encrypted using GPG** on the server side.
3. Encrypted image is uploaded to **Amazon S3**.
4. Metadata (username, file name, timestamp) is saved to **DynamoDB**.
5. A **notification is sent** to the admin or user via **SNS**.
6. **IAM roles/policies** ensure only authorised actions.

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/encrypted-image-upload-app.git
cd encrypted-image-upload-app
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS credentials

Make sure you have an IAM user with appropriate policies:

```bash
aws configure
```

### 4. Run the app locally

```bash
streamlit run app/main.py
```

---

## ☁️ Deployment on AWS

### 1. Launch an EC2 instance (Ubuntu)

- Allow inbound traffic on ports `22` and `8501`.
- Install Python 3, pip, and Streamlit.
- Upload project files or clone repo.

### 2. Setup IAM Roles

- Attach an IAM role to EC2 with permissions for:
  - `AmazonS3FullAccess`
  - `AmazonDynamoDBFullAccess`
  - `AmazonSNSFullAccess`

### 3. Configure S3 and DynamoDB

- Create an S3 bucket (e.g., `encrypted-image-bucket`)
- Create a DynamoDB table (e.g., `ImageMetadata`) with a primary key (e.g., `image_id`)

---

## 📬 Notifications via SNS

- Create an SNS topic (e.g., `image-upload-notify`)
- Subscribe your email or SMS
- The app publishes to this topic after each upload

---

## 🔒 Security Considerations

- Use KMS or GPG for strong encryption before S3 storage
- Ensure IAM policies follow least privilege principle
- Enable logging on S3 and DynamoDB for audit trails
- Use HTTPS and SSL/TLS wherever applicable

---

## 📈 Future Improvements

- Add user login (Cognito or OAuth2)
- Use AWS Lambda for serverless processing
- Implement presigned URLs for secure downloads
- Add expiry and lifecycle rules on S3

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🙋‍♀️ Maintainer

**Sarah Fitzpatrick**  
Product Manager – Safety & Compliance Software  
Contact: sarah@example.com

---
