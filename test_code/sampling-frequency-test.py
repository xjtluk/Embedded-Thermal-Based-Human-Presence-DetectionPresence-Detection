import serial
import time
import statistics
import argparse

def test_sampling_frequency(port, baudrate, duration=60):
    """
    Test the actual sampling frequency and current draw of the system.
    
    Args:
        port: Serial port connected to Arduino
        baudrate: Baud rate for serial communication
        duration: Test duration in seconds
    """
    print(f"Testing sampling frequency for {duration} seconds...")
    
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Wait for connection to stabilize
    
    # Clear buffer
    ser.reset_input_buffer()
    
    frame_times = []
    start_time = time.time()
    frames_received = 0
    
    # Send command to start test mode
    ser.write(b'TEST_MODE\n')
    
    while (time.time() - start_time) < duration:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("FRAME_TIME:"):
            # Format: FRAME_TIME:capture_ms,process_ms,total_ms
            times = line.split(':')[1].split(',')
            frame_times.append({
                'capture': float(times[0]),
                'process': float(times[1]),
                'total': float(times[2])
            })
            frames_received += 1
            
        if line.startswith("CURRENT:"):
            current_draw = float(line.split(':')[1])
            print(f"Current draw: {current_draw:.2f} mA")
    
    # Calculate statistics
    actual_duration = time.time() - start_time
    actual_rate = frames_received / actual_duration
    
    # Calculate averages and standard deviations
    if frame_times:
        avg_capture = statistics.mean([t['capture'] for t in frame_times])
        avg_process = statistics.mean([t['process'] for t in frame_times])
        avg_total = statistics.mean([t['total'] for t in frame_times])
        
        std_capture = statistics.stdev([t['capture'] for t in frame_times]) if len(frame_times) > 1 else 0
        std_process = statistics.stdev([t['process'] for t in frame_times]) if len(frame_times) > 1 else 0
        std_total = statistics.stdev([t['total'] for t in frame_times]) if len(frame_times) > 1 else 0
    
        print(f"\nResults for {frames_received} frames over {actual_duration:.2f} seconds:")
        print(f"Actual sampling rate: {actual_rate:.2f} Hz")
        print(f"Frame capture time: {avg_capture:.2f} ms (±{std_capture:.2f} ms)")
        print(f"Frame processing time: {avg_process:.2f} ms (±{std_process:.2f} ms)")
        print(f"Total frame time: {avg_total:.2f} ms (±{std_total:.2f} ms)")
    
    ser.close()

def test_latency(port, baudrate, num_tests=20):
    """
    Test end-to-end latency from frame read to LED update
    
    Args:
        port: Serial port connected to Arduino
        baudrate: Baud rate for serial communication
        num_tests: Number of latency tests to run
    """
    print(f"Testing end-to-end latency with {num_tests} tests...")
    
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Wait for connection to stabilize
    
    # Clear buffer
    ser.reset_input_buffer()
    
    # Send command to start latency test mode
    ser.write(b'LATENCY_TEST\n')
    
    latencies = []
    
    for i in range(num_tests):
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("LATENCY:"):
            latency = float(line.split(':')[1])
            latencies.append(latency)
            print(f"Test {i+1}/{num_tests}: {latency:.2f} ms")
    
    if latencies:
        avg_latency = statistics.mean(latencies)
        std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
        print(f"\nAverage end-to-end latency: {avg_latency:.2f} ms (±{std_latency:.2f} ms)")
    
    ser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test sampling frequency and latency")
    parser.add_argument("--port", required=True, help="Serial port (e.g., COM6 or /dev/ttyACM0)")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baud rate")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--latency-tests", type=int, default=20, help="Number of latency tests")
    parser.add_argument("--test-type", choices=["freq", "latency", "both"], default="both", 
                        help="Test type: freq (frequency), latency, or both")
    
    args = parser.parse_args()
    
    if args.test_type in ["freq", "both"]:
        test_sampling_frequency(args.port, args.baudrate, args.duration)
    
    if args.test_type in ["latency", "both"]:
        test_latency(args.port, args.baudrate, args.latency_tests)
