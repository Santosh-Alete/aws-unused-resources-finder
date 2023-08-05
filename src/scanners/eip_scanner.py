"""Elastic IP Scanner - Find idle IPs"""
import boto3

class EIPScanner:
    def __init__(self, config):
        self.config = config
        
    def scan(self):
        """Scan for idle Elastic IPs"""
        findings = []
        
        for region in self.config['aws']['regions']:
            ec2 = boto3.client('ec2', region_name=region)
            
            # Get all Elastic IPs
            response = ec2.describe_addresses()
            
            for address in response['Addresses']:
                # Check if not associated with any instance
                if 'AssociationId' not in address:
                    public_ip = address['PublicIp']
                    allocation_id = address.get('AllocationId', 'N/A')
                    
                    # Get tags
                    tags = {tag['Key']: tag['Value'] for tag in address.get('Tags', [])}
                    owner = tags.get(self.config['notifications']['owner_tag'], 'unknown')
                    
                    findings.append({
                        'resource_type': 'elastic_ip',
                        'resource_id': public_ip,
                        'region': region,
                        'size_gb': 0,
                        'age_days': 0,
                        'monthly_cost': self.config['costs']['eip_idle'],
                        'owner': owner,
                        'tags': tags
                    })
        
        return findings
