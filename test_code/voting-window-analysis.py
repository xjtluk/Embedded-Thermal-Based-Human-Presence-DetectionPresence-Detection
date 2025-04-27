import serial
import argparse
import json
import time
from collections import deque

def analyze_voting_windows(log_file, configurations):
    """
    Analyze system-level performance with different voting window configurations
    
    Args:
        log_file: File with raw frame-by-frame classification results
        configurations: List of voting window configurations to test
    """
    # Load raw classification results
    with open(log_file, 'r') as f:
        raw_results = json.load(f)
    
    print("Voting Window Analysis:")
    print("=" * 70)
    print(f"{'Frames':^10}|{'Threshold':^12}|{'Overall Acc (%)':^16}|{'FPR (%)':^10}|{'FNR (%)':^10}|{'Latency (ms)':^12}")
    print("-" * 70)
    
    # Process each configuration
    for config in configurations:
        window_size = config['window_size']
        threshold_percent = config['threshold_percent']
        threshold = int(window_size * threshold_percent / 100)
        
        predictions = []
        ground_truth = []
        
        # Sliding window over results
        detection_window = deque(maxlen=window_size)
        
        for i, frame in enumerate(raw_results):
            # Add current frame result to window
            detection_window.append(1 if frame['raw_prediction'] == 'person' else 0)
            
            # Only make decision when window is full
            if i >= window_size - 1:
                # Apply majority voting
                vote_sum = sum(detection_window)
                final_prediction = 1 if vote_sum >= threshold else 0
                predictions.append(final_prediction)
                ground_truth.append(1 if frame['ground_truth'] == 'person' else 0)
        
        # Calculate metrics
        correct = sum(p == g for p, g in zip(predictions, ground_truth))
        accuracy = (correct / len(predictions)) * 100 if predictions else 0
        
        # Calculate FPR and FNR
        false_positives = sum(p == 1 and g == 0 for p, g in zip(predictions, ground_truth))
        false_negatives = sum(p == 0 and g == 1 for p, g in zip(predictions, ground_truth))
        true_negatives = sum(p == 0 and g == 0 for p, g in zip(predictions, ground_truth))
        true_positives = sum(p == 1 and g == 1 for p, g in zip(predictions, ground_truth))
        
        fpr = (false_positives / (false_positives + true_negatives)) * 100 if (false_positives + true_negatives) > 0 else 0
        fnr = (false_negatives / (false_negatives + true_positives)) * 100 if (false_negatives + true_positives) > 0 else 0
        
        # Latency is approximately half the window size in ms (assuming 4Hz = 250ms per frame)
        latency_ms = (window_size - 1) * 250 / 2
        
        print(f"{window_size:^10}|{threshold_percent:^12}|{accuracy:^16.1f}|{fpr:^10.1f}|{fnr:^10.1f}|{latency_ms:^12.1f}")

def capture_raw_results(port, baudrate, duration, output_file):
    """
    Capture raw frame-by-frame classification results from device
    
    Args:
        port: Serial port connected to Arduino
        baudrate: Baud rate for serial communication
        duration: Test duration in seconds
        output_file: JSON file to save raw results
    """
    print(f"Capturing raw classification results for {duration} seconds...")
    
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Wait for connection to stabilize
    
    # Clear buffer
    ser.reset_input_buffer()
    
    # Send command to start raw results mode
    ser.write(b'RAW_RESULTS\n')
    
    results = []
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("RESULT:"):
            # Format: RESULT:raw_prediction,confidence,ground_truth
            data = line.split(':')[1].split(',')
            results.append({
                'raw_prediction': data[0],
                'confidence': float(data[1]),
                'ground_truth': data[2]
            })
    
    ser.close()
    
    # Save results to file
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Captured {len(results)} raw results and saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze majority voting windows")
    parser.add_argument("--port", help="Serial port for capturing raw results")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baud rate")
    parser.add_argument("--duration", type=int, default=300, help="Capture duration in seconds")
    parser.add_argument("--output", default="raw_results.json", help="Output file for raw results")
    parser.add_argument("--analyze", action="store_true", help="Analyze existing raw results")
    parser.add_argument("--input", help="Input file with raw results for analysis")
    
    args = parser.parse_args()
    
    if not args.analyze and args.port:
        # Capture mode
        capture_raw_results(args.port, args.baudrate, args.duration, args.output)
    
    if args.analyze and args.input:
        # Analysis mode
        configurations = [
            {'window_size': 2, 'threshold_percent': 50},  # >50% of 2 frames
            {'window_size': 4, 'threshold_percent': 50},  # >50% of 4 frames
            {'window_size': 4, 'threshold_percent': 75},  # ≥75% of 4 frames
            {'window_size': 6, 'threshold_percent': 50},  # >50% of 6 frames
            {'window_size': 8, 'threshold_percent': 50},  # >50% of 8 frames
        ]
        analyze_voting_windows(args.input, configurations)
