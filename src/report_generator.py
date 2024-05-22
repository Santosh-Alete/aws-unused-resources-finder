"""Report generator for unused resources"""
import csv
from datetime import datetime

class ReportGenerator:
    def __init__(self, config):
        self.config = config
        
    def generate_csv(self, findings):
        """Generate CSV report"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f'unused-resources-{timestamp}.csv'
        
        fieldnames = [
            'resource_type', 'resource_id', 'region', 'size_gb',
            'age_days', 'monthly_cost', 'owner', 'tags'
        ]
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for finding in findings:
                # Convert tags dict to string
                finding_copy = finding.copy()
                finding_copy['tags'] = str(finding['tags'])
                writer.writerow(finding_copy)
        
        return filename
    
    def send_notifications(self, findings):
        """Send email notifications to owners"""
        # Group findings by owner
        by_owner = {}
        for finding in findings:
            owner = finding['owner']
            if owner not in by_owner:
                by_owner[owner] = []
            by_owner[owner].append(finding)
        
        # Send emails (placeholder)
        for owner, owner_findings in by_owner.items():
            total_cost = sum(f['monthly_cost'] for f in owner_findings)
            print(f"Would send email to {owner}: {len(owner_findings)} resources, ${total_cost:.2f}/month")
