import serial
import time
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

def test_distance_performance(port, baudrate, distances, tests_per_distance=20):
    """
    Test detection performance at different distances
    
    Args:
        port: Serial port connected to Arduino
        baudrate: Baud rate for serial communication
        distances: List of distances to test (in meters)
        tests_per_distance: Number of tests to run at each distance
    """
    print("Testing detection performance at different distances...")
    
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Wait for connection to stabilize
    
    # Clear buffer
    ser.reset_input_buffer()
    
    results = {}
    
    for distance in distances:
        print(f"\nTesting at {distance} meters...")
        print(f"Position the subject {distance} meters from the sensor and press Enter")
        input()
        
        # Send command to start distance test mode
        ser.write(b'DISTANCE_TEST\n')
        
        detections = 0
        confidence_scores = []
        
        for i in range(tests_per_distance):
            # Allow time for sensor reading and processing
            time.sleep(1)
            
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("DETECTION:"):
                # Format: DETECTION:result,confidence
                data = line.split(':')[1].split(',')
                result = data[0]
                confidence = float(data[1])
                
                if result == "PERSON":
                    detections += 1
                confidence_scores.append(confidence)
                
                print(f"Test {i+1}/{tests_per_distance}: {result} (confidence: {confidence:.2f})")
        
        # Calculate metrics
        detection_rate = (detections / tests_per_distance) * 100
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
        
        results[distance] = {
            'detection_rate': detection_rate,
            'avg_confidence': avg_confidence
        }
        
        print(f"Results at {distance}m: Detection rate: {detection_rate:.1f}%, Average confidence: {avg_confidence:.2f}")
    
    ser.close()
    
    # Save results to file
    with open("distance_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Plot results
    plot_distance_results(results)

def plot_distance_results(results):
    """
    Plot distance performance results
    
    Args:
        results: Dictionary with distance test results
    """
    distances = sorted([float(d) for d in results.keys()])
    detection_rates = [results[str(d)]['detection_rate'] for d in distances]
    confidence_scores = [results[str(d)]['avg_confidence'] for d in distances]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = 'tab:blue'
    ax1.set_xlabel('Distance (m)')
    ax1.set_ylabel('Detection Rate (%)', color=color)
    ax1.plot(distances, detection_rates, 'o-', color=color, linewidth=2)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.set_ylim(0, 105)
    
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Confidence Score', color=color)
    ax2.plot(distances, confidence_scores, 's-', color=color, linewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax2.set_ylim(0, 1.05)
    
    plt.title('Detection Performance vs Distance', fontsize=14)
    fig.tight_layout()
    plt.savefig('distance_performance.png', dpi=300)
    plt.show()

def load_and_plot_results(results_file):
    """
    Load and plot existing distance test results
    
    Args:
        results_file: JSON file with distance test results
    """
    with open(results_file, 'r') as f:
        results = json.load(f)
    plot_distance_results(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test detection performance at different distances")
    parser.add_argument("--port", help="Serial port connected to Arduino")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baud rate")
    parser.add_argument("--distances", type=str, default="1,2,3,4,5,6", 
                        help="Comma-separated list of distances to test (in meters)")
    parser.add_argument("--tests", type=int, default=20, help="Number of tests per distance")
    parser.add_argument("--plot-only", action="store_true", help="Only plot existing results")
    parser.add_argument("--results-file", help="JSON file with existing results for plotting")
    
    args = parser.parse_args()
    
    if args.plot_only and args.results_file:
        load_and_plot_results(args.results_file)
    elif args.port:
        distances = [float(d) for d in args.distances.split(',')]
        test_distance_performance(args.port, args.baudrate, distances, args.tests)
    else:
        parser.print_help()
