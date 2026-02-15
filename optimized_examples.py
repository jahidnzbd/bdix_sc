#!/usr/bin/env python3
"""
Example usage of the optimized IPTV Scraper
Demonstrates various ways to use the scraper with concurrent processing
"""

from scraper import IPTVScraper
import json
import time

# Example 1: Quick scrape with default settings (8 workers)
print("=" * 60)
print("Example 1: Quick Scrape (8 concurrent workers)")
print("=" * 60)
start = time.time()
scraper = IPTVScraper()
scraper.scrape_streams(fetch_urls=True, delay=0.1)
scraper.save_json('channels.json')
scraper.save_m3u('playlist.m3u')
elapsed = time.time() - start
print(f"✓ Completed in {elapsed:.1f} seconds\n")

# Example 2: Faster scrape with more workers
print("=" * 60)
print("Example 2: Faster Scrape (16 concurrent workers)")
print("=" * 60)
start = time.time()
scraper2 = IPTVScraper(max_workers=16)
scraper2.scrape_streams(fetch_urls=True, delay=0.05)
scraper2.save_json('channels_fast.json')
scraper2.save_m3u('playlist_fast.m3u')
elapsed = time.time() - start
print(f"✓ Completed in {elapsed:.1f} seconds\n")

# Example 3: Conservative approach (4 workers for slower connections)
print("=" * 60)
print("Example 3: Conservative Scrape (4 workers - slower connection)")
print("=" * 60)
start = time.time()
scraper3 = IPTVScraper(max_workers=4)
scraper3.scrape_streams(fetch_urls=True, delay=0.2)
scraper3.save_json('channels_conservative.json')
elapsed = time.time() - start
print(f"✓ Completed in {elapsed:.1f} seconds\n")

# Example 4: Custom server URL
print("=" * 60)
print("Example 4: Custom Server with Optimization")
print("=" * 60)
scraper4 = IPTVScraper(
    base_url="http://your-iptv-server.com",
    max_workers=8
)
try:
    scraper4.scrape_streams(fetch_urls=True, delay=0.1)
    scraper4.save_json('custom_channels.json')
    print("✓ Custom server scraping completed\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

# Example 5: Metadata only (no URL fetching - very fast)
print("=" * 60)
print("Example 5: Metadata Only (No network requests)")
print("=" * 60)
start = time.time()
scraper5 = IPTVScraper()
scraper5.scrape_streams(fetch_urls=False)  # Just extract metadata
elapsed = time.time() - start
print(f"Found {len(scraper5.channels)} channels in {elapsed:.1f} seconds\n")

# Example 6: Process and filter results
print("=" * 60)
print("Example 6: Process and Filter Results")
print("=" * 60)
scraper6 = IPTVScraper()
scraper6.scrape_streams(fetch_urls=True, delay=0.1)

# Filter working streams only
working_channels = [ch for ch in scraper6.channels if ch['m3u8_url']]
print(f"Total: {len(scraper6.channels)} channels")
print(f"Working: {len(working_channels)} channels")
print(f"Success rate: {len(working_channels)/len(scraper6.channels)*100:.1f}%")

# Save working streams to separate file
with open('working_channels.json', 'w', encoding='utf-8') as f:
    json.dump(working_channels, f, indent=2, ensure_ascii=False)

# Save by category if possible
sports_channels = [ch for ch in scraper6.channels if 'SPORTS' in ch['name'].upper()]
if sports_channels:
    with open('sports_channels.json', 'w', encoding='utf-8') as f:
        json.dump(sports_channels, f, indent=2, ensure_ascii=False)
    print(f"Sports channels: {len(sports_channels)}")

print("\nSample channels:")
for ch in scraper6.channels[:5]:
    status = "✓" if ch['m3u8_url'] else "✗"
    print(f"  [{status}] {ch['number']}: {ch['name']}")

print("\n" + "=" * 60)
print("Performance Summary")
print("=" * 60)
print("Typical execution times:")
print("  • 8 workers:  15-20 seconds (default, balanced)")
print("  • 16 workers: 10-15 seconds (fast, may impact server)")
print("  • 4 workers:  25-30 seconds (conservative, slower connections)")
print("  • Metadata only: <1 second (no network requests)")
print("\nRecommended settings:")
print("  • Good connection: --workers 16 --delay 0.05")
print("  • Normal: --workers 8 --delay 0.1 (default)")
print("  • Slow connection: --workers 4 --delay 0.2")
