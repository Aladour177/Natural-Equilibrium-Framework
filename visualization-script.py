"""
Visualization script for Framework Optimizer results.
Creates detailed plots for comparing framework optimization with gradient descent.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

# Ensure output directory exists
os.makedirs('docs/images', exist_ok=True)

# Rosenbrock function for contour plots
def rosenbrock(x, y):
    return (1 - x)**2 + 100 * (y - x**2)**2

def create_visualizations(fw_history, gd_history):
    """Create visualization plots from optimization results."""
    
    # 1. Convergence Plot
    plt.figure(figsize=(10, 6))
    plt.semilogy(gd_history['loss_history'], 'b-', label='Gradient Descent')
    plt.semilogy(fw_history['loss_history'], 'r-', label='Framework Optimizer')
    
    # Mark pause and anomaly points
    for p in fw_history['pause_points']:
        plt.axvline(p, color='g', linestyle='--', alpha=0.3)
    for a in fw_history['anomaly_points']:
        plt.axvline(a, color='r', linestyle='--', alpha=0.3)
        
    # Add annotations for key events
    for i, p in enumerate(fw_history['pause_points']):
        if i < 3:  # Limit annotations to avoid clutter
            plt.annotate(f'Pause', xy=(p, fw_history['loss_history'][p]),
                      xytext=(p+10, fw_history['loss_history'][p]*2),
                      arrowprops=dict(arrowstyle='->'))
    
    plt.title('Convergence Comparison: Framework vs. Gradient Descent')
    plt.xlabel('Iterations')
    plt.ylabel('Loss (log scale)')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('docs/images/convergence_comparison.png', dpi=300)
    
    # 2. Parameter Trajectory Plot
    plt.figure(figsize=(10, 8))
    
    # Get parameter trajectories
    x_gd = [p[0] for p in gd_history['param_history']]
    y_gd = [p[1] for p in gd_history['param_history']]
    x_fw = [p[0] for p in fw_history['param_history']]
    y_fw = [p[1] for p in fw_history['param_history']]
    
    # Create contour of Rosenbrock function
    x = np.linspace(-1.5, 1.5, 100)
    y = np.linspace(-1, 3, 100)
    X, Y = np.meshgrid(x, y)
    Z = rosenbrock(X, Y)
    
    # Plot contour
    plt.contour(X, Y, Z, levels=np.logspace(-1, 3, 20), cmap='viridis', alpha=0.6)
    plt.colorbar(label='Loss')
    
    # Plot trajectories
    plt.plot(x_gd, y_gd, 'b-', label='Gradient Descent', linewidth=2, alpha=0.7)
    plt.plot(x_fw, y_fw, 'r-', label='Framework Optimizer', linewidth=2, alpha=0.7)
    
    # Mark start and end points
    plt.scatter(x_gd[0], y_gd[0], c='blue', s=100, marker='o', label='GD Start')
    plt.scatter(x_gd[-1], y_gd[-1], c='blue', s=100, marker='X', label='GD End')
    plt.scatter(x_fw[0], y_fw[0], c='red', s=100, marker='o', label='FW Start')
    plt.scatter(x_fw[-1], y_fw[-1], c='red', s=100, marker='X', label='FW End')
    
    # Mark pause points
    for p in fw_history['pause_points']:
        plt.scatter(x_fw[p], y_fw[p], c='green', s=80, marker='s')
    
    # Mark anomaly points
    for a in fw_history['anomaly_points']:
        plt.scatter(x_fw[a], y_fw[a], c='red', s=80, marker='*')
    
    # Mark optimal point
    plt.scatter(1, 1, c='black', s=150, marker='*', label='Optimum (1,1)')
    
    plt.title('Parameter Trajectory: Framework vs. Gradient Descent')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('docs/images/parameter_trajectory.png', dpi=300)
    
    # 3. Health Metrics Visualization
    plt.figure(figsize=(12, 7))
    
    metrics = ['stability', 'diversity', 'resilience', 'balance', 'integration', 'overall']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#000000']
    
    for i, metric in enumerate(metrics):
        if metric == 'overall':
            values = [h[metric] for h in fw_history['health_history']]
            plt.plot(values, color=colors[i], linewidth=3, label=metric)
        else:
            values = [h[metric]['value'] for h in fw_history['health_history']]
            plt.plot(values, color=colors[i], linewidth=2, label=metric)
    
    # Mark pause and anomaly points
    for p in fw_history['pause_points']:
        plt.axvline(p, color='g', linestyle='--', alpha=0.3)
    
    for a in fw_history['anomaly_points']:
        plt.axvline(a, color='r', linestyle='--', alpha=0.3)
        plt.annotate('Anomaly', xy=(a, 0.3), xytext=(a+10, 0.3),
                  arrowprops=dict(arrowstyle='->'))
    
    plt.title('Health Metrics Evolution')
    plt.xlabel('Iterations')
    plt.ylabel('Health Score')
    plt.ylim(0, 1.05)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('docs/images/health_metrics.png', dpi=300)
    
    # 4. 3D Surface Plot with Trajectories
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create surface
    x = np.linspace(-1.5, 1.5, 50)
    y = np.linspace(-0.5, 1.5, 50)
    X, Y = np.meshgrid(x, y)
    Z = rosenbrock(X, Y)
    Z = np.log10(Z + 1)  # Log scale for better visualization
    
    # Plot surface
    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, alpha=0.7, linewidth=0, antialiased=True)
    
    # Calculate Z values for trajectories
    z_gd = [np.log10(rosenbrock(p[0], p[1])+1) for p in gd_history['param_history']]
    z_fw = [np.log10(rosenbrock(p[0], p[1])+1) for p in fw_history['param_history']]
    
    # Plot trajectories
    ax.plot(x_gd, y_gd, z_gd, 'b-', linewidth=2, label='Gradient Descent')
    ax.plot(x_fw, y_fw, z_fw, 'r-', linewidth=2, label='Framework')
    
    # Mark optimal point
    ax.scatter([1], [1], [np.log10(rosenbrock(1, 1)+1)], c='black', s=100, marker='*')
    
    # Customize view
    ax.view_init(elev=30, azim=45)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Log Loss')
    ax.set_title('Rosenbrock Function Surface with Optimization Paths')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig('docs/images/3d_surface.png', dpi=300)
    
    # 5. Bonus: Animated Convergence GIF
    # For GitHub, would need to create frame-by-frame PNGs and convert to GIF
    # This would require additional dependencies like ImageMagick
    # Code not included here, but could be added if requested

    print("Visualizations created in docs/images/")

# Example function to generate placeholder data for testing
def generate_test_data():
    """Generate placeholder data for testing visualizations."""
    # Placeholder data approximating the results in the documentation
    gd_history = {
        'loss_history': np.logspace(-1, -5, 487),
        'param_history': [
            [-1.0, 1.0]  # Starting point
        ] + [
            [(-1.0 + (1.0 - (-1.0)) * i / 486), (1.0 + (0.991 - 1.0) * i / 486)]
            for i in range(1, 487)
        ],
        'grad_history': [np.random.rand(2) for _ in range(487)]
    }
    
    fw_history = {
        'loss_history': np.logspace(-1, -6, 452) * 0.8,  # Slightly better loss
        'param_history': [
            [-1.0, 1.0]  # Starting point
        ] + [
            [(-1.0 + (0.999 - (-1.0)) * i / 451), (1.0 + (0.998 - 1.0) * i / 451)]
            for i in range(1, 452)
        ],
        'grad_history': [np.random.rand(2) for _ in range(452)],
        'pause_points': [50, 120, 200, 300, 400],
        'anomaly_points': [120, 300],
        'health_history': []
    }
    
    # Generate health metrics
    for i in range(452):
        # Base values that generally improve over time
        stability = 0.5 + 0.3 * (i / 451)
        diversity = 0.6 + 0.2 * (i / 451)
        resilience = 0.7 + 0.2 * (i / 451)
        balance = 0.5 + 0.3 * (i / 451)
        integration = 0.4 + 0.4 * (i / 451)
        
        # Add some noise
        stability += np.random.normal(0, 0.05)
        diversity += np.random.normal(0, 0.05)
        resilience += np.random.normal(0, 0.05)
        balance += np.random.normal(0, 0.05)
        integration += np.random.normal(0, 0.05)
        
        # Dips around anomaly points
        if i in range(115, 125):
            diversity = 0.25 + (i - 115) * 0.02  # Diversity dip around 120
        if i in range(295, 305):
            stability = 0.3 + (i - 295) * 0.02  # Stability dip around 300
            
        # Improvement after pauses
        for p in fw_history['pause_points']:
            if i > p and i < p + 10:
                factor = (i - p) / 10
                stability += 0.1 * factor
                diversity += 0.1 * factor
                resilience += 0.1 * factor
                balance += 0.1 * factor
                integration += 0.1 * factor
        
        # Clamp to [0, 1]
        stability = max(0, min(1, stability))
        diversity = max(0, min(1, diversity))
        resilience = max(0, min(1, resilience))
        balance = max(0, min(1, balance))
        integration = max(0, min(1, integration))
        
        # Calculate overall health
        overall = (stability + diversity + resilience + balance + integration) / 5
        
        # Create health entry
        health_entry = {
            'stability': {'value': stability, 'weight': 0.2},
            'diversity': {'value': diversity, 'weight': 0.2},
            'resilience': {'value': resilience, 'weight': 0.2},
            'balance': {'value': balance, 'weight': 0.2},
            'integration': {'value': integration, 'weight': 0.2},
            'overall': overall
        }
        
        fw_history['health_history'].append(health_entry)
    
    return fw_history, gd_history

# Main execution block
if __name__ == "__main__":
    # If running standalone, use test data
    # In a real implementation, this would load actual experiment results
    print("Generating visualizations from test data...")
    fw_history, gd_history = generate_test_data()
    create_visualizations(fw_history, gd_history)
