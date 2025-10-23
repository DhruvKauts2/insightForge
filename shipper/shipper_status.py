"""Simple script to check shipper status"""
from pathlib import Path

def get_status():
    pid_file = Path('.shipper.pid')
    if pid_file.exists():
        pid = pid_file.read_text().strip()
        print(f"✅ Shipper is running (PID: {pid})")
        
        # Check log file
        log_file = Path('logs/shipper.log')
        if log_file.exists():
            lines = log_file.read_text().splitlines()
            # Find last "Sent X logs" message
            for line in reversed(lines[-50:]):
                if 'Sent' in line and 'logs to Kafka' in line:
                    print(f"📊 {line.strip()}")
                    break
    else:
        print("❌ Shipper is not running")

if __name__ == "__main__":
    get_status()
