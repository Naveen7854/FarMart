#!/usr/bin/env python3

import sys
import os
from datetime import datetime
import mmap
import argparse
from pathlib import Path
import zipfile
import tempfile
import shutil
import requests
from tqdm import tqdm

class LogExtractor:
    def __init__(self, zip_url):
        self.zip_url = zip_url
        self.temp_dir = None
        self.log_file_path = None
        
    def download_and_extract(self):
        """Download and extract the zip file"""
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(self.temp_dir, "logs.zip")
            
            # Download the zip file with progress bar
            print("Downloading zip file...")
            response = requests.get(self.zip_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(zip_path, 'wb') as f:
                with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
                    for data in response.iter_content(chunk_size=1024*1024):
                        size = f.write(data)
                        pbar.update(size)
            
            # Extract the zip file
            print("Extracting zip file...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
                
            # Find the log file (assuming there's only one .log or .txt file)
            for file in os.listdir(self.temp_dir):
                if file.endswith(('.log', '.txt')):
                    self.log_file_path = os.path.join(self.temp_dir, file)
                    break
                    
            if not self.log_file_path:
                raise Exception("No log file found in zip archive")
                
        except Exception as e:
            self.cleanup()
            raise Exception(f"Error downloading/extracting zip file: {str(e)}")
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def _create_output_directory(self):
        """Create output directory if it doesn't exist"""
        Path("output").mkdir(exist_ok=True)
        
    def _get_line_at_position(self, mm, position):
        """Get complete line at given position"""
        # Search backward for line start
        while position > 0 and mm[position - 1:position] != b'\n':
            position -= 1
        
        line_start = position
        
        # Search forward for line end
        while position < len(mm) and mm[position:position + 1] != b'\n':
            position += 1
            
        return mm[line_start:position].decode('utf-8')

    def _binary_search_date(self, mm, target_date):
        """Binary search to find the first occurrence of the target date"""
        left, right = len(mm)
        first_occurrence = -1
        
        while left < right:
            mid = (left + right) // 2
            
            # Get complete line at mid position
            line = self._get_line_at_position(mm, mid)
            try:
                line_date = line[:10]  # Extract date part (YYYY-MM-DD)
                
                if line_date == target_date:
                    first_occurrence = mid
                    right = mid  # Continue searching left for first occurrence
                elif line_date < target_date:
                    left = mid + 1
                else:
                    right = mid
            except:
                right = mid
                
        return first_occurrence

    def extract_logs(self, target_date):
        """Extract all logs for the given date"""
        try:
            # Download and extract zip file
            self.download_and_extract()
            
            self._create_output_directory()
            output_file = f"output/output_{target_date}.txt"
            
            print(f"Processing logs for date {target_date}...")
            with open(self.log_file_path, 'rb') as f:
                # Memory-map the file for efficient reading
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                
                # Find first occurrence of target date
                position = self._binary_search_date(mm, target_date)
                
                if position == -1:
                    print(f"No logs found for date {target_date}")
                    return
                
                # Open output file
                with open(output_file, 'w') as out_f:
                    # Read forward until date changes
                    while position < len(mm):
                        line = self._get_line_at_position(mm, position)
                        if not line.startswith(target_date):
                            break
                            
                        out_f.write(line + '\n')
                        
                        # Move to next line
                        position += len(line.encode('utf-8')) + 1
                
                mm.close()
                
            print(f"Logs extracted successfully to {output_file}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            self.cleanup()

def validate_url(url):
    """Validate the URL format"""
    try:
        response = requests.head(url)
        return response.status_code == 200
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description='Extract logs for a specific date from a zip file')
    parser.add_argument('date', help='Date in YYYY-MM-DD format')
    parser.add_argument('--url', default="https://limewire.com/d/608b3bd4-c3bf-45c6-abc1-91302035b7e4#ILE27cGoutmcDEpHdV9VqQRvJkC16pq7v1Nx2rzoIl4",
                        help='URL of the zip file containing logs')
    args = parser.parse_args()
    
    # Validate date format
    try:
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD")
        sys.exit(1)
    
    # Validate URL
    if not validate_url(args.url):
        print("Error: Invalid or inaccessible URL")
        sys.exit(1)
    
    extractor = LogExtractor(args.url)
    extractor.extract_logs(args.date)

if __name__ == "__main__":
    main()