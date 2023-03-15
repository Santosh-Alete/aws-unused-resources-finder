# AWS Unused Resources Finder

Automated tool to identify and report unused AWS resources that are costing money. Scans for unattached EBS volumes, idle Elastic IPs, orphaned snapshots, unused NAT Gateways, old AMIs, and idle load balancers.

## Overview

This tool helps reduce AWS costs by identifying resources you're paying for but not using. It generates detailed reports with cost estimates and sends notifications to resource owners.

## Features

- **Unattached EBS Volumes**: Find volumes not attached to any instance
- **Idle Elastic IPs**: Detect IPs not associated with running instances
- **Orphaned Snapshots**: Identify snapshots whose source volume is deleted
- **Unused NAT Gateways**: Find NAT Gateways with zero data processed
- **Old AMIs**: Detect AMIs not used by any instance in 90+ days
- **Idle Load Balancers**: Find ALB/NLB with no active targets
- **Cost Calculation**: Estimate monthly savings for each resource
- **CSV Reports**: Generate detailed reports with all findings
- **Email Notifications**: Send alerts to resource owners via tags

## Architecture

```
┌─────────────────────────────────────────┐
│     Main Script (main.py)               │
│  - Orchestrates all scanners            │
│  - Generates reports                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│     Scanners (modular)                  │
│  - ebs_scanner.py                       │
│  - eip_scanner.py                       │
│  - snapshot_scanner.py                  │
│  - nat_scanner.py                       │
│  - ami_scanner.py                       │
│  - elb_scanner.py                       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│     Report Generator                    │
│  - CSV export                           │
│  - Email notifications                  │
│  - S3 upload                            │
└─────────────────────────────────────────┘
```

## Installation

```bash
git clone https://github.com/Santosh-Alete/aws-unused-resources-finder.git
cd aws-unused-resources-finder
pip install -r requirements.txt
```

## Configuration

Edit `config/config.yaml`:

```yaml
aws:
  regions:
    - us-east-1
    - us-west-2
  
scanning:
  # Days to consider AMI as unused
  ami_unused_days: 90
  
  # Days to consider NAT Gateway as unused
  nat_idle_days: 7

costs:
  # Monthly costs (USD)
  ebs_per_gb: 0.10
  eip_idle: 3.60
  snapshot_per_gb: 0.05
  nat_gateway: 32.40
  alb: 16.20
  nlb: 22.50

notifications:
  enabled: true
  from_email: "aws-scanner@company.com"
  owner_tag: "Owner"
```

## Usage

### Run All Scans

```bash
python src/main.py --config config/config.yaml
```

### Run Specific Scanner

```bash
# EBS volumes only
python src/main.py --scanner ebs

# Multiple scanners
python src/main.py --scanner ebs,eip,snapshots
```

### Generate Report Only

```bash
python src/main.py --report-only --output unused-resources.csv
```

## Example Output

```
🔍 AWS Unused Resources Finder
Generated: 2024-04-15 10:30:00

Scanning Regions: us-east-1, us-west-2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Unattached EBS Volumes: 12 found
   Total Size: 2.5 TB
   Monthly Cost: $250.00

💡 Idle Elastic IPs: 5 found
   Monthly Cost: $18.00

📸 Orphaned Snapshots: 23 found
   Total Size: 1.2 TB
   Monthly Cost: $60.00

🌐 Unused NAT Gateways: 2 found
   Monthly Cost: $64.80

🖼️  Old AMIs: 8 found
   Snapshot Storage: 500 GB
   Monthly Cost: $25.00

⚖️  Idle Load Balancers: 3 found
   Monthly Cost: $48.60

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Total Potential Savings: $466.40/month ($5,596.80/year)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Report saved to: unused-resources-2024-04-15.csv
```

## CSV Report Format

```csv
resource_type,resource_id,region,size_gb,age_days,monthly_cost,owner,tags
ebs_volume,vol-abc123,us-east-1,100,45,10.00,platform-team,Environment=prod
elastic_ip,54.123.45.67,us-east-1,N/A,120,3.60,unknown,
snapshot,snap-xyz789,us-west-2,200,180,10.00,data-team,Project=analytics
nat_gateway,nat-0a1b2c3d,us-east-1,N/A,30,32.40,network-team,
ami,ami-def456,us-east-1,50,150,2.50,platform-team,
load_balancer,api-alb,us-east-1,N/A,15,16.20,backend-team,
```

## Scheduling

Run weekly via cron:

```bash
# Every Monday at 8 AM
0 8 * * 1 /usr/bin/python3 /path/to/src/main.py --config /path/to/config.yaml
```

Or deploy as Lambda function (see `lambda_deployment/` directory).

## AWS Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeVolumes",
        "ec2:DescribeAddresses",
        "ec2:DescribeSnapshots",
        "ec2:DescribeNatGateways",
        "ec2:DescribeImages",
        "ec2:DescribeInstances",
        "elasticloadbalancing:DescribeLoadBalancers",
        "elasticloadbalancing:DescribeTargetHealth",
        "cloudwatch:GetMetricStatistics",
        "ses:SendEmail",
        "s3:PutObject"
      ],
      "Resource": "*"
    }
  ]
}
```

## Real-World Impact

At my previous organization:
- Found 150+ unattached EBS volumes ($1,500/month)
- Identified 25 idle Elastic IPs ($90/month)
- Discovered 8 forgotten NAT Gateways ($260/month)
- Total savings: $1,850/month ($22,200/year)
- Automated monthly scanning reduced waste by 85%

## Project Structure

```
.
├── src/
│   ├── main.py                 # Main orchestrator
│   ├── scanners/
│   │   ├── __init__.py
│   │   ├── ebs_scanner.py      # EBS volume scanner
│   │   ├── eip_scanner.py      # Elastic IP scanner
│   │   ├── snapshot_scanner.py # Snapshot scanner
│   │   ├── nat_scanner.py      # NAT Gateway scanner
│   │   ├── ami_scanner.py      # AMI scanner
│   │   └── elb_scanner.py      # Load balancer scanner
│   ├── report_generator.py     # Report generation
│   └── utils.py                # Helper functions
├── config/
│   └── config.yaml             # Configuration
├── requirements.txt
└── README.md
```

## Contributing

Pull requests welcome! Please open an issue first.

## License

MIT License

## Author

Santosh Alete  
Cloud FinOps Engineer  
[LinkedIn](https://www.linkedin.com/in/santosh-r-alete-09260a27b/) | [GitHub](https://github.com/Santosh-Alete)
