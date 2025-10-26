import sys, json

data = json.load(sys.stdin)
if data:
    print(f"✅ Found {len(data)} anomalies:")
    for i, a in enumerate(data, 1):
        print(f"\n{i}. {a['severity'].upper()} - {a['anomaly_type']}")
        print(f"   Actual: {a['actual_value']:.0f}")
        print(f"   Expected: {a['expected_value']:.0f}")
        print(f"   Deviation: {a['deviation_percent']:.1f}%")
        print(f"   Score: {a['score']:.2f}")
else:
    print("❌ No anomalies detected")
