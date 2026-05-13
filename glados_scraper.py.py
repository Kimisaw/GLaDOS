import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import os

# Correct URLs (with closing parentheses)
urls = {
    'portal': 'https://theportalwiki.com/wiki/GLaDOS_voice_lines_(Portal)',
    'portal2': 'https://theportalwiki.com/wiki/GLaDOS_voice_lines_(Portal_2)',
    'coop': 'https://theportalwiki.com/wiki/GLaDOS_voice_lines_(Cooperative_Testing_Initiative)',
    'other': 'https://theportalwiki.com/wiki/GLaDOS_voice_lines_(Other)',
}

# Base directory for output paths (NOT where we search for files)
BASE_DIR = '/storage/plzen1/home/sike/GLaDOS/'

def get_wav_files(directory):
    """Get all .wav files from the specified directory."""
    wav_files = []
    for file in os.listdir(directory):
        if file.lower().endswith('.wav'):
            wav_files.append(file)
    return wav_files

# Scrape a single wiki page
def scrape_page(url, page_name):
    print(f"Fetching {page_name} from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"  ERROR: Failed to fetch {page_name}: {e}")
        return {}
    
    transcripts = {}
    page_count = 0
    
    # Find all list items containing voice lines
    for li in soup.find_all('li'):
        # Find the italic text containing the transcript
        i_tag = li.find('i')
        if not i_tag:
            continue
        
        # Extract transcript (remove the surrounding quotes if present)
        transcript = i_tag.get_text()
        transcript = transcript.strip('"').strip("'").strip()
        
        # Find the download link to get the filename
        download_link = li.find('a', href=re.compile(r'\.wav'))
        if not download_link:
            continue
        
        # Extract filename from URL
        href = download_link.get('href', '')
        filename = href.split('/')[-1]
        
        # Store transcript
        transcripts[filename] = transcript
        page_count += 1
    
    print(f"  Found {page_count} transcripts")
    return transcripts

# Main execution
def main():
    print("=" * 60)
    print("GLaDOS Voice Line Scraper")
    print("=" * 60)
    
    # Get the current working directory (where script is launched)
    current_dir = os.getcwd()
    print(f"\nSearching for .wav files in: {current_dir}")
    
    # Get all .wav files from the current directory
    wav_files = get_wav_files(current_dir)
    print(f"Found {len(wav_files)} .wav files")
    
    if len(wav_files) == 0:
        print("No .wav files found. Exiting.")
        return
    
    # Scrape all pages
    all_transcripts = {}
    for name, url in urls.items():
        time.sleep(1)  # Be polite to the server
        transcripts = scrape_page(url, name)
        all_transcripts.update(transcripts)
    
    print(f"\nTotal unique transcripts found: {len(all_transcripts)}")
    
    # Match and generate output
    output_lines = []
    matched_count = 0
    not_found = []
    
    for filename in wav_files:
        if filename in all_transcripts:
            transcript = all_transcripts[filename]
            # Clean up transcript - remove newlines and extra spaces
            transcript = ' '.join(transcript.split())
            # Build output line with the base directory (not where the file actually is)
            output_line = f"{BASE_DIR}{filename}|GLaDOS|EN|{transcript}"
            output_lines.append(output_line)
            matched_count += 1
        else:
            not_found.append(filename)
    
    # Write to metadata.list
    with open('metadata.list', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"\n" + "=" * 60)
    print(f"RESULTS:")
    print(f"  Matched: {matched_count} files")
    print(f"  Not found: {len(not_found)} files")
    print(f"  Output written to: metadata.list")
    
    if not_found and len(not_found) <= 20:
        print(f"\nFiles not found (first 20):")
        for fname in not_found[:20]:
            print(f"  - {fname}")
    elif not_found:
        print(f"\nFiles not found: {len(not_found)} total (see not_found.txt for list)")
        with open('not_found.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(not_found))

if __name__ == "__main__":
    main()