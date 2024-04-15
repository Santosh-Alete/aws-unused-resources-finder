"""Load Balancer Scanner - Find idle load balancers"""
import boto3

class ELBScanner:
    def __init__(self, config):
        self.config = config
        
    def scan(self):
        """Scan for idle load balancers"""
        findings = []
        
        for region in self.config['aws']['regions']:
            elbv2 = boto3.client('elbv2', region_name=region)
            
            # Get all load balancers
            response = elbv2.describe_load_balancers()
            
            for lb in response['LoadBalancers']:
                lb_arn = lb['LoadBalancerArn']
                lb_name = lb['LoadBalancerName']
                lb_type = lb['Type']  # application or network
                
                # Get target groups
                tg_response = elbv2.describe_target_groups(LoadBalancerArn=lb_arn)
                
                has_healthy_targets = False
                for tg in tg_response['TargetGroups']:
                    health = elbv2.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])
                    if any(t['TargetHealth']['State'] == 'healthy' for t in health['TargetHealthDescriptions']):
                        has_healthy_targets = True
                        break
                
                # If no healthy targets, consider it idle
                if not has_healthy_targets:
                    # Determine cost based on type
                    monthly_cost = self.config['costs']['alb'] if lb_type == 'application' else self.config['costs']['nlb']
                    
                    # Get tags
                    tags_response = elbv2.describe_tags(ResourceArns=[lb_arn])
                    tags = {}
                    if tags_response['TagDescriptions']:
                        tags = {tag['Key']: tag['Value'] for tag in tags_response['TagDescriptions'][0]['Tags']}
                    
                    owner = tags.get(self.config['notifications']['owner_tag'], 'unknown')
                    
                    findings.append({
                        'resource_type': 'load_balancer',
                        'resource_id': lb_name,
                        'region': region,
                        'size_gb': 0,
                        'age_days': 0,
                        'monthly_cost': monthly_cost,
                        'owner': owner,
                        'tags': tags
                    })
        
        return findings
