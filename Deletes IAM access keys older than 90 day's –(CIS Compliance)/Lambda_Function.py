import boto3
import datetime
from datetime import timezone

# CIS Compliance Configuration (90-day rotation)
MAX_KEY_AGE_DAYS = 90  # Keys older than 90 days will be rotated
DRY_RUN = False        # Set to True for testing (no changes made)
WHITELISTED_USERS = ['admin', 'ci-cd-user']  # Exempt users (e.g., breakglass accounts)

def lambda_handler(event, context):
    iam = boto3.client('iam')
    report = {
        'rotated_keys': [],  # Old keys deleted + new keys created
        'deleted_keys': [],  # Only deletions (no new key created)
        'skipped_keys': [],  # Keys not rotated (recent/whitelisted/inactive)
        'errors': [],
        'config': {
            'max_age_days': MAX_KEY_AGE_DAYS,
            'dry_run': DRY_RUN,
            'whitelisted_users': WHITELISTED_USERS
        }
    }
    
    try:
        users = iam.list_users()
        print(f"Checking {len(users['Users'])} IAM users")
        
        for user in users['Users']:
            username = user['UserName']
            
            if username in WHITELISTED_USERS:
                print(f"Skipping whitelisted user: {username}")
                report['skipped_keys'].append({
                    'user': username,
                    'reason': 'Whitelisted'
                })
                continue
                
            try:
                keys = iam.list_access_keys(UserName=username)
                print(f"Found {len(keys['AccessKeyMetadata'])} keys for {username}")
                
                for key in keys['AccessKeyMetadata']:
                    key_id = key['AccessKeyId']
                    create_date = key['CreateDate']
                    status = key['Status']
                    age_days = (datetime.datetime.now(timezone.utc) - create_date).total_seconds() / 86400  # Convert to days
                    
                    # CIS 1.4: Rotate keys older than MAX_KEY_AGE_DAYS
                    if status == 'Active' and age_days > MAX_KEY_AGE_DAYS:
                        action = "Would rotate" if DRY_RUN else "Rotating"
                        msg = f"{action} {key_id} from {username} (created {age_days:.1f} days ago)"
                        print(msg)
                        
                        if not DRY_RUN:
                            try:
                                # Step 1: Create a new key (ensure no access loss)
                                new_key = iam.create_access_key(UserName=username)
                                new_key_id = new_key['AccessKey']['AccessKeyId']
                                
                                # Step 2: Delete the old key
                                iam.delete_access_key(
                                    UserName=username,
                                    AccessKeyId=key_id
                                )
                                
                                report['rotated_keys'].append({
                                    'user': username,
                                    'old_key_id': key_id,
                                    'new_key_id': new_key_id,
                                    'age_days': round(age_days, 1)
                                })
                                
                                print(f"Created new key: {new_key_id} for {username}")
                                
                            except Exception as e:
                                error_msg = f"Failed to rotate key {key_id}: {str(e)}"
                                report['errors'].append(error_msg)
                                print(error_msg)
                                continue
                    else:
                        report['skipped_keys'].append({
                            'user': username,
                            'key_id': key_id,
                            'reason': 'Recently created' if age_days <= MAX_KEY_AGE_DAYS else 'Inactive',
                            'age_days': round(age_days, 1)
                        })
                        
            except Exception as e:
                error_msg = f"Error processing {username}: {str(e)}"
                report['errors'].append(error_msg)
                print(error_msg)
    
        return {
            'statusCode': 200,
            'body': report
        }
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return {
            'statusCode': 500,
            'body': str(e)
        }