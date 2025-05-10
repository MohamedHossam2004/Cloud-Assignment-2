import json
import boto3
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event))
    
    for record in event['Records']:
        # Parse message from SQS
        message_body = record['body']
        logger.info(f"Processing message: {message_body}")
        
        try:
            # Parse the SNS message within SQS
            message_json = json.loads(message_body)
            # If the message comes from SNS, it will have a 'Message' field
            if 'Message' in message_json:
                order_data = json.loads(message_json['Message'])
            else:
                order_data = message_json
            
            # Log order details
            logger.info(f"Order data extracted: {json.dumps(order_data)}")
            
            # Store in DynamoDB
            store_order(order_data)
            
            logger.info(f"Successfully processed order {order_data.get('orderId', 'unknown')}")
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # This will make the message visible again if not deleted
            raise e
    
    return {
        'statusCode': 200,
        'body': json.dumps('Order processing completed successfully')
    }

def store_order(order_data):
    try:
        # Ensure order data has all required fields
        if 'orderId' not in order_data:
            raise ValueError("Order data must contain orderId")
        
        # Set timestamp if not present
        if 'timestamp' not in order_data:
            order_data['timestamp'] = datetime.utcnow().isoformat()
        
        # Store in DynamoDB
        table.put_item(Item=order_data)
        logger.info(f"Order {order_data['orderId']} saved to DynamoDB")
        
    except Exception as e:
        logger.error(f"Error storing order in DynamoDB: {str(e)}")
        raise e