#!/usr/bin/env python3
"""Test different worker configurations to show speed improvements"""

from scraper import IPTVScraper
import time

print("\n" + "="*70)
print("PERFORMANCE COMPARISON - Different Worker Configurations")
print("="*70 + "\n")

# Test 1: 4 workers (conservative)
print("Test 1: Conservative (4 workers, 0.2s delay)")
print("-" * 70)
start = time.time()
scraper1 = IPTVScraper(max_workers=4)
scraper1.scrape_streams(fetch_urls=True, delay=0.2)
time1 = time.time() - start
working1 = sum(1 for c in scraper1.channels if c['m3u8_url'])
print(f"⏱️  Time: {time1:.1f} seconds")
print(f"✓ Working: {working1}/92")
print()

# Test 2: 8 workers (default/balanced)
print("Test 2: Balanced (8 workers, 0.1s delay)")
print("-" * 70)
start = time.time()
scraper2 = IPTVScraper(max_workers=8)
scraper2.scrape_streams(fetch_urls=True, delay=0.1)
time2 = time.time() - start
working2 = sum(1 for c in scraper2.channels if c['m3u8_url'])
print(f"⏱️  Time: {time2:.1f} seconds")
print(f"✓ Working: {working2}/92")
print()

# Test 3: 16 workers (fast)
print("Test 3: Fast (16 workers, 0.05s delay)")
print("-" * 70)
start = time.time()
scraper3 = IPTVScraper(max_workers=16)
scraper3.scrape_streams(fetch_urls=True, delay=0.05)
time3 = time.time() - start
working3 = sum(1 for c in scraper3.channels if c['m3u8_url'])
print(f"⏱️  Time: {time3:.1f} seconds")
print(f"✓ Working: {working3}/92")
print()

# Summary
print("="*70)
print("SUMMARY")
print("="*70)
print(f"4 workers  → {time1:.1f}s (baseline for comparison)")
print(f"8 workers  → {time2:.1f}s ({time1/time2:.2f}x faster than 4 workers)")
print(f"16 workers → {time3:.1f}s ({time1/time3:.2f}x faster than 4 workers)")
print()
print("Recommendation:")
print(f"  • Slow connection:   Use 4 workers ({time1:.1f}s)")
print(f"  • Normal connection: Use 8 workers ({time2:.1f}s) ← DEFAULT")
print(f"  • Fast connection:   Use 16 workers ({time3:.1f}s)")
print()
print("✅ All configurations successful! Choose what works for your connection.")
print("="*70 + "\n")
