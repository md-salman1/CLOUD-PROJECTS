import json
import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS client
ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    """
    Checks if newly created EC2 instances have the required 'employee id' tag
    with the value 'poiuyt'. If not, terminates the instance.
    """
    logger.info(f"Event received: {json.dumps(event)}")
    
    try:
        # Extract details from CloudTrail event
        if 'detail' not in event:
            logger.warning("Not a CloudTrail event. Exiting.")
            return
        
        # Check if this is an EC2 RunInstances event
        if event['detail']['eventName'] != 'RunInstances':
            logger.info(f"Not an EC2 RunInstances event: {event['detail']['eventName']}. Skipping.")
            return
        
        # Extract instance IDs from the event
        instance_ids = []
        for item in event['detail']['responseElements']['instancesSet']['items']:
            instance_ids.append(item['instanceId'])
        
        if not instance_ids:
            logger.warning("No EC2 instances found in the event.")
            return
        
        logger.info(f"Checking tags for instances: {instance_ids}")
        
        # Check tags on each instance
        for instance_id in instance_ids:
            # Get instance tags
            response = ec2_client.describe_tags(
                Filters=[
                    {
                        'Name': 'resource-id',
                        'Values': [instance_id]
                    }
                ]
            )
            
            # Check if required tag exists
            has_required_tag = False
            for tag in response.get('Tags', []):
                if tag['Key'].lower() == 'employee id' and tag['Value'] == 'poiuyt':
                    has_required_tag = True
                    break
            
            # If required tag doesn't exist, terminate the instance
            if not has_required_tag:
                logger.warning(f"Instance {instance_id} missing required tag 'employee id=poiuyt'. Terminating instance.")
                
                # Terminate the instance
                ec2_client.terminate_instances(
                    InstanceIds=[instance_id]
                )
                
                logger.info(f"Instance {instance_id} terminated successfully.")
            else:
                logger.info(f"Instance {instance_id} has required tag. No action needed.")
        
        return {
            'statusCode': 200,
            'body': json.dumps('EC2 tag compliance check completed successfully')
        }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        raise