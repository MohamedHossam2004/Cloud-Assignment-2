# CloudFormation Deployment Instructions

This README provides step-by-step instructions for deploying the CloudFormation template for Assignment 2.

## Prerequisites

Before deploying the template, ensure you have:

1. An AWS account with appropriate permissions
2. AWS CLI installed and configured (optional, for command-line deployment)
3. An existing EC2 key pair for SSH access

## Deployment Steps via AWS Console

### Step 1: Navigate to CloudFormation

1. Log in to your AWS Management Console
2. Navigate to the CloudFormation service
3. Click on "Create stack" > "With new resources (standard)"

### Step 2: Specify Template

1. Select "Upload a template file"
2. Click "Choose file" and select the `order-notification-template.yaml` file from this directory
3. Click "Next"

### Step 3: Specify Stack Details

1. Enter a Stack name (e.g., "Assignment2Stack")
2. Review and modify the parameters as needed:
   - VPC CIDR block
   - Subnet CIDR blocks
   - EC2 instance type
   - Key pair name (must be an existing key pair in your account)
3. Click "Next"

### Step 4: Configure Stack Options

1. Add any tags if required
2. Configure permissions if necessary
3. Set advanced options if needed
4. Click "Next"

### Step 5: Review and Create

1. Review all the settings
2. Check the acknowledgment for IAM resources if prompted
3. Click "Create stack"

### Step 6: Monitor Stack Creation

1. Wait for the stack creation to complete (it may take 5-10 minutes)
2. Once the status shows "CREATE_COMPLETE", the deployment is successful

## Accessing Resources

After successful deployment, you can find important information in the "Outputs" tab of your CloudFormation stack:

- VPC ID
- Public Subnet IDs
- Private Subnet IDs
- Web Server Public IP
- Web Server Public DNS
- S3 Bucket Name

## Connecting to EC2 Instance

To connect to the EC2 instance via SSH:

```
ssh -i /path/to/your-key.pem ec2-user@<WebServerPublicIP>
```

## Cleaning Up

To avoid incurring charges, delete the stack when you're done:

1. Go to the CloudFormation console
2. Select your stack
3. Click "Delete"
4. Confirm the deletion

## Deployment via AWS CLI (Alternative)

If you prefer using the AWS CLI, run:

```bash
aws cloudformation create-stack \
  --stack-name Assignment2Stack \
  --template-body file://template.yaml \
  --parameters ParameterKey=KeyName,ParameterValue=YourKeyName \
  --capabilities CAPABILITY_IAM
```

Replace `YourKeyName` with the name of your EC2 key pair.
