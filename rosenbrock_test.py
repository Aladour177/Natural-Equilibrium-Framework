"""
Example using the Framework Optimizer on Rosenbrock function.

This demonstrates how the Natural Equilibrium Framework optimizer
outperforms traditional gradient descent on a challenging function.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add parent directory to path to import optimizer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nef_optimizer_base import FrameworkOptimizer

# Rosenbrock function (banana-shaped valley)
def rosenbrock(params):
    """Rosenbrock function (banana-shaped valley)."""
    x, y = params
    return (1 - x)**2 + 100 * (y - x**2)**2

def rosenbrock_grad(params):
    """Gradient of the Rosenbrock function."""
    x, y = params
    dx = -2 * (1 - x) - 400 * x * (y - x**2)
    dy = 200 * (y - x**2)
    return [dx, dy]

def run_comparison():
    """Compare framework optimizer with traditional gradient descent."""
    # Use a challenging starting point
    starting_point = [-1.0, 1.0]
    
    # Create the optimizer
    optimizer = FrameworkOptimizer(lr=0.01, max_iterations=500)
    
    # Run comparison
    results = optimizer.compare_with_gd(
        loss_fn=rosenbrock,
        grad_fn=rosenbrock_grad,
        initial_params=starting_point,
        plot=True
    )
    
    return results

if __name__ == "__main__":
    print("Running Rosenbrock Test...")
    results = run_comparison()
    
    # Print detailed analysis
    print("\nDetailed Analysis:")
    print("GD Final Parameters:", results['gd']['result'])
    print("Framework Final Parameters:", results['framework']['result'])
    
    print("\nHealth Factor Analysis:")
    final_health = results['framework']['health_history'][-1]
    for metric in ['stability', 'diversity', 'resilience', 'balance', 'integration']:
        print(f"- {metric.capitalize()}: {final_health[metric]['value']:.2f}")
    
    print("\nPause Analysis:")
    pause_points = results['framework']['pause_points']
    print(f"Total pauses: {len(pause_points)}")
    if pause_points:
        pause_indices = ", ".join(str(p) for p in pause_points[:5])
        pause_indices += "..." if len(pause_points) > 5 else ""
        print(f"Pause points: {pause_indices}")
    
    print("\nAnomaly Analysis:")
    anomaly_points = results['framework']['anomaly_points']
    print(f"Total anomalies: {len(anomaly_points)}")
    if anomaly_points:
        anomaly_indices = ", ".join(str(a) for a in anomaly_points)
        print(f"Anomaly points: {anomaly_indices}")
    
    print("\nConclusion:")
    loss_ratio = results['comparison']['loss_ratio']
    iter_ratio = results['comparison']['iteration_ratio']
    time_ratio = results['comparison']['time_ratio']
    
    print(f"The framework approach achieved:")
    print(f"- {loss_ratio:.2f}x lower final loss")
    print(f"- {iter_ratio:.2f}x {'fewer' if iter_ratio > 1 else 'more'} iterations")
    print(f"- {time_ratio:.2f}x {'faster' if time_ratio > 1 else 'slower'} execution time")
    
    if loss_ratio > 1 and iter_ratio > 1:
        print("\nVerdict: Framework optimizer significantly outperformed gradient descent!")
    elif loss_ratio > 1:
        print("\nVerdict: Framework optimizer achieved better results but took more resources!")
    else:
        print("\nVerdict: Mixed results - framework has room for improvement!")