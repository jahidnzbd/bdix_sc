#!/usr/bin/env python3
"""
Quick Start Guide - Run this to test the scraper
"""

import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    missing = []
    
    try:
        import bs4
        print("✓ beautifulsoup4 installed")
    except ImportError:
        missing.append('beautifulsoup4')
        print("✗ beautifulsoup4 NOT installed")
    
    try:
        import requests
        print("✓ requests installed")
    except ImportError:
        missing.append('requests')
        print("✗ requests NOT installed")
    
    if missing:
        print(f"\nInstall missing packages with:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    print("\nAll dependencies satisfied!")
    return True


def check_html_file():
    """Check if HTML file exists"""
    html_file = Path('view-source_103.144.89.251.html')
    
    print(f"\nChecking HTML file: {html_file.name}")
    if html_file.exists():
        size = html_file.stat().st_size
        print(f"✓ HTML file found ({size:,} bytes)")
        return True
    else:
        print(f"✗ HTML file not found in current directory")
        print(f"  Make sure {html_file.name} is in: {Path.cwd()}")
        return False


def run_basic_scrape():
    """Run basic scraping"""
    print("\n" + "="*60)
    print("Running Basic Scrape (HTML Parsing Only)")
    print("="*60 + "\n")
    
    try:
        from scraper import IPTVScraper
        
        scraper = IPTVScraper(html_file='view-source_103.144.89.251.html')
        channels = scraper.scrape_streams(fetch_urls=False)
        
        print("\n✓ Scraping completed successfully!")
        print(f"\nSummary:")
        print(f"  Total channels: {len(channels)}")
        print(f"  Output file: channels.json")
        
        # Show some examples
        if channels:
            print(f"\nFirst 5 channels:")
            for i, channel in enumerate(channels[:5], 1):
                print(f"  {i}. [{channel['number']:3d}] {channel['name']}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_next_steps():
    """Show next steps"""
    print("\n" + "="*60)
    print("Next Steps")
    print("="*60 + "\n")
    
    print("1. View extracted channels:")
    print("   cat channels.json\n")
    
    print("2. Run example scripts:")
    print("   python example_usage.py\n")
    
    print("3. Fetch m3u8 URLs from server (OPTIONAL):")
    print("   python scraper.py --fetch --delay 1\n")
    
    print("4. Use from Python code:")
    print("   from scraper import IPTVScraper")
    print("   scraper = IPTVScraper(html_file='...')") 
    print("   channels = scraper.scrape_streams()\n")
    
    print("For more details, see README.md")


def main():
    """Main quick start flow"""
    print("\n" + "="*60)
    print("IPTV M3U8 Scraper - Quick Start Guide")
    print("="*60 + "\n")
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install dependencies first:")
        print("pip install -r requirements.txt")
        return False
    
    # Check HTML file
    if not check_html_file():
        print("\nCannot proceed without HTML file.")
        return False
    
    # Run basic scrape
    if not run_basic_scrape():
        print("\nScraping failed. Check error messages above.")
        return False
    
    # Show next steps
    show_next_steps()
    
    print("\n" + "="*60)
    print("✓ Quick Start Complete!")
    print("="*60 + "\n")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
