#!/usr/bin/env python3
"""
Helper script to generate mock CPD data or reset the diary.

USAGE EXAMPLES:
---------------
1. Reset/Clear everything:
   python scripts/manage_data.py --clear

2. Generate 25 random mock entries:
   python scripts/manage_data.py --mock

3. Generate 50 random mock entries:
   python scripts/manage_data.py --mock --count 50

4. Clear and then generate mock entries in one shot:
   python scripts/manage_data.py --clear --mock
"""

import sys
import os
import random
import argparse
from datetime import datetime, timedelta

# Add the project root to sys.path so we can import models and storage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import storage
from models import Activity, DISCIPLINES, UNIFIED_CATEGORIES

def reset_diary():
    """Clear all entries in activities.json."""
    storage.save_activities([])
    print("✓ CPD Diary reset (all entries deleted).")

def generate_mock_data(count=20):
    """Generate random CPD entries over the last 3.5 years."""
    activities = []
    
    # Mock data templates
    titles = [
        "Advanced Structural Analysis Seminar",
        "Project Management Professional Workshop",
        "Site Visit: New Bridge Construction",
        "Ethics in Engineering Webinar",
        "Software Architecture for Engineers",
        "Introduction to Python for Data Analysis",
        "Renewable Energy Systems Integration",
        "Geotechnical Soil Testing Lab",
        "Safety in Design (SiD) Training",
        "Leadership & Communication Mentoring"
    ]
    
    providers = [
        "Engineers Australia",
        "Professionals Australia",
        "LinkedIn Learning",
        "Udemy",
        "In-house Training",
        "Local Council Engineering Dept"
    ]

    now = datetime.now()
    
    for i in range(count):
        # Pick a random date in the last ~1300 days (approx 3.5 years)
        days_ago = random.randint(0, 1300)
        act_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Pick random logic
        title = random.choice(titles)
        hours = random.choice([0.5, 1.0, 1.5, 2.0, 4.0, 7.5])
        discipline = random.choice(DISCIPLINES)
        category = random.choice(UNIFIED_CATEGORIES)
        provider = random.choice(providers)
        
        act = Activity(
            title=f"{title} #{i+1}",
            date=act_date,
            hours=hours,
            discipline=discipline,
            category=category,
            notes=f"Mock entry generated for testing purposes. Topic: {title}.",
            evidence_path="mock_certificate.pdf",
            provider_name=provider,
            provider_contact=f"contact@{provider.lower().replace(' ', '')}.com",
            ea_status=random.choice(["Pending", "Uploaded"]),
            pa_status=random.choice(["Pending", "Uploaded"])
        )
        activities.append(act)
    
    storage.save_activities(activities)
    print(f"✓ Generated {count} mock entries across the 3-year window.")

def main():
    parser = argparse.ArgumentParser(description="AutoCPD Data Helper")
    parser.add_argument("--clear", action="store_true", help="Delete all entries in the diary")
    parser.add_argument("--mock", action="store_true", help="Generate mock entries for testing")
    parser.add_argument("--count", type=int, default=25, help="Number of mock entries to generate (default: 25)")
    
    args = parser.parse_args()
    
    if args.clear:
        reset_diary()
    
    if args.mock:
        generate_mock_data(args.count)
        
    if not (args.clear or args.mock):
        parser.print_help()

if __name__ == "__main__":
    main()
