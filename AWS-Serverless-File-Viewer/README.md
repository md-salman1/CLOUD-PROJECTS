
# AWS Serverless File Viewer

This is a **serverless project** built using **Amazon API Gateway**, **AWS Lambda**, and **Amazon S3**. It allows users to **view the list of files** stored in an S3 bucket named `my-file-uploader-bucket-salman`. The project is designed for scalability, security, and ease of use.

---

## 🔧 Features

- ✅ List files stored in an S3 bucket using a RESTful API.
- 🔒 Built with IAM roles for secure access.
- ☁️ 100% serverless using API Gateway and Lambda.
- 🚀 Scalable and lightweight architecture.
- 📝 Upload feature planned for future updates.

---

## 🧠 Architecture

```
[Client]
   |
   | (GET /files)
   ↓
[API Gateway]
   ↓
[AWS Lambda Function]
   ↓
[S3 Bucket: my-file-uploader-bucket-salman]
   ↓
[Returns: List of Files in JSON]
```

---



## 🛠 Technologies Used

- **Amazon API Gateway** – Create REST API endpoints.
- **AWS Lambda** – Backend logic for listing files.
- **Amazon S3** – Storage of files.
- **IAM Roles** – Secure permissions.

---

## 🚀 How to Use

1. Deploy the Lambda function with list permissions for S3.
2. Connect the Lambda to an API Gateway (GET method).
3. Access the endpoint to get list of files from the bucket.



## 📁 Bucket Name

```
my-file-uploader-bucket-salman
```

---



## 👨‍💻 Author

Mohammed Salman  
Email: mohammedsalman04277@gmail.com  
GitHub: [md-salman1](https://github.com/md-salman1)
