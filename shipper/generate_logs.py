"""
Log Generator - Creates realistic application logs for testing
Generates logs for multiple services with different log levels
"""

import time
import random
from datetime import datetime
from pathlib import Path
import json

# Configuration
SERVICES = ['payment-service', 'auth-service', 'user-service', 'order-service', 'inventory-service']
LOG_LEVELS = ['INFO', 'WARN', 'ERROR', 'DEBUG']

# Realistic log messages by level
LOG_MESSAGES = {
    'INFO': [
        'Request processed successfully',
        'User logged in successfully',
        'Payment completed for order',
        'Order created successfully',
        'Database query executed',
        'Cache hit for key',
        'API request completed',
        'Session created',
        'Email notification sent',
        'Background job completed',
    ],
    'WARN': [
        'Rate limit approaching for user',
        'Slow query detected (>1s)',
        'Cache miss, fetching from database',
        'Retry attempt {attempt} for operation',
        'High memory usage detected',
        'Connection pool almost exhausted',
        'API response time degraded',
        'Queue backlog increasing',
        'Deprecated API endpoint called',
        'SSL certificate expires in 7 days',
    ],
    'ERROR': [
        'Database connection timeout after 5s',
        'Payment gateway unavailable',
        'Authentication failed: invalid credentials',
        'Invalid request format: missing required field',
        'Failed to send email notification',
        'Service unavailable: connection refused',
        'Transaction rolled back due to error',
        'File not found: /path/to/resource',
        'Rate limit exceeded for IP address',
        'Internal server error: unexpected exception',
    ],
    'DEBUG': [
        'Entering function: processOrder()',
        'Query parameters: {params}',
        'Response body: {data}',
        'Cache lookup for key: user_123',
        'Validating input parameters',
        'HTTP request to external API',
        'Database connection acquired',
        'Session data: {session_info}',
        'Parsing JSON payload',
        'Processing batch of 100 items',
    ]
}

# Additional context for some messages
CONTEXTS = {
    'order_id': lambda: f"order_{random.randint(10000, 99999)}",
    'user_id': lambda: f"user_{random.randint(1, 1000)}",
    'transaction_id': lambda: f"txn_{random.randint(100000, 999999)}",
    'ip_address': lambda: f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
    'duration_ms': lambda: random.randint(10, 5000),
    'amount': lambda: round(random.uniform(10.0, 1000.0), 2),
}


class LogGenerator:
    def __init__(self, output_dir='sample_logs', format_type='text'):
        """
        Initialize log generator
        
        Args:
            output_dir: Directory to write logs
            format_type: 'text' for plain text logs, 'json' for JSON logs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.format_type = format_type
        self.log_file = self.output_dir / f'app.log'
        self.log_count = 0
        
    def generate_log_line(self):
        """Generate a single log line"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Weight distribution: 70% INFO, 15% WARN, 10% ERROR, 5% DEBUG
        level = random.choices(LOG_LEVELS, weights=[70, 15, 10, 5])[0]
        service = random.choice(SERVICES)
        message = random.choice(LOG_MESSAGES[level])
        
        # Add context to some messages
        if '{' in message:
            if 'order' in message.lower():
                message = message.replace('{order_id}', CONTEXTS['order_id']())
            if 'user' in message.lower():
                message = message.replace('{user_id}', CONTEXTS['user_id']())
            if 'attempt' in message.lower():
                message = message.replace('{attempt}', str(random.randint(1, 3)))
            # Generic replacements
            message = message.replace('{params}', str({'page': 1, 'limit': 10}))
            message = message.replace('{data}', str({'status': 'ok'}))
            message = message.replace('{session_info}', str({'user_id': CONTEXTS['user_id']()}))
        
        # Add additional fields for some log types
        extra_fields = {}
        if level == 'ERROR':
            extra_fields['error_code'] = random.choice(['E001', 'E002', 'E500', 'E503'])
        if 'order' in message.lower():
            extra_fields['order_id'] = CONTEXTS['order_id']()
        if 'user' in message.lower():
            extra_fields['user_id'] = CONTEXTS['user_id']()
        
        if self.format_type == 'json':
            log_entry = {
                'timestamp': timestamp,
                'level': level,
                'service': service,
                'message': message,
                **extra_fields
            }
            return json.dumps(log_entry)
        else:
            # Plain text format
            extra = ' '.join([f'{k}={v}' for k, v in extra_fields.items()])
            if extra:
                return f"{timestamp} {level} [{service}] {message} {extra}"
            return f"{timestamp} {level} [{service}] {message}"
    
    def generate_burst(self, count=10):
        """Generate a burst of logs (simulating high activity)"""
        with open(self.log_file, 'a') as f:
            for _ in range(count):
                log_line = self.generate_log_line()
                f.write(log_line + '\n')
                self.log_count += 1
        print(f"Generated burst of {count} logs (total: {self.log_count})")
    
    def run(self, logs_per_second=5, burst_interval=30):
        """
        Run continuous log generation
        
        Args:
            logs_per_second: Average logs to generate per second
            burst_interval: Generate burst every N seconds
        """
        print(f"🚀 Starting log generator...")
        print(f"📁 Writing to: {self.log_file}")
        print(f"📊 Format: {self.format_type}")
        print(f"⚡ Rate: ~{logs_per_second} logs/second")
        print(f"💥 Bursts every {burst_interval} seconds")
        print(f"\nPress Ctrl+C to stop\n")
        
        last_burst = time.time()
        
        try:
            with open(self.log_file, 'a') as f:
                while True:
                    # Generate normal log
                    log_line = self.generate_log_line()
                    f.write(log_line + '\n')
                    f.flush()  # Ensure it's written immediately
                    self.log_count += 1
                    
                    # Print progress every 10 logs
                    if self.log_count % 10 == 0:
                        print(f"✓ Generated {self.log_count} logs")
                    
                    # Generate burst periodically
                    if time.time() - last_burst > burst_interval:
                        burst_size = random.randint(20, 50)
                        print(f"💥 Generating burst of {burst_size} logs...")
                        for _ in range(burst_size):
                            log_line = self.generate_log_line()
                            f.write(log_line + '\n')
                            self.log_count += 1
                        f.flush()
                        last_burst = time.time()
                    
                    # Sleep to control rate
                    time.sleep(random.uniform(0.5, 2.0) / logs_per_second)
                    
        except KeyboardInterrupt:
            print(f"\n\n✅ Stopped. Generated {self.log_count} total logs")
            print(f"📁 Log file: {self.log_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate realistic application logs')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='Log format (default: text)')
    parser.add_argument('--rate', type=int, default=5,
                        help='Logs per second (default: 5)')
    parser.add_argument('--burst-interval', type=int, default=30,
                        help='Seconds between bursts (default: 30)')
    parser.add_argument('--output-dir', default='sample_logs',
                        help='Output directory (default: sample_logs)')
    
    args = parser.parse_args()
    
    generator = LogGenerator(
        output_dir=args.output_dir,
        format_type=args.format
    )
    
    generator.run(
        logs_per_second=args.rate,
        burst_interval=args.burst_interval
    )
