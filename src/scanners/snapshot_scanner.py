"""Snapshot Scanner - Find orphaned snapshots"""
import boto3
from datetime import datetime

class SnapshotScanner:
    def __init__(self, config):
        self.config = config
        
    def scan(self):
        """Scan for orphaned snapshots"""
        findings = []
        
        for region in self.config['aws']['regions']:
            ec2 = boto3.client('ec2', region_name=region)
            
            # Get all snapshots owned by this account
            response = ec2.describe_snapshots(OwnerIds=['self'])
            
            # Get all existing volumes
            volumes_response = ec2.describe_volumes()
            existing_volume_ids = {v['VolumeId'] for v in volumes_response['Volumes']}
            
            for snapshot in response['Snapshots']:
                volume_id = snapshot.get('VolumeId')
                
                # Check if source volume no longer exists
                if volume_id and volume_id not in existing_volume_ids:
                    snapshot_id = snapshot['SnapshotId']
                    size_gb = snapshot['VolumeSize']
                    start_time = snapshot['StartTime']
                    age_days = (datetime.now(start_time.tzinfo) - start_time).days
                    
                    # Calculate cost
                    cost_per_gb = self.config['costs']['snapshot_per_gb']
                    monthly_cost = size_gb * cost_per_gb
                    
                    # Get tags
                    tags = {tag['Key']: tag['Value'] for tag in snapshot.get('Tags', [])}
                    owner = tags.get(self.config['notifications']['owner_tag'], 'unknown')
                    
                    findings.append({
                        'resource_type': 'snapshot',
                        'resource_id': snapshot_id,
                        'region': region,
                        'size_gb': size_gb,
                        'age_days': age_days,
                        'monthly_cost': round(monthly_cost, 2),
                        'owner': owner,
                        'tags': tags
                    })
        
        return findings
