"""EBS Volume Scanner - Find unattached volumes"""
import boto3
from datetime import datetime, timedelta

class EBSScanner:
    def __init__(self, config):
        self.config = config
        self.ec2_client = boto3.client('ec2')
        
    def scan(self):
        """Scan for unattached EBS volumes"""
        findings = []
        
        for region in self.config['aws']['regions']:
            ec2 = boto3.client('ec2', region_name=region)
            
            # Get all volumes
            response = ec2.describe_volumes(
                Filters=[{'Name': 'status', 'Values': ['available']}]
            )
            
            for volume in response['Volumes']:
                volume_id = volume['VolumeId']
                size_gb = volume['Size']
                create_time = volume['CreateTime']
                age_days = (datetime.now(create_time.tzinfo) - create_time).days
                
                # Calculate cost
                cost_per_gb = self.config['costs']['ebs_per_gb']
                monthly_cost = size_gb * cost_per_gb
                
                # Get tags
                tags = {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])}
                owner = tags.get(self.config['notifications']['owner_tag'], 'unknown')
                
                findings.append({
                    'resource_type': 'ebs_volume',
                    'resource_id': volume_id,
                    'region': region,
                    'size_gb': size_gb,
                    'age_days': age_days,
                    'monthly_cost': round(monthly_cost, 2),
                    'owner': owner,
                    'tags': tags
                })
        
        return findings
