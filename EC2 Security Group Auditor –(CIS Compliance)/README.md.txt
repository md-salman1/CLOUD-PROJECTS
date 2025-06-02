
# 🔐 AWS Lambda: EC2 Security Group Audit & Tagging

This project uses an AWS Lambda function to scan all **running EC2 instances** and identify those using **security groups** that allow **unrestricted access** (i.e., `0.0.0.0/0` or `::/0`) to any port. If such a group is found attached to an instance, the instance is tagged with `InsecureSecurityGroup=NeedsReview` to highlight the potential security risk.

---

## 📌 Use Case

Helps ensure compliance with security best practices like [CIS Benchmark: 4.1](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-cis-controls.html), which states:
> "EC2 security groups should not allow unrestricted ingress to remote administration ports."

---

## ✅ What This Lambda Does

1. **Scans** all running EC2 instances.
2. **Checks** their attached Security Groups.
3. **Detects** overly permissive ingress rules like:
   - IPv4: `0.0.0.0/0`
   - IPv6: `::/0`
4. **Tags** the instance with:
   ```
   Key: InsecureSecurityGroup
   Value: NeedsReview
   ```
5. **Skips** already tagged instances.
6. **Returns** a detailed summary in the Lambda execution result.

---

## 🔧 Prerequisites

Ensure the following AWS services and permissions are in place:

### 🔑 IAM Permissions

Attach the following managed policies to the Lambda's execution role:

- `AdministratorAccess` *(for full access, can be limited to EC2)*
- `AmazonEC2FullAccess`
- `AmazonEventBridgeFullAccess`

---

## 🧠 How It Works (Architecture)

```
EventBridge (Trigger)
     │
     ▼
Lambda Function ───► Describes running EC2 instances
     │
     └──► Describes security groups
            └──► Finds '0.0.0.0/0' or '::/0' → Tags instance
```

---

## ⚙️ Step-by-Step Setup Guide

### 1️⃣ Prepare the Lambda Function

1. Go to **AWS Lambda** > Create a new function:
   - Name: `EC2-Insecure-SG-Tagger`
   - Runtime: `Python 3.12`
   - Permissions: Use existing role (with required policies above)

2. Replace the default code with `lambda_function.py` code from this repo.

---

### 2️⃣ Add EventBridge Trigger

1. Go to **EventBridge** > Rules > Create rule
2. Name: `Trigger-InsecureSGAudit`
3. Define pattern:
    ```json
    {
      "source": ["aws.ec2"]
    }
    ```
4. Set Lambda as the target and choose your function.

---

### 3️⃣ Test the Lambda

1. Start a few EC2 instances.
2. Attach security groups with inbound rules from `0.0.0.0/0`.
3. Invoke the Lambda manually or wait for the EventBridge trigger.

---

## 📦 lambda_function.py Overview

```python
# This script:
# - Fetches all running EC2 instances
# - Describes each attached security group
# - Detects 0.0.0.0/0 or ::/0 ingress rules
# - Tags such EC2 instances with InsecureSecurityGroup=NeedsReview
```

> Sample response:
```json
{
  "statusCode": 200,
  "body": {
    "tagged_instances": [
      {
        "instance_id": "i-xxxxxxxxxxxxxxxxx",
        "insecure_security_groups": ["sg-xxxxxxxx"]
      }
    ],
    "already_tagged": ["i-yyyyyyyyyyyyyyyyy"],
    "errors": [],
    "message": "✅ 1 instances tagged | 🔁 1 skipped | ⚠️ 0 errors"
  }
}
```

---

## 📁 Files in this Repo

- `lambda_function.py`: Main Lambda code
- `README.md`: You’re here

---

## 💡 Tips

- Integrate with AWS Security Hub or SNS for alerting.
- Extend the logic to restrict tagging based on specific ports like 22/3389 only.

---

## 🧼 Cleanup

- Delete the EventBridge rule if no longer needed.
- Remove the Lambda function to stop tagging.

---

## 🧠 Author Notes

Feel free to modify the logic to apply stricter checks like:
- Only ports 22 (SSH), 3389 (RDP)
- Tag the **security group** instead of instance
