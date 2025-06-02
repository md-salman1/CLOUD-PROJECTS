# lambda_function.py

import boto3
import logging
from botocore.exceptions import ClientError
from botocore.config import Config

# Logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
TAG_KEY = "InsecureSecurityGroup"
TAG_VALUE = "NeedsReview"

# Retry-safe EC2 client
ec2 = boto3.client('ec2', config=Config(retries={'max_attempts': 10, 'mode': 'standard'}))

def has_insecure_ingress(sg):
    for permission in sg.get('IpPermissions', []):
        for ip_range in permission.get('IpRanges', []):
            if ip_range.get('CidrIp') == '0.0.0.0/0':
                return True
        for ipv6_range in permission.get('Ipv6Ranges', []):
            if ipv6_range.get('CidrIpv6') == '::/0':
                return True
    return False

def tag_instance(instance_id):
    try:
        ec2.create_tags(
            Resources=[instance_id],
            Tags=[{'Key': TAG_KEY, 'Value': TAG_VALUE}]
        )
        logger.info(f"✅ Tagged instance {instance_id}")
        return True
    except ClientError as e:
        logger.error(f"❌ Failed to tag instance {instance_id}: {str(e)}")
        return False

def lambda_handler(event, context):
    tagged_instances = []
    already_tagged = []
    errors = []

    try:
        paginator = ec2.get_paginator('describe_instances')
        for page in paginator.paginate(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]):
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}

                    if instance_tags.get(TAG_KEY) == TAG_VALUE:
                        logger.info(f"🔁 Instance {instance_id} already tagged. Skipping.")
                        already_tagged.append(instance_id)
                        continue

                    insecure = False
                    insecure_sgs = []

                    for sg in instance.get('SecurityGroups', []):
                        try:
                            sg_details = ec2.describe_security_groups(GroupIds=[sg['GroupId']])['SecurityGroups'][0]
                            if has_insecure_ingress(sg_details):
                                insecure = True
                                insecure_sgs.append(sg['GroupId'])
                        except ClientError as sg_error:
                            logger.error(f"⚠️ Error describing SG {sg['GroupId']}: {str(sg_error)}")
                            errors.append(sg['GroupId'])

                    if insecure:
                        if tag_instance(instance_id):
                            tagged_instances.append({
                                "instance_id": instance_id,
                                "insecure_security_groups": insecure_sgs
                            })

        return {
            'statusCode': 200,
            'body': {
                "tagged_instances": tagged_instances,
                "already_tagged": already_tagged,
                "errors": errors,
                "message": f"✅ {len(tagged_instances)} tagged | 🔁 {len(already_tagged)} skipped | ⚠️ {len(errors)} errors"
            }
        }

    except Exception as e:
        logger.error(f"🚨 Fatal error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Lambda execution failed: {str(e)}"
        }
