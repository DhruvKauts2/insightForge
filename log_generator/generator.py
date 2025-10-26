"""
Enhanced log generator with correlation IDs for transaction tracing
"""
import random
import time
import json
from datetime import datetime
from kafka import KafkaProducer
from loguru import logger
import uuid

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'logs-raw'

# Services configuration
SERVICES = [
    "auth-service",
    "payment-service",
    "user-service",
    "notification-service",
    "inventory-service",
    "order-service",
    "shipping-service"
]

# Log levels and their probabilities
LOG_LEVELS = {
    "DEBUG": 0.20,
    "INFO": 0.50,
    "WARN": 0.20,
    "ERROR": 0.08,
    "CRITICAL": 0.02
}

# Sample log messages by service
LOG_MESSAGES = {
    "auth-service": [
        "User login successful",
        "User registration completed",
        "Password reset requested",
        "Token validated",
        "Session expired",
        "Invalid credentials",
        "MFA verification completed"
    ],
    "payment-service": [
        "Payment processed successfully",
        "Payment gateway timeout",
        "Payment authorization failed",
        "Refund initiated",
        "Payment captured",
        "Card validation failed",
        "Transaction completed"
    ],
    "user-service": [
        "User profile updated",
        "User preferences saved",
        "Email verification sent",
        "Profile image uploaded",
        "User account activated",
        "User data exported",
        "Account settings changed"
    ],
    "notification-service": [
        "Email sent successfully",
        "Push notification delivered",
        "SMS sent",
        "Notification queue processed",
        "Email delivery failed",
        "Template rendered",
        "Notification scheduled"
    ],
    "inventory-service": [
        "Stock level updated",
        "Item reserved",
        "Inventory check completed",
        "Stock replenished",
        "Item out of stock",
        "Warehouse sync completed",
        "Product availability checked"
    ],
    "order-service": [
        "Order created",
        "Order confirmed",
        "Order cancelled",
        "Order status updated",
        "Order validation failed",
        "Order processing started",
        "Order completed"
    ],
    "shipping-service": [
        "Shipment created",
        "Tracking number generated",
        "Package picked up",
        "Delivery in progress",
        "Package delivered",
        "Delivery failed",
        "Address validation completed"
    ]
}

# Transaction flows (service call chains)
TRANSACTION_FLOWS = [
    # User registration flow
    ["auth-service", "user-service", "notification-service"],
    
    # Order checkout flow
    ["auth-service", "order-service", "inventory-service", "payment-service", "notification-service"],
    
    # Payment flow
    ["auth-service", "payment-service", "notification-service"],
    
    # Shipping flow
    ["order-service", "inventory-service", "shipping-service", "notification-service"],
    
    # Simple flows
    ["auth-service", "user-service"],
    ["order-service", "payment-service"],
]


def weighted_random_choice(choices_dict):
    """Select item based on weights"""
    choices = list(choices_dict.keys())
    weights = list(choices_dict.values())
    return random.choices(choices, weights=weights)[0]


def generate_transaction_logs(producer, correlation_id, flow):
    """Generate a series of correlated logs for a transaction"""
    request_id = str(uuid.uuid4())
    
    for i, service in enumerate(flow):
        # Slight delay between service calls
        if i > 0:
            time.sleep(random.uniform(0.1, 0.5))
        
        # Determine log level (errors more likely later in the chain)
        if i < len(flow) - 1:
            # Earlier in chain - mostly INFO
            level = weighted_random_choice({
                "INFO": 0.85,
                "DEBUG": 0.10,
                "WARN": 0.04,
                "ERROR": 0.01
            })
        else:
            # Last service - normal distribution
            level = weighted_random_choice(LOG_LEVELS)
        
        # Get appropriate message
        messages = LOG_MESSAGES.get(service, ["Processing request"])
        message = random.choice(messages)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "service": service,
            "message": message,
            "correlation_id": correlation_id,
            "request_id": request_id,
            "transaction_position": i + 1,
            "transaction_total": len(flow),
            "metadata": {
                "environment": "production",
                "region": "us-east-1",
                "instance_id": f"{service}-{random.randint(1, 5)}"
            }
        }
        
        # Send to Kafka
        producer.send(
            KAFKA_TOPIC,
            value=log_entry,
            key=correlation_id.encode('utf-8')
        )
        
        logger.info(f"[{correlation_id[:8]}] {service} [{level}] {message}")


def generate_standalone_log(producer):
    """Generate a single uncorrelated log"""
    service = random.choice(SERVICES)
    level = weighted_random_choice(LOG_LEVELS)
    message = random.choice(LOG_MESSAGES.get(service, ["Processing request"]))
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "service": service,
        "message": message,
        "metadata": {
            "environment": "production",
            "region": "us-east-1",
            "instance_id": f"{service}-{random.randint(1, 5)}"
        }
    }
    
    producer.send(KAFKA_TOPIC, value=log_entry)
    logger.debug(f"Standalone: {service} [{level}] {message}")


def main():
    """Main log generator"""
    logger.info("Starting enhanced log generator with correlation support...")
    
    # Create Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    logger.info(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
    logger.info(f"Generating logs to topic: {KAFKA_TOPIC}")
    logger.info("70% correlated transactions, 30% standalone logs")
    
    try:
        counter = 0
        while True:
            # 70% chance of generating a transaction, 30% standalone
            if random.random() < 0.7:
                # Generate correlated transaction
                correlation_id = str(uuid.uuid4())
                flow = random.choice(TRANSACTION_FLOWS)
                generate_transaction_logs(producer, correlation_id, flow)
                counter += len(flow)
            else:
                # Generate standalone log
                generate_standalone_log(producer)
                counter += 1
            
            if counter % 100 == 0:
                logger.info(f"Generated {counter} logs")
            
            # Random delay between transactions
            time.sleep(random.uniform(0.5, 2.0))
            
    except KeyboardInterrupt:
        logger.info("\nStopping log generator...")
    finally:
        producer.close()
        logger.info(f"Generator stopped. Total logs: {counter}")


if __name__ == "__main__":
    main()
