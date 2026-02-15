#!/usr/bin/env python3
"""
IPTV M3U8 Scraper
Scrapes m3u8 stream links and channel information from the HTML file
Outputs results as JSON with channel number, name, logo, and m3u8 URL

Features:
- Persistent channel numbering (numbers don't change for existing channels)
- New channels automatically get the next available number
- Concurrent m3u8 URL fetching for speed
- GitHub Actions ready
"""

import json
import re
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

class IPTVScraper:
    def __init__(self, base_url="http://103.144.89.251", html_file=None, max_workers=8, mapping_file='channel_mapping.json'):
        """
        Initialize the scraper
        
        Args:
            base_url: Base URL for the streaming server
            html_file: Path to the HTML file to parse (if None, will fetch from URL)
            max_workers: Number of concurrent threads for fetching m3u8 URLs
            mapping_file: File to store persistent channel-to-number mappings
        """
        self.base_url = base_url.rstrip('/')
        self.html_file = html_file
        self.channels = []
        self.max_workers = max_workers
        self.mapping_file = mapping_file
        self.channel_mapping = {}  # Maps channel name to assigned number
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.lock = Lock()  # Thread-safe lock for updating progress
        
        # Load existing channel mappings
        self._load_channel_mapping()
    
    def _load_channel_mapping(self):
        """Load existing channel name to number mappings from file"""
        if Path(self.mapping_file).exists():
            try:
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    self.channel_mapping = json.load(f)
                print(f"Loaded {len(self.channel_mapping)} existing channel mappings")
            except Exception as e:
                print(f"Warning: Could not load channel mapping: {e}")
                self.channel_mapping = {}
        else:
            print("No existing channel mappings found, starting fresh")
            self.channel_mapping = {}
    
    def _save_channel_mapping(self):
        """Save channel mappings to file for persistence"""
        try:
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.channel_mapping, f, indent=2, ensure_ascii=False)
            print(f"✓ Channel mapping saved ({len(self.channel_mapping)} channels)")
        except Exception as e:
            print(f"Warning: Could not save channel mapping: {e}")
    
    def _assign_channel_number(self, channel_name):
        """
        Assign or get channel number based on persistent mapping
        
        Args:
            channel_name: Channel name
            
        Returns:
            Channel number (existing or newly assigned)
        """
        # If channel already has a number, return it
        if channel_name in self.channel_mapping:
            return self.channel_mapping[channel_name]
        
        # Assign new number (next available)
        if self.channel_mapping:
            next_number = max(int(v) for v in self.channel_mapping.values()) + 1
        else:
            next_number = 1
        
        self.channel_mapping[channel_name] = str(next_number)
        return next_number
    
    def _extract_html_from_view_source(self, html_content):
        """Extract raw HTML from browser view-source formatted page"""
        # Check if this is a view-source page (has line-number class and table structure)
        if 'line-number' in html_content and '<table>' in html_content:
            print("Detected view-source HTML format, extracting raw content...")
            
            try:
                # Extract content from line-content cells
                pattern = r'<td class="line-content">(.*?)</td>'
                matches = re.findall(pattern, html_content, re.DOTALL)
                
                if matches:
                    # Join all line content
                    raw_content = '\n'.join(matches)
                    # Decode HTML entities
                    raw_content = raw_content.replace('&lt;', '<')
                    raw_content = raw_content.replace('&gt;', '>')
                    raw_content = raw_content.replace('&quot;', '"')
                    raw_content = raw_content.replace('&#x27;', "'")
                    raw_content = raw_content.replace('&amp;', '&')
                    # Remove span tags from syntax highlighting (but NOT content)
                    raw_content = re.sub(r'<span[^>]*>', '', raw_content)
                    raw_content = re.sub(r'</span>', '', raw_content)
                    # Remove ONLY the view-source formatting <a> tags (not actual <a> tags)
                    raw_content = re.sub(r'<a class="html-attribute-value html-resource-link"[^>]*>', '', raw_content)
                    raw_content = re.sub(r'</a>', '', raw_content)  # Remove closing tags from those links
                    # Remove <br> tags used in view-source
                    raw_content = re.sub(r'<br>\n?', '\n', raw_content)
                    
                    # Debug: save extracted HTML
                    with open('extracted_raw.html', 'w', encoding='utf-8') as f:
                        f.write(raw_content)
                    print(f"Extracted HTML saved to extracted_raw.html ({len(raw_content)} bytes)")
                    
                    return raw_content
            except Exception as e:
                print(f"Warning: Could not parse view-source format: {e}")
        
        return html_content

    def parse_html(self):
        """Parse HTML to extract channel information"""
        print("Parsing HTML from server...")
        
        # Try to fetch from URL first, fallback to local file if specified
        if self.html_file and Path(self.html_file).exists():
            print(f"Loading from local file: {self.html_file}")
            with open(self.html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            print(f"Fetching from {self.base_url}...")
            try:
                response = self.session.get(self.base_url, timeout=10)
                response.raise_for_status()
                html_content = response.text
            except Exception as e:
                print(f"Error fetching HTML: {e}")
                raise
        
        # Extract HTML if this is a view-source page
        html_content = self._extract_html_from_view_source(html_content)
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all channel list items
        channels_list = soup.find_all('li', class_=lambda x: x and 'All' in x)
        
        print(f"Found {len(channels_list)} channels")
        
        # Debug: print a sample if found
        if len(channels_list) == 0:
            print("DEBUG: No channels found with 'All' class. Checking actual classes...")
            all_li = soup.find_all('li')
            if all_li:
                print(f"Total <li> elements: {len(all_li)}")
                # Print first 5 li elements and their classes
                for i, li in enumerate(all_li[:5]):
                    print(f"  {i+1}. Classes: {li.get('class')}")
        
        for idx, channel_item in enumerate(channels_list, 1):
            try:
                # Extract channel link info
                link = channel_item.find('a', class_='channel')
                if not link:
                    continue
                
                # Extract onclick attribute to get stream number
                onclick = link.get('onclick', '')
                stream_match = re.search(r'stream=(\d+)', onclick)
                if not stream_match:
                    continue
                
                stream_number = stream_match.group(1)
                
                # Extract image info (channel name and logo)
                img = channel_item.find('img')
                if not img:
                    continue
                
                channel_name = img.get('alt', f'Channel {stream_number}')
                logo_src = img.get('src', '')
                
                # Convert relative paths to absolute URLs
                logo_url = urljoin(self.base_url, logo_src)
                
                # IMPORTANT: Use persistent channel number based on channel name
                # This ensures the number never changes even if scraper is re-run
                channel_number = self._assign_channel_number(channel_name)
                
                channel_info = {
                    'number': channel_number,
                    'name': channel_name,
                    'stream_id': stream_number,  # Keep track of original stream number
                    'logo': logo_url,
                    'm3u8_url': None  # Will be filled by fetch_m3u8_url
                }
                
                self.channels.append(channel_info)
                print(f"{idx}. Stream {stream_number} → Channel #{channel_number}: {channel_name}")
                
            except Exception as e:
                print(f"Error parsing channel item {idx}: {e}")
                continue
        
        # Sort by channel number
        self.channels.sort(key=lambda x: x['number'])
        
        # Save the updated mappings for persistence
        self._save_channel_mapping()
        
        print(f"Successfully extracted {len(self.channels)} channels\n")
    
    def fetch_m3u8_url(self, stream_number, idx=None, total=None, timeout=5):
        """
        Fetch m3u8 URL from player.php
        
        Args:
            stream_number: Stream number
            idx: Progress index (optional, for logging)
            total: Total streams (optional, for logging)
            timeout: Request timeout in seconds
            
        Returns:
            m3u8 URL or None if not found
        """
        try:
            player_url = f"{self.base_url}/player.php?stream={stream_number}"
            response = self.session.get(player_url, timeout=timeout)
            response.raise_for_status()
            
            html_content = response.text
            
            # Search for m3u8 URL in multiple locations and formats
            # Pattern 1: Direct m3u8 in src attribute
            m3u8_patterns = [
                r'src=["\']([^"\']*\.m3u8[^"\']*)["\']',
                # Pattern 2: In HLS.js configuration
                r'src\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                # Pattern 3: In Video.js/VideoJS sources
                r'<source[^>]+src=["\']([^"\']*\.m3u8[^"\']*)["\']',
                # Pattern 4: Quoted URLs anywhere
                r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                # Pattern 5: Unquoted m3u8 URLs
                r'(https?://[^<>\s]+\.m3u8[^<>\s]*)',
                # Pattern 6: In data attributes
                r'data-src=["\']([^"\']*\.m3u8[^"\']*)["\']',
                # Pattern 7: In iframe src
                r'<iframe[^>]+src=["\']([^"\']*)["\'][^>]*>',
            ]
            
            for pattern in m3u8_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    url = match if isinstance(match, str) else match[0]
                    
                    # Filter for m3u8 or valid stream URLs
                    if '.m3u8' in url.lower() or 'stream' in url.lower() or url.startswith('http'):
                        # Normalize URL
                        if not url.startswith('http'):
                            url = urljoin(self.base_url, url)
                        
                        # Filter out common false positives
                        if any(exclude in url.lower() for exclude in ['css', 'js', 'icon', 'logo', 'image']):
                            continue
                            
                        return url
            
            # Debug: if nothing found, try to get it from iframe
            iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', html_content)
            if iframe_match:
                iframe_src = iframe_match.group(1)
                if not iframe_src.startswith('http'):
                    iframe_src = urljoin(self.base_url, iframe_src)
                return iframe_src
            
            return None
            
        except requests.exceptions.RequestException as e:
            # Silently fail instead of printing to reduce noise
            return None
        except Exception as e:
            return None
    
    def scrape_streams(self, fetch_urls=True, delay=0.1):
        """
        Scrape all channel information and m3u8 URLs using concurrent requests
        
        Args:
            fetch_urls: Whether to fetch m3u8 URLs (requires network access)
            delay: Delay between requests in seconds (for rate limiting, typically 0.05-0.2)
        """
        self.parse_html()
        
        if fetch_urls:
            print("Fetching m3u8 URLs using concurrent requests...")
            total = len(self.channels)
            
            # Create a list to track futures with their corresponding channels
            futures_map = {}
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                for idx, channel in enumerate(self.channels, 1):
                    # Use stream_id for fetching (original server stream number)
                    future = executor.submit(self.fetch_m3u8_url, channel['stream_id'], idx, total)
                    futures_map[future] = (idx, channel)
                
                # Process completed futures as they finish
                for future in as_completed(futures_map):
                    idx, channel = futures_map[future]
                    try:
                        m3u8_url = future.result()
                        channel['m3u8_url'] = m3u8_url
                        status = "✓" if m3u8_url else "✗"
                        print(f"[{idx}/{total}] {status} Channel #{channel['number']}: {channel['name']}")
                    except Exception as e:
                        print(f"[{idx}/{total}] ✗ Channel #{channel['number']}: Error - {e}")
                
                # Small delay between batches if specified
                if delay > 0:
                    time.sleep(delay)
        
        return self.channels
    
    def save_json(self, output_file='channels.json'):
        """
        Save channel data to JSON file with metadata
        
        Args:
            output_file: Path to output JSON file
        """
        output_path = Path(output_file)
        
        # Create GMT+6 timestamp
        gmt6 = timezone(timedelta(hours=6))
        timestamp = datetime.now(gmt6).strftime('%Y-%m-%d %H:%M:%S GMT+6')
        
        # Create output structure with metadata
        output_data = {
            "_metadata": {
                "created": timestamp,
                "disclaimer": "We do not host or serve any content. All content belongs to their respective owners."
            },
            "channels": self.channels
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nJSON file saved: {output_path.absolute()}")
        print(f"Total channels: {len(self.channels)}")
        
        # Print summary
        working = sum(1 for c in self.channels if c['m3u8_url'])
        not_working = len(self.channels) - working
        print(f"Working streams: {working}")
        print(f"Failed streams: {not_working}")
    
    def save_m3u(self, output_file='playlist.m3u'):
        """
        Save channels as M3U playlist format
        
        Args:
            output_file: Path to output M3U file
        """
        output_path = Path(output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            
            for channel in self.channels:
                if channel['m3u8_url']:
                    f.write(f"#EXTINF:-1 tvg-logo=\"{channel['logo']}\", {channel['name']}\n")
                    f.write(f"{channel['m3u8_url']}\n")
        
        print(f"M3U playlist saved: {output_path.absolute()}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='IPTV M3U8 Scraper - Automatically fetch and extract streaming information from IPTV server'
    )
    parser.add_argument(
        '--url',
        type=str,
        help='Base URL of the streaming server (default: http://103.144.89.251)',
        default='http://103.144.89.251'
    )
    parser.add_argument(
        '--html',
        type=str,
        help='Path to HTML file (optional, will fetch from URL if not provided)',
        default=None
    )
    parser.add_argument(
        '--json',
        type=str,
        help='Output JSON file path (default: channels.json)',
        default='channels.json'
    )
    parser.add_argument(
        '--m3u',
        type=str,
        help='Output M3U playlist file path (default: playlist.m3u)',
        default='playlist.m3u'
    )
    parser.add_argument(
        '--fetch',
        action='store_true',
        help='Fetch m3u8 URLs from player.php (required for streaming links)',
        default=True
    )
    parser.add_argument(
        '--no-fetch',
        action='store_false',
        dest='fetch',
        help='Skip fetching m3u8 URLs (metadata only)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        help='Delay between request batches in seconds (default: 0.1)',
        default=0.1
    )
    parser.add_argument(
        '--workers',
        type=int,
        help='Number of concurrent workers/threads (default: 8)',
        default=8
    )
    
    args = parser.parse_args()
    
    # Create scraper instance with specified number of workers
    scraper = IPTVScraper(base_url=args.url, html_file=args.html, max_workers=args.workers)
    
    # Scrape data
    scraper.scrape_streams(fetch_urls=args.fetch, delay=args.delay)
    
    # Save outputs (always save both JSON and M3U)
    scraper.save_json(args.json)
    scraper.save_m3u(args.m3u)


if __name__ == '__main__':
    main()
