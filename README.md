# Log Extractor from Large Log Archive

This repository provides a solution for efficiently extracting logs from a large log file stored inside a zip archive. The script is designed to handle files of approximately 1 TB in size and return log entries for a specified date.

## Solutions Considered

1. **Sequential File Reading**
   - **Pros**: Simple implementation.
   - **Cons**: Inefficient for large files as it requires reading the entire file sequentially to find entries for a specific date.

2. **Binary Search on Timestamps**
   - **Pros**: Efficient for sorted data, reduces the search space.
   - **Cons**: Requires the file to be pre-indexed or sorted by date, which is impractical for such large data without preprocessing.

3. **Parallel Processing**
   - **Pros**: Speeds up processing by dividing the file into chunks that can be processed concurrently.
   - **Cons**: Requires careful handling to manage chunk boundaries and memory.

4. **Indexing**
   - **Pros**: Pre-indexing the file can allow for fast lookup.
   - **Cons**: Indexing a 1 TB file is resource-intensive and may not fit the problem constraints.

## Final Solution Summary

The final solution combines **parallel processing** with efficient zip file handling. The script opens the zip archive, processes the log file in chunks using multiple processes, and extracts log entries that match the specified date. This approach ensures efficient usage of computational resources and time.

## Steps to Run

### Prerequisites

- Python 3.x installed on your system.

### Set Up

1. **Clone the Repository:**
   ```bash
   git clone <https://github.com/Naveen7854/FarMart>
   cd <repository-directory>
   ```

2. **Install Required Libraries:**
   - Ensure that `zipfile` and `concurrent.futures` (which is included in the Python standard library from Python 3.2+) are available.

### Execution

1. **Run the Script:**

   Execute the script with the specified date (format: `YYYY-MM-DD`) as a command-line argument:

   ```bash
   python extract_logs.py 2024-12-01
   ```

2. **Output:**
   
   - The output will be saved in the `output/` directory with the filename `output_YYYY-MM-DD.txt`.
   - The directory will be automatically created if it doesn't exist.

### Implementation Details

- **File Handling:** The script uses Python's `zipfile` module to read from the compressed log file.
- **Parallel Execution:** Using `ProcessPoolExecutor`, the log file is processed in chunks to improve efficiency when extracting desired log entries.

## Notes

- The script assumes that the log file within the zip archive is the first file listed and logs are generated nearly uniformly.
- Ensure sufficient memory is available when processing large files as the script reads significant portions into memory for processing.
- Modify `zip_file_path` in the script to point to the correct path of your log archive.

---

This README provides a comprehensive guide to running and understanding the log extraction solution effectively.
