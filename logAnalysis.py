import os

def analyze_logs(log_folder="error_logs"):
    if not os.path.exists(log_folder):
        print(f"No log folder found at {log_folder}.")
        return
    
    log_files = [f for f in os.listdir(log_folder) if f.endswith(".log")]
    if not log_files:
        print("No log files found.")
        return
    
    print(f"Found {len(log_files)} log file(s) in {log_folder}:")
    for log_file in log_files:
        log_path = os.path.join(log_folder, log_file)
        print(f"\n--- {log_file} ---")
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(content[:500])  # Display the first 500 characters of the log file

if __name__ == "__main__":
    analyze_logs()