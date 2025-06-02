#  EC2 Tag Compliance Enforcer with AWS Lambda & EventBridge

This project enforces tagging policies for EC2 instances. If a newly created EC2 instance **does not have a specific tag `XYZPQR`**, it is **automatically terminated** by an AWS Lambda function. This ensures compliance and avoids misconfigured resources.

--

##  Table of Contents

- [ Objective](#-objective)
- [ Services & Tools Used]
- [ Project Setup Steps]
  - [ Step 1: Created Lambda Function](#-step-1-created-lambda-function)
  - [ Step 2: Created IAM Role and Attached Permissions](#-step-2-created-iam-role-and-attached-permissions)
  - [ Step 3: Created Event Pattern](#-step-3-created-event-pattern)
  - [ Step 4: Created EventBridge Rule (Using AWS Console)](#️-step-4-created-eventbridge-rule-using-aws-console)
  - [ Step 5: Connected Rule to Lambda Function](#-step-5-connected-rule-to-lambda-function)
  - [ Step 6: Tested the Setup](#-step-6-tested-the-setup)
- [ Result]



##  Objective

- Detect EC2 instance creation
- Check if tag `XYZPQR` is present
- If missing, **delete the instance**
- All actions are **fully automated**

--

##  Services & Tools Used

- **AWS Lambda**
- **Amazon EventBridge**
- **AWS EC2**
- **AWS IAM**
- **AWS CloudTrail**
- **Python (boto3)**

--

##  Project Setup Steps

--

###  Step 1: Created Lambda Function

- Go to **AWS Lambda Console** → Click **Create function**
- Name: `TerminateUntaggedEC2Instance`
- Runtime: Python 3.12
- Execution role: Select existing role or create new one (see next step)
- Uploaded Python code (`lambda_function.py`) that:
  - Extracts EC2 instance ID from the triggering event
  - Waits a few seconds (to ensure tags are applied)
  - Describes the instance using `boto3`
  - Terminates the instance if the tag `XYZPQR` is missing

--

###  Step 2: Created IAM Role and Attached Permissions

- Go to **IAM Console** → **Roles** → Click **Create Role**
- Choose **Lambda** as the trusted entity
- Attach the following permissions:
  - `AmazonEC2ReadOnlyAccess` (or custom: `ec2:DescribeInstances`)
  - `AmazonEC2FullAccess` (or custom: `ec2:TerminateInstances`)
  - `AWSLambdaBasicExecutionRole`
- Name the role (e.g., `lambda-ec2-tag-role`)
- Attach this role to your Lambda function

--

###  Step 3: Created Event Pattern

Here’s the event pattern used to detect EC2 instance creation:

```json
{
  "source": ["aws.ec2"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventSource": ["ec2.amazonaws.com"],
    "eventName": ["RunInstances"]
  }
}

--

###  Step 4: Created EventBridge Rule (Using AWS Console)

1. Open the **Amazon EventBridge** console.
2. Go to **Rules** > Click **Create rule**
3. Fill in the rule details:
   - **Name:** `EC2LaunchRule`
   - **Event bus:** `default`
   - **Rule type:** `Rule with an event pattern`
4. In **Event pattern**:
   - Choose **Custom pattern (JSON editor)**
   - Paste the following:

     ```json
     {
  "source": [
    "aws.ec2"
  ]
}
```
     

5. Click **Next**

6. In **Select targets**:
   - **Target type:** AWS service
   - **Select a target:** Lambda function
   - **Function:** `TerminateUntaggedEC2Instance` (your Lambda function)

7. Click **Next**, then **Create rule**

--

###  Step 5: Connected Rule to Lambda Function

- When creating the rule, you selected the Lambda as the target.
- EventBridge automatically added permissions to allow it to invoke the Lambda.
- You can verify this by:
  - Going to **Lambda Console**
  - Selecting your function → **Configuration** → **Permissions**
  - Under **Resource-based policies**, ensure EventBridge is listed

--

###  Step 6: Tested the Setup

1. Open the **EC2 Console** → Launch a new instance
2. **Do NOT** add the tag `XYZPQR` while creating the instance
3. Wait for 10–30 seconds
4. Go to **CloudWatch Logs** → Choose the log group for `TerminateUntaggedEC2Instance`
5. Confirm the Lambda was triggered and terminated the instance:
   - Log message will show instance ID
   - Message like: `"Required tag 'XYZPQR' not found. Terminating instance i-xxxxxxxxxxxx"`

✅ If the instance was successfully terminated, your automation is working!
