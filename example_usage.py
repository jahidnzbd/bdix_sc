#!/usr/bin/env python3
"""
Example script demonstrating IPTVScraper usage
"""

from scraper import IPTVScraper
import json

def example_1_basic_parsing():
    """Example 1: Basic HTML parsing to extract channel info"""
    print("\n" + "="*60)
    print("Example 1: Basic HTML Parsing")
    print("="*60)
    
    scraper = IPTVScraper(html_file='view-source_103.144.89.251.html')
    channels = scraper.scrape_streams(fetch_urls=False)
    
    print(f"\nExtracted {len(channels)} channels:")
    for i, channel in enumerate(channels[:5], 1):
        print(f"{i}. {channel['name']} (Stream: {channel['number']})")
        print(f"   Logo: {channel['logo']}")
    
    if len(channels) > 5:
        print(f"... and {len(channels) - 5} more channels")
    
    scraper.save_json('channels_sample.json')


def example_2_with_url_fetching():
    """Example 2: Parse HTML and fetch m3u8 URLs"""
    print("\n" + "="*60)
    print("Example 2: HTML Parsing + M3U8 URL Fetching")
    print("="*60)
    print("Note: This will fetch m3u8 URLs from the server")
    print("Set fetch_urls=True to enable this feature\n")
    
    # Uncomment to enable (requires network access)
    # scraper = IPTVScraper(html_file='view-source_103.144.89.251.html')
    # channels = scraper.scrape_streams(fetch_urls=True, delay=0.5)
    # scraper.save_json('channels_with_urls.json')
    # scraper.save_m3u('playlist.m3u')


def example_3_custom_processing():
    """Example 3: Load and process saved JSON"""
    print("\n" + "="*60)
    print("Example 3: Load and Process Saved JSON")
    print("="*60)
    
    try:
        with open('channels_sample.json', 'r', encoding='utf-8') as f:
            channels = json.load(f)
        
        print(f"\nLoaded {len(channels)} channels from JSON")
        
        # Group channels by category
        categories = {}
        for channel in channels:
            name = channel['name']
            # Extract category from name (simple heuristic)
            if 'SPORTS' in name or 'CRICKET' in name or 'GOLF' in name:
                category = 'Sports'
            elif 'CARTOON' in name or 'KIDS' in name or 'NICK' in name or 'POGO' in name:
                category = 'Kids'
            elif 'NEWS' in name:
                category = 'News'
            elif 'MUSIC' in name:
                category = 'Music'
            else:
                category = 'Entertainment'
            
            if category not in categories:
                categories[category] = []
            categories[category].append(channel)
        
        print("\nChannels by Category:")
        for category, channels_list in sorted(categories.items()):
            print(f"\n{category}: {len(channels_list)} channels")
            for channel in channels_list[:3]:
                print(f"  - {channel['name']}")
            if len(channels_list) > 3:
                print(f"  ... and {len(channels_list) - 3} more")
    
    except FileNotFoundError:
        print("channels_sample.json not found. Run example_1_basic_parsing() first.")


def example_4_filter_channels():
    """Example 4: Filter and export specific channels"""
    print("\n" + "="*60)
    print("Example 4: Filter and Export Specific Channels")
    print("="*60)
    
    try:
        with open('channels_sample.json', 'r', encoding='utf-8') as f:
            channels = json.load(f)
        
        # Filter only sports channels
        sports_channels = [c for c in channels if 'SPORTS' in c['name'].upper()]
        
        print(f"\nFound {len(sports_channels)} sports channels:")
        for channel in sports_channels:
            print(f"  - Stream {channel['number']}: {channel['name']}")
        
        # Save filtered channels
        with open('sports_channels.json', 'w', encoding='utf-8') as f:
            json.dump(sports_channels, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved to: sports_channels.json")
    
    except FileNotFoundError:
        print("channels_sample.json not found. Run example_1_basic_parsing() first.")


def example_5_create_m3u_from_json():
    """Example 5: Create M3U playlist from saved JSON"""
    print("\n" + "="*60)
    print("Example 5: Create M3U Playlist from JSON")
    print("="*60)
    
    try:
        with open('channels_sample.json', 'r', encoding='utf-8') as f:
            channels = json.load(f)
        
        # Create M3U content
        m3u_content = "#EXTM3U\n"
        
        for channel in channels:
            if channel.get('m3u8_url'):
                m3u_content += f"#EXTINF:-1 tvg-logo=\"{channel['logo']}\", {channel['name']}\n"
                m3u_content += f"{channel['m3u8_url']}\n"
            else:
                # Even without m3u8 URL, we can add the channel with a placeholder
                m3u_content += f"#EXTINF:-1 tvg-logo=\"{channel['logo']}\", {channel['name']}\n"
                m3u_content += f"http://example.com/stream/{channel['number']}\n"
        
        with open('sample_playlist.m3u', 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        
        lines = m3u_content.strip().split('\n')
        print(f"\nCreated M3U playlist with {len(channels)} channels")
        print(f"File size: {len(m3u_content)} bytes")
        print(f"Saved to: sample_playlist.m3u")
        print(f"\nFirst few lines:")
        for line in lines[:6]:
            print(f"  {line}")
    
    except FileNotFoundError:
        print("channels_sample.json not found. Run example_1_basic_parsing() first.")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("IPTV M3U8 Scraper - Usage Examples")
    print("="*60)
    
    example_1_basic_parsing()
    example_3_custom_processing()
    example_4_filter_channels()
    example_5_create_m3u_from_json()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\nGenerated files:")
    print("  - channels_sample.json: Basic channel list")
    print("  - sports_channels.json: Filtered sports channels")
    print("  - sample_playlist.m3u: M3U playlist file")
    print("\nFor more information, see README.md")


if __name__ == '__main__':
    main()
