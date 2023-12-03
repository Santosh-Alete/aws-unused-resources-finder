#!/usr/bin/env python3
"""
AWS Unused Resources Finder - Main Orchestrator
"""

import argparse
import logging
from datetime import datetime
from scanners.ebs_scanner import EBSScanner
from scanners.eip_scanner import EIPScanner
from scanners.snapshot_scanner import SnapshotScanner
from scanners.nat_scanner import NATScanner
from scanners.ami_scanner import AMIScanner
from scanners.elb_scanner import ELBScanner
from report_generator import ReportGenerator
from utils import load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnusedResourcesFinder:
    def __init__(self, config_file='config/config.yaml'):
        self.config = load_config(config_file)
        self.report_generator = ReportGenerator(self.config)
        
    def run(self, scanners=None):
        """Run all or specific scanners"""
        logger.info("=" * 70)
        logger.info("🔍 AWS Unused Resources Finder")
        logger.info(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        all_findings = []
        total_cost = 0
        
        # Define available scanners
        available_scanners = {
            'ebs': EBSScanner(self.config),
            'eip': EIPScanner(self.config),
            'snapshots': SnapshotScanner(self.config),
            'nat': NATScanner(self.config),
            'ami': AMIScanner(self.config),
            'elb': ELBScanner(self.config)
        }
        
        # Determine which scanners to run
        if scanners:
            scanners_to_run = {k: v for k, v in available_scanners.items() if k in scanners}
        else:
            scanners_to_run = available_scanners
        
        # Run scanners
        for name, scanner in scanners_to_run.items():
            logger.info(f"\n📦 Scanning {name.upper()}...")
            findings = scanner.scan()
            all_findings.extend(findings)
            
            scanner_cost = sum(f['monthly_cost'] for f in findings)
            total_cost += scanner_cost
            
            logger.info(f"   Found: {len(findings)} resources")
            logger.info(f"   Cost: ${scanner_cost:.2f}/month")
        
        # Generate summary
        logger.info("\n" + "=" * 70)
        logger.info(f"💰 Total Potential Savings: ${total_cost:.2f}/month (${total_cost * 12:.2f}/year)")
        logger.info("=" * 70)
        
        # Generate report
        if all_findings:
            report_file = self.report_generator.generate_csv(all_findings)
            logger.info(f"\n📄 Report saved to: {report_file}")
            
            # Send notifications if enabled
            if self.config['notifications']['enabled']:
                self.report_generator.send_notifications(all_findings)
        
        return all_findings

def main():
    parser = argparse.ArgumentParser(description='AWS Unused Resources Finder')
    parser.add_argument('--config', default='config/config.yaml', help='Config file path')
    parser.add_argument('--scanner', help='Specific scanners to run (comma-separated)')
    parser.add_argument('--output', help='Output CSV file path')
    
    args = parser.parse_args()
    
    scanners = args.scanner.split(',') if args.scanner else None
    
    finder = UnusedResourcesFinder(config_file=args.config)
    finder.run(scanners=scanners)

if __name__ == '__main__':
    main()
