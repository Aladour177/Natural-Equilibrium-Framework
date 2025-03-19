"""
Natural Equilibrium Framework Optimizer - Base Module

Contains the core optimizer implementation and health metric calculations.
"""

import numpy as np
import matplotlib.pyplot as plt
import time
from collections import deque

class HealthMetaLearner:
    """Manages health metric weights throughout optimization."""
    
    def __init__(self):
        self.default_weights = {
            'stability': 0.2, 'diversity': 0.2, 'resilience': 0.2, 
            'balance': 0.2, 'integration': 0.2
        }
    
    def get_weights(self, epoch, system_state):
        """
        Return health metric weights appropriate for the current training stage.
        """
        # Early training: favor stability and diversity
        if epoch < 100:
            return {
                'stability': 0.35, 'diversity': 0.25, 'resilience': 0.15,
                'balance': 0.15, 'integration': 0.10
            }
        # Middle training: shift toward balance
        elif 100 <= epoch < 500:
            return {
                'stability': 0.20, 'diversity': 0.20, 'resilience': 0.20,
                'balance': 0.30, 'integration': 0.10
            }
        # Late training: prioritize integration and balance
        else:
            return {
                'stability': 0.15, 'diversity': 0.15, 'resilience': 0.20,
                'balance': 0.25, 'integration': 0.25
            }

def compute_health_factor(stability, diversity, resilience, balance, integration, meta_learner=None, epoch=None, system_state=None):
    """
    Compute overall health factor from individual metrics.
    """
    # Get weights either from meta_learner or use defaults
    if meta_learner and epoch is not None and system_state is not None:
        weights = meta_learner.get_weights(epoch, system_state)
    else:
        weights = {
            'stability': 0.2, 'diversity': 0.2, 'resilience': 0.2, 
            'balance': 0.2, 'integration': 0.2
        }
    
    # Compute weighted health factor
    health = (
        weights['stability'] * stability +
        weights['diversity'] * diversity +
        weights['resilience'] * resilience +
        weights['balance'] * balance +
        weights['integration'] * integration
    )
    
    # Record the health calculation details
    health_details = {
        'stability': {'value': stability, 'weight': weights['stability']},
        'diversity': {'value': diversity, 'weight': weights['diversity']},
        'resilience': {'value': resilience, 'weight': weights['resilience']},
        'balance': {'value': balance, 'weight': weights['balance']},
        'integration': {'value': integration, 'weight': weights['integration']},
        'overall': health
    }
    
    return health, health_details

class FrameworkOptimizer:
    """Framework-inspired optimizer implementing NEF principles."""
    
    def __init__(self, lr=0.01, max_iterations=1000):
        from nef_optimizer_metrics import calc_stability, calc_diversity, calc_resilience, calc_balance, calc_integration
        from nef_optimizer_detection import detect_anomalies, should_pause
        
        self.lr = lr
        self.max_iterations = max_iterations
        self.meta_learner = HealthMetaLearner()
        
        # Import functions from other modules
        self.calc_stability = calc_stability
        self.calc_diversity = calc_diversity
        self.calc_resilience = calc_resilience
        self.calc_balance = calc_balance
        self.calc_integration = calc_integration
        self.detect_anomalies = detect_anomalies
        self.should_pause = should_pause
        
        self.reset()
    
    def reset(self):
        """Reset optimizer state."""
        self.params_history = []
        self.loss_history = []
        self.grad_history = []
        self.health_history = []
        self.pause_points = []
        self.anomaly_points = []
    
    def minimize(self, loss_fn, grad_fn, initial_params, objectives=None):
        """
        Minimize a loss function using framework-inspired optimization.
        """
        from nef_optimizer_steps import framework_step
        
        self.reset()
        params = initial_params.copy()
        self.params_history = [params.copy()]
        
        if objectives is None:
            objectives = {'main': loss_fn}
        
        for i in range(self.max_iterations):
            # Calculate loss and gradient
            loss = loss_fn(params)
            self.loss_history.append(loss)
            
            grad = grad_fn(params)
            self.grad_history.append(grad)
            
            # Calculate health metrics
            stability = self.calc_stability(self.params_history)
            diversity = self.calc_diversity(self.grad_history)
            resilience = self.calc_resilience(self.loss_history)
            balance = self.calc_balance(objectives, params, self.params_history)
            integration = self.calc_integration(params, self.params_history)
            
            # Get overall health
            health, health_details = compute_health_factor(
                stability, diversity, resilience, balance, integration,
                self.meta_learner, i, {'loss': loss}
            )
            self.health_history.append(health_details)
            
            # Check for pauses and anomalies
            should_pause_now = self.should_pause(self.loss_history, self.grad_history, health)
            anomalies = self.detect_anomalies(health_details)
            
            if should_pause_now:
                self.pause_points.append(i)
                if anomalies:
                    self.anomaly_points.append(i)
            
            # Framework step
            params = framework_step(
                params, 
                self.loss_history, 
                self.grad_history, 
                health_details, 
                self.params_history, 
                self.lr,
                grad_fn
            )
            self.params_history.append(params.copy())
            
            # Check for convergence
            if loss < 1e-6:
                break
        
        history = {
            'loss_history': self.loss_history,
            'param_history': self.params_history,
            'grad_history': self.grad_history,
            'health_history': self.health_history,
            'pause_points': self.pause_points,
            'anomaly_points': self.anomaly_points
        }
        
        return params, history
    
    def compare_with_gd(self, loss_fn, grad_fn, initial_params, objectives=None, plot=True):
        """
        Compare framework optimizer with traditional gradient descent.
        """
        # Run framework optimization
        fw_start = time.time()
        fw_result, fw_history = self.minimize(loss_fn, grad_fn, initial_params, objectives)
        fw_time = time.time() - fw_start
        
        # Run standard gradient descent
        gd_start = time.time()
        gd_result, gd_history = self._run_gd(loss_fn, grad_fn, initial_params)
        gd_time = time.time() - gd_start
        
        # Prepare comparison metrics
        comparison = {
            'gd': {
                'result': gd_result,
                'loss_history': gd_history['loss_history'],
                'iterations': len(gd_history['loss_history']),
                'time': gd_time
            },
            'framework': {
                'result': fw_result,
                'loss_history': fw_history['loss_history'],
                'iterations': len(fw_history['loss_history']),
                'time': fw_time,
                'health_history': fw_history['health_history'],
                'pause_points': fw_history['pause_points'],
                'anomaly_points': fw_history['anomaly_points']
            },
            'comparison': {
                'loss_ratio': gd_history['loss_history'][-1] / fw_history['loss_history'][-1] 
                              if fw_history['loss_history'][-1] > 0 else float('inf'),
                'iteration_ratio': len(gd_history['loss_history']) / len(fw_history['loss_history']),
                'time_ratio': gd_time / fw_time
            }
        }
        
        # Print summary
        print("\nResults:")
        print(f"GD Solution: {gd_result}, Final Loss: {gd_history['loss_history'][-1]}, Iterations: {len(gd_history['loss_history'])}, Time: {gd_time:.4f}s")
        print(f"Framework Solution: {fw_result}, Final Loss: {fw_history['loss_history'][-1]}, Iterations: {len(fw_history['loss_history'])}, Time: {fw_time:.4f}s")
        print(f"Pauses: {len(fw_history['pause_points'])}, Anomalies: {len(fw_history['anomaly_points'])}")
        
        print("\nPerformance Summary:")
        print(f"Loss improvement: {comparison['comparison']['loss_ratio']:.2f}x")
        print(f"Iteration efficiency: {comparison['comparison']['iteration_ratio']:.2f}x")
        print(f"Time efficiency: {comparison['comparison']['time_ratio']:.2f}x")
        
        # Plot comparison if requested
        if plot:
            self._plot_comparison(gd_history, fw_history, gd_result, fw_result)
        
        return comparison
    
    def _run_gd(self, loss_fn, grad_fn, initial_params):
        """Run standard gradient descent."""
        params = initial_params.copy()
        loss_history = []
        param_history = [params.copy()]
        grad_history = []
        
        for i in range(self.max_iterations):
            loss = loss_fn(params)
            loss_history.append(loss)
            
            grad = grad_fn(params)
            grad_history.append(grad)
            
            # Standard GD update
            params = [p - self.lr * g for p, g in zip(params, grad)]
            param_history.append(params.copy())
            
            if loss < 1e-6:  # Convergence check
                break
        
        history = {
            'loss_history': loss_history,
            'param_history': param_history,
            'grad_history': grad_history
        }
        
        return params, history
    
    def _plot_comparison(self, gd_history, fw_history, gd_result, fw_result):
        """Plot comparison between GD and Framework optimization."""
        plt.figure(figsize=(15, 10))
        
        # Loss comparison
        plt.subplot(2, 2, 1)
        plt.semilogy(gd_history['loss_history'], label='GD')
        plt.semilogy(fw_history['loss_history'], label='Framework')
        
        # Mark pause and anomaly points
        for p in fw_history['pause_points']:
            plt.axvline(p, color='g', linestyle='--', alpha=0.3)
        for a in fw_history['anomaly_points']:
            plt.axvline(a, color='r', linestyle='--', alpha=0.3)
            
        plt.title('Loss Comparison')
        plt.xlabel('Iterations')
        plt.ylabel('Loss (log scale)')
        plt.legend()
        
        # Parameter trajectory (if 2D)
        if len(gd_result) == 2:
            plt.subplot(2, 2, 2)
            x_gd = [p[0] for p in gd_history['param_history']]
            y_gd = [p[1] for p in gd_history['param_history']]
            plt.plot(x_gd, y_gd, 'b-', label='GD')
            
            x_fw = [p[0] for p in fw_history['param_history']]
            y_fw = [p[1] for p in fw_history['param_history']]
            plt.plot(x_fw, y_fw, 'r-', label='Framework')
            
            plt.title('Parameter Trajectory')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.legend()
        
        # Health metrics
        plt.subplot(2, 2, 3)
        for metric in ['stability', 'diversity', 'resilience', 'balance', 'integration', 'overall']:
            if metric == 'overall':
                values = [h[metric] for h in fw_history['health_history']]
            else:
                values = [h[metric]['value'] for h in fw_history['health_history']]
            plt.plot(values, label=metric)
            
        plt.title('Framework Health Metrics')
        plt.xlabel('Iterations')
        plt.ylabel('Health Score')
        plt.legend()
        
        # Framework events
        plt.subplot(2, 2, 4)
        plt.plot(fw_history['loss_history'], label='Framework Loss')
        for p in fw_history['pause_points']:
            plt.scatter(p, fw_history['loss_history'][p], color='g', marker='o', 
                      label='Pause' if p == fw_history['pause_points'][0] else "")
        for a in fw_history['anomaly_points']:
            plt.scatter(a, fw_history['loss_history'][a], color='r', marker='x', 
                      label='Anomaly' if a == fw_history['anomaly_points'][0] else "")
            
        plt.title('Framework Events')
        plt.xlabel('Iterations')
        plt.ylabel('Loss')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('optimization_comparison.png')
        plt.show()
