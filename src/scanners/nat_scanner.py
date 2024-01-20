"""NAT Gateway Scanner - Find unused NAT Gateways"""
import boto3

class NATScanner:
    def __init__(self, config):
        self.config = config
        
    def scan(self):
        """Scan for unused NAT Gateways"""
        findings = []
        
        for region in self.config['aws']['regions']:
            ec2 = boto3.client('ec2', region_name=region)
            
            # Get all NAT Gateways
            response = ec2.describe_nat_gateways(
                Filters=[{'Name': 'state', 'Values': ['available']}]
            )
            
            for nat in response['NatGateways']:
                nat_id = nat['NatGatewayId']
                
                # Get tags
                tags = {tag['Key']: tag['Value'] for tag in nat.get('Tags', [])}
                owner = tags.get(self.config['notifications']['owner_tag'], 'unknown')
                
                # In production, check CloudWatch metrics for actual usage
                # For now, flag all as potentially unused
                findings.append({
                    'resource_type': 'nat_gateway',
                    'resource_id': nat_id,
                    'region': region,
                    'size_gb': 0,
                    'age_days': 0,
                    'monthly_cost': self.config['costs']['nat_gateway'],
                    'owner': owner,
                    'tags': tags
                })
        
        return findings
