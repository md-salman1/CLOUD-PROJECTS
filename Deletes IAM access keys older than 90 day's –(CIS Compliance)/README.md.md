
# 🔐 AWS IAM Access Key Rotator (CIS-Compliant)

This AWS Lambda function enforces **CIS AWS Benchmark 1.4** for IAM access keys, ensuring that no IAM user retains an active access key for more than 90 days. It rotates old keys by creating new ones and deleting outdated ones. This is essential for maintaining secure, auditable AWS environments.

---

## 📌 Features

- ✅ Automatically checks all IAM users daily
- 🔁 Rotates access keys older than **90 days**
- 🧪 Supports dry-run mode for safe testing
- 🛡 Skips whitelisted break-glass users
- 📋 Returns detailed reports: rotated, skipped, errors

---

## 📂 Project Structure

```
|-- lambda_function.py       # Lambda source code
|-- README.md                # Project documentation
```

---

## ⚙️ Lambda Configuration

- **Runtime**: Python 3.x
- **Trigger**: EventBridge (Scheduled: `rate(1 day)`)
- **IAM Role Requirements**:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "iam:ListUsers",
          "iam:ListAccessKeys",
          "iam:DeleteAccessKey",
          "iam:CreateAccessKey"
        ],
        "Resource": "*"
      }
    ]
  }
  ```

---

## 📋 Usage Steps

### 1️⃣ Create the IAM Role

- Go to **IAM > Roles > Create Role**
- Choose **Lambda** as the trusted entity
- Attach the inline policy above (or create a new managed policy)
- Name it something like `LambdaAccessKeyRotatorRole`

### 2️⃣ Create the Lambda Function

- Go to **AWS Lambda > Create Function**
- Runtime: Python 3.x
- Execution Role: Use the IAM role you created

Paste the code from `lambda_function.py`

### 3️⃣ Set Up EventBridge Trigger

- Go to **Amazon EventBridge > Scheduler > Create Rule**
- Choose `rate(1 day)` to evaluate keys daily
- Select your Lambda as the target

### 4️⃣ (Optional) Enable Dry-Run Mode

To test without making changes:
```python
DRY_RUN = True
```

When ready to enforce key rotation:
```python
DRY_RUN = False
```

### 5️⃣ View Results

The Lambda function logs and returns a JSON object like:
```json
{
  "rotated_keys": [...],
  "deleted_keys": [...],
  "skipped_keys": [...],
  "errors": [...]
}
```

Check **CloudWatch Logs** for detailed output.

---

## ✅ Compliance Alignment

This implementation aligns with:
- [CIS AWS Foundations Benchmark v1.4.0](https://docs.cisecurity.org)
  - **Section 1.4**: Ensure access keys are rotated every 90 days or less

---

## 🧠 Best Practices

- Use environment variables for max key age and dry-run toggles
- Monitor logs and alerts via Amazon CloudWatch
- Whitelist admin/service accounts where appropriate
- Rotate keys securely and notify users if needed

---

## 👨‍💻 Author

Built by Salman ([@md-salman1](https://github.com/md-salman1)) | DevSecOps Enthusiast 🚀

---


