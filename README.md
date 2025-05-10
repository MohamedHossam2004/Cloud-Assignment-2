# Event-Driven Order Notification System

This project implements an event-driven architecture for an e-commerce order processing system using various AWS services:

- Amazon SNS for broadcasting notifications
- Amazon SQS for queuing order events
- AWS Lambda to process messages
- Amazon DynamoDB to store order data

## Architecture Overview

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│    SNS   │────▶│    SQS   │────▶│  Lambda  │────▶┌──────────┐
│          │     │  Topic   │     │  Queue   │     │ Function │     │ DynamoDB │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
                                        │
                                        │
                                        ▼
                                  ┌──────────┐
                                  │Dead Letter│
                                  │   Queue   │
                                  └──────────┘
```

The system works as follows:
1. A new order is published to an SNS topic
2. The order message is delivered to a subscribed SQS queue
3. A Lambda function processes messages from the queue
4. The Lambda function stores order data in DynamoDB
5. If message processing fails multiple times, messages go to a Dead Letter Queue (DLQ)

## Manual Setup Instructions

### Step 1: Create DynamoDB Table

1. Sign in to the AWS Management Console and open the DynamoDB console
2. Click "Create table"
3. Enter the following details:
   - Table name: `Orders`
   - Partition key: `orderId` (String)
4. Under "Table settings", select "Customize settings"
5. For capacity mode, select "On-demand"
6. Click "Create table"

### Step 2: Create SNS Topic

1. Open the Amazon SNS console
2. Click "Topics" in the navigation pane, then "Create topic"
3. Select "Standard" type
4. Enter "OrderTopic" for the name
5. Leave other settings as default and click "Create topic"

### Step 3: Create SQS Queues

1. Open the Amazon SQS console
2. Click "Create queue"
3. First, create the Dead Letter Queue:
   - Select "Standard" queue type
   - Enter "OrderDeadLetterQueue" for the name
   - Leave other settings as default
   - Click "Create queue"

4. Now create the main queue:
   - Click "Create queue" again
   - Select "Standard" queue type
   - Enter "OrderQueue" for the name
   - Under "Configuration", set "Visibility timeout" to 30 seconds
   - Expand "Dead-letter queue" section
   - Enable "Dead-letter queue"
   - Select "OrderDeadLetterQueue" from the dropdown
   - Set "Maximum receives" to 3
   - Click "Create queue"

### Step 4: Subscribe SQS to SNS

1. Go back to the SNS console and select the "OrderTopic"
2. Click "Create subscription"
3. For "Protocol", select "Amazon SQS"
4. For "Endpoint", select the ARN of your "OrderQueue"
5. Click "Create subscription"

### Step 5: Create Lambda Function

1. Open the AWS Lambda console
2. Click "Create function"
3. Select "Author from scratch"
4. Enter "OrderProcessor" for the function name
5. For Runtime, select "Python 3.9"
6. Under "Permissions", expand "Change default execution role"
7. Select "Create a new role with basic Lambda permissions"
8. Click "Create function"

9. After the function is created, scroll down to the "Code source" section
10. Copy the Lambda code from `lambda/index.py` in this repository and paste it into the editor
11. Click "Deploy" to save your function

### Step 6: Configure Lambda Permissions

1. In the Lambda function view, select the "Configuration" tab
2. Click on "Permissions" in the left sidebar
3. Click on the role name under "Execution role"
4. In the IAM console that opens, click "Add permissions" > "Create inline policy"
5. Select the "JSON" tab and paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement
": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/Orders"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            "Resource": "*"
        }
    ]
}
```

6. Click "Review policy"
7. Name it "OrderProcessorPolicy" and click "Create policy"

### Step 7: Configure Lambda Trigger

1. Return to the Lambda function console
2. Click on the "Configuration" tab
3. Select "Triggers" from the left sidebar
4. Click "Add trigger"
5. Select "SQS" from the dropdown
6. Select "OrderQueue" for the SQS queue
7. Leave batch size at 10
8. Click "Add"

## Testing the System

To test the system after setup:

1. **Publish a Test Message to SNS**
   - Go to the SNS console
   - Select the OrderTopic
   - Click "Publish message"
   - Enter the following JSON in the Message body:
   
   ```json
   {
     "orderId": "O1234",
     "userId": "U123",
     "itemName": "Laptop",
     "quantity": 1,
     "status": "new",
     "timestamp": "2025-05-03T12:00:00Z"
   }
   ```
   - Click "Publish"

2. **Verify the Flow**
   - Go to CloudWatch Logs:
     - Open the CloudWatch console
     - Click on "Log groups"
     - Find and select the "/aws/lambda/OrderProcessor" log group
     - Check the latest log stream to see processing details
   
   - Check DynamoDB:
     - Open the DynamoDB console
     - Select the "Orders" table
     - Click "Explore table items"
     - You should see the order with ID "O1234"

## Understanding Visibility Timeout and DLQ

### Visibility Timeout

Visibility timeout is a critical SQS feature that prevents multiple consumers from processing the same message simultaneously. When a consumer (our Lambda function) receives a message, SQS makes the message invisible to other consumers for the duration of the visibility timeout.

In our system, we set a 30-second visibility timeout, which means:
- When Lambda receives a message, it has 30 seconds to process it before the message becomes visible again
- If Lambda processes the message successfully, it deletes it from the queue
- If Lambda fails to process the message within 30 seconds, the message becomes visible again for another attempt

This helps ensure that each order is processed only once under normal conditions.

### Dead Letter Queue (DLQ)

The Dead Letter Queue provides a safety net for messages that can't be processed successfully after multiple attempts. Key benefits:

1. **Error Isolation**: Problematic messages don't block the main processing queue
2. **Debugging**: The DLQ preserves failed messages for investigation
3. **Retry Control**: We configured `maxReceiveCount = 3`, meaning a message can fail processing 3 times before moving to the DLQ

In our system, this prevents infinite processing loops for invalid orders while preserving their data for troubleshooting.

## Lambda Function Details

The Lambda function:
1. Parses the incoming SQS message (containing the SNS message)
2. Extracts the order data
3. Logs the order details for monitoring
4. Stores the order in DynamoDB
5. Reports success or raises an exception on failure