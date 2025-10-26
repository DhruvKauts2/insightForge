import numpy as np

values = [1600, 0, 3000, 0, 3000]
timestamps = ["t1", "t2", "t3", "t4", "t5"]
time_series = list(zip(timestamps, values))

print(f"Time series: {time_series}")
print(f"Length: {len(time_series)}")

values = np.array([v for _, v in time_series])
mean = np.mean(values)
std = np.std(values)

print(f"Mean: {mean}, Std: {std}")

if std == 0:
    print("Std is 0, no anomalies")
else:
    z_scores = np.abs((values - mean) / std)
    print(f"Z-scores: {z_scores}")
    
    threshold = 1.0  # Our new sensitivity
    anomaly_indices = np.where(z_scores > threshold)[0]
    print(f"Threshold: {threshold}")
    print(f"Anomaly indices: {anomaly_indices}")
    print(f"Anomaly values: {values[anomaly_indices]}")
