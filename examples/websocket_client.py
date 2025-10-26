"""
Example WebSocket client for LogFlow
"""
import asyncio
import websockets
import json
from datetime import datetime


async def stream_logs(service=None, level=None):
    """
    Stream logs from LogFlow WebSocket
    
    Args:
        service: Filter by service name (optional)
        level: Filter by log level (optional)
    """
    # Build WebSocket URL with filters
    url = "ws://localhost:8000/ws/logs"
    params = []
    if service:
        params.append(f"service={service}")
    if level:
        params.append(f"level={level}")
    
    if params:
        url += "?" + "&".join(params)
    
    print(f"Connecting to {url}...")
    
    try:
        async with websockets.connect(url) as websocket:
            print("✅ Connected!")
            
            # Receive and display messages
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data.get("type") == "connection":
                    print(f"\n📡 {data.get('message')}\n")
                
                elif data.get("type") == "log":
                    log = data.get("data", {})
                    timestamp = log.get("timestamp", "")
                    level = log.get("level", "INFO")
                    service = log.get("service", "unknown")
                    message = log.get("message", "")
                    
                    # Color code by level
                    color = {
                        "DEBUG": "\033[36m",   # Cyan
                        "INFO": "\033[32m",    # Green
                        "WARN": "\033[33m",    # Yellow
                        "ERROR": "\033[31m",   # Red
                        "CRITICAL": "\033[35m" # Magenta
                    }.get(level, "\033[0m")
                    reset = "\033[0m"
                    
                    print(f"{timestamp} {color}[{level:8}]{reset} {service:20} | {message}")
                
    except websockets.exceptions.ConnectionClosed:
        print("\n❌ Connection closed")
    except KeyboardInterrupt:
        print("\n👋 Disconnected")
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def stream_metrics():
    """Stream real-time metrics from LogFlow"""
    url = "ws://localhost:8000/ws/metrics"
    
    print(f"Connecting to {url}...")
    
    try:
        async with websockets.connect(url) as websocket:
            print("✅ Connected to metrics stream!\n")
            
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data.get("type") == "connection":
                    print(f"📡 {data.get('message')}\n")
                
                elif data.get("type") == "metrics":
                    metrics = data.get("data", {})
                    timestamp = data.get("timestamp", "")
                    
                    print(f"\n📊 Metrics Update - {timestamp}")
                    print(f"   Total Logs: {metrics.get('total_logs', 0)}")
                    
                    by_level = metrics.get("by_level", {})
                    if by_level:
                        print("   By Level:")
                        for level, count in sorted(by_level.items()):
                            print(f"     - {level}: {count}")
                    
                    by_service = metrics.get("by_service", {})
                    if by_service:
                        print("   Top Services:")
                        for service, count in list(sorted(by_service.items(), key=lambda x: x[1], reverse=True))[:5]:
                            print(f"     - {service}: {count}")
                
    except websockets.exceptions.ConnectionClosed:
        print("\n❌ Connection closed")
    except KeyboardInterrupt:
        print("\n👋 Disconnected")
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def stream_alerts():
    """Stream real-time alerts from LogFlow"""
    url = "ws://localhost:8000/ws/alerts"
    
    print(f"Connecting to {url}...")
    
    try:
        async with websockets.connect(url) as websocket:
            print("✅ Connected to alert stream!\n")
            print("Waiting for alerts...\n")
            
            # Send periodic pings to keep connection alive
            async def send_pings():
                while True:
                    await asyncio.sleep(30)
                    await websocket.send(json.dumps({"command": "ping"}))
            
            ping_task = asyncio.create_task(send_pings())
            
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data.get("type") == "connection":
                    print(f"📡 {data.get('message')}\n")
                
                elif data.get("type") == "alert":
                    alert = data.get("data", {})
                    print(f"\n🚨 ALERT TRIGGERED!")
                    print(f"   Rule: {alert.get('rule_name')}")
                    print(f"   Condition: {alert.get('condition')}")
                    print(f"   Current Value: {alert.get('current_value')}")
                    print(f"   Threshold: {alert.get('threshold')}")
                    print(f"   Time: {alert.get('triggered_at')}")
                    print()
                
                elif data.get("type") == "pong":
                    pass  # Ignore pong responses
            
    except websockets.exceptions.ConnectionClosed:
        print("\n❌ Connection closed")
    except KeyboardInterrupt:
        print("\n👋 Disconnected")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python websocket_client.py logs [service] [level]")
        print("  python websocket_client.py metrics")
        print("  python websocket_client.py alerts")
        print()
        print("Examples:")
        print("  python websocket_client.py logs")
        print("  python websocket_client.py logs payment-service")
        print("  python websocket_client.py logs payment-service ERROR")
        print("  python websocket_client.py metrics")
        print("  python websocket_client.py alerts")
        sys.exit(1)
    
    stream_type = sys.argv[1]
    
    if stream_type == "logs":
        service = sys.argv[2] if len(sys.argv) > 2 else None
        level = sys.argv[3] if len(sys.argv) > 3 else None
        asyncio.run(stream_logs(service, level))
    
    elif stream_type == "metrics":
        asyncio.run(stream_metrics())
    
    elif stream_type == "alerts":
        asyncio.run(stream_alerts())
    
    else:
        print(f"Unknown stream type: {stream_type}")
        print("Use: logs, metrics, or alerts")
