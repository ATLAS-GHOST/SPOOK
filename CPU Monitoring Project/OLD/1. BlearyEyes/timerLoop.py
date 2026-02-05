import time

times = []

for _ in range(1000):
    start = time.perf_counter()
    time.sleep(0)  # Request minimum sleep
    end = time.perf_counter()
    times.append(end - start)

# Remove outliers (first few iterations can be slower)
times = sorted(times)[10:-10]

print(f"Minimum sleep time: {min(times)*1000:.6f} ms ({min(times)*1000000:.3f} µs)")
print(f"Average sleep time: {(sum(times)/len(times))*1000:.6f} ms")
print(f"Maximum sleep time: {max(times)*1000:.6f} ms")