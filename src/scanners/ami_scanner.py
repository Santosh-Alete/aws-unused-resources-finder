"""AMI Scanner - Find old unused AMIs"""
import boto3
from datetime import datetime, timedelta

class AMIScanner:
    def __init__(self, config):
        self.config = config
        
    def scan(self):
        """Scan for old unused AMIs"""
        findings = []
        unused_days = self.config['scanning']['ami_unused_days']
        
        for region in self.config['aws']['regions']:
            ec2 = boto3.client('ec2', region_name=region)
            
            # Get all AMIs owned by this account
            response = ec2.describe_images(Owners=['self'])
            
            # Get all running instances
            instances_response = ec2.describe_instances()
            used_amis = set()
            for reservation in instances_response['Reservations']:
                for instance in reservation['Instances']:
                    used_amis.add(instance['ImageId'])
            
            for image in response['Images']:
                image_id = image['ImageId']
                
                # Check if AMI is not used by any instance
                if image_id not in used_amis:
                    creation_date = datetime.strptime(image['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    age_days = (datetime.utcnow() - creation_date).days
                    
                    if age_days > unused_days:
                        # Calculate storage cost from snapshots
                        snapshot_size = sum(
                            bdm.get('Ebs', {}).get('VolumeSize', 0)
                            for bdm in image.get('BlockDeviceMappings', [])
                        )
                        
                        monthly_cost = snapshot_size * self.config['costs']['snapshot_per_gb']
                        
                        # Get tags
                        tags = {tag['Key']: tag['Value'] for tag in image.get('Tags', [])}
                        owner = tags.get(self.config['notifications']['owner_tag'], 'unknown')
                        
                        findings.append({
                            'resource_type': 'ami',
                            'resource_id': image_id,
                            'region': region,
                            'size_gb': snapshot_size,
                            'age_days': age_days,
                            'monthly_cost': round(monthly_cost, 2),
                            'owner': owner,
                            'tags': tags
                        })
        
        return findings
