import pandas as pd
import numpy as np
import json
import argparse
from sklearn.metrics import accuracy_score, confusion_matrix

def evaluate_window_performance(results_file, ground_truth_file):
    """
    Evaluate model performance with different window sizes and strides
    
    Args:
        results_file: JSON file with model outputs for different configurations
        ground_truth_file: CSV file with ground truth labels
    """
    # Load data
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    ground_truth = pd.read_csv(ground_truth_file)
    
    print("Window Size and Stride Evaluation Results:")
    print("=" * 60)
    print(f"{'Window':^10}|{'Stride':^10}|{'Acc (%)':^10}|{'FPR (%)':^10}|{'FNR (%)':^10}|{'Throughput':^12}")
    print("-" * 60)
    
    # Process each configuration
    for config in results:
        window_ms = config['window_ms']
        stride_ms = config['stride_ms']
        predictions = np.array(config['predictions'])
        true_labels = ground_truth['label'].values[:len(predictions)]
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, predictions) * 100
        tn, fp, fn, tp = confusion_matrix(true_labels, predictions, labels=[0, 1]).ravel()
        
        # False positive and negative rates
        fpr = fp / (fp + tn) * 100 if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) * 100 if (fn + tp) > 0 else 0
        
        # Calculate throughput
        throughput = 1000 / stride_ms
        
        print(f"{window_ms:^10}|{stride_ms:^10}|{accuracy:^10.1f}|{fpr:^10.1f}|{fnr:^10.1f}|{throughput:^12.1f} Hz")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate window size and stride performance")
    parser.add_argument("--results", required=True, help="JSON file with model results")
    parser.add_argument("--ground-truth", required=True, help="CSV file with ground truth labels")
    
    args = parser.parse_args()
    evaluate_window_performance(args.results, args.ground_truth)
