"""
Natural Equilibrium Framework Optimizer - Optimization Steps

Contains functions for taking optimization steps, integrating learnings, etc.
"""

import numpy as np
from nef_optimizer_detection import detect_plateau, detect_oscillation, detect_anomalies

def inject_diversity(params, scale=0.05):
    """
    Add small random perturbation to introduce diversity.
    
    Args:
        params: Current parameters
        scale: Scale of perturbation
        
    Returns:
        New parameters with added diversity
    """
    perturbation = [scale * (np.random.random() - 0.5) for _ in range(len(params))]
    return [p + d for p, d in zip(params, perturbation)]


def handle_anomaly(params, anomalies):
    """
    Respond to detected anomalies.
    
    Args:
        params: Current parameters
        anomalies: List of detected anomalies
        
    Returns:
        Adjusted parameters
    """
    # Handle worst anomaly first
    worst = max(anomalies, key=lambda a: a['severity'])
    
    if worst['metric'] == 'stability' and worst['value'] < 0.3:
        # Dampen unstable params
        return [p * 0.95 for p in params]
    elif worst['metric'] == 'diversity' and worst['value'] < 0.3:
        # Add diversity
        return inject_diversity(params, scale=0.1)
    elif worst['metric'] == 'resilience' and worst['value'] < 0.3:
        # Move toward average of recent history
        # This would require recent history, which we don't have here
        return inject_diversity(params, scale=0.02)  # Small perturbation as fallback
    
    # Default: small diversity injection
    return inject_diversity(params, scale=0.01)


def integrate_learnings(params, loss_history, grad_history, health_metrics, params_history):
    """
    Integrate learnings during pause phase.
    
    Args:
        params: Current parameters
        loss_history: List of loss values over time
        grad_history: List of gradient values over time
        health_metrics: Dict of health metrics
        params_history: List of parameter values over time
        
    Returns:
        New parameters after integration
    """
    # Analyze trajectory
    is_plateau = detect_plateau(loss_history)
    is_oscillating = detect_oscillation(grad_history)
    anomalies = detect_anomalies(health_metrics)
    
    # Handle anomalies first
    if anomalies:
        return handle_anomaly(params, anomalies)
    elif is_plateau and is_oscillating:
        # Likely at saddle point - larger perturbation
        return inject_diversity(params, scale=0.1)
    elif is_plateau:
        # Likely at local minimum - small perturbation
        return inject_diversity(params, scale=0.05)
    elif is_oscillating:
        # Likely overshooting - reduce effective learning rate
        # Return average of recent parameters
        window = min(5, len(params_history))
        avg_params = np.mean(params_history[-window:], axis=0)
        return list(avg_params)
    
    # Default - small diversity injection
    return inject_diversity(params, scale=0.01)


def framework_step(params, loss_history, grad_history, health_metrics, params_history, lr=0.01, grad_fn=None):
    """
    Perform one step of framework-inspired optimization.
    
    Args:
        params: Current parameters
        loss_history: List of loss values over time
        grad_history: List of gradient values over time
        health_metrics: Dict of health metrics
        params_history: List of parameter values over time
        lr: Learning rate
        grad_fn: Function to calculate gradient
        
    Returns:
        New parameters after one optimization step
    """
    # Check if we should pause for integration
    from nef_optimizer_detection import should_pause
    
    if should_pause(loss_history, grad_history, health_metrics['overall']):
        # Integration phase
        return integrate_learnings(params, loss_history, grad_history, health_metrics, params_history)
    
    # Normal step, but modulated by health
    if grad_fn:
        # If gradient function provided, use it
        grad = grad_fn(params)
        # Modulate learning rate by health
        adjusted_lr = lr * max(health_metrics['overall'], 0.1)  # Minimum of 10% learning rate
        return [p - adjusted_lr * g for p, g in zip(params, grad)]
    else:
        # If no gradient function, use last gradient from history
        if grad_history:
            last_grad = grad_history[-1]
            adjusted_lr = lr * max(health_metrics['overall'], 0.1)
            return [p - adjusted_lr * g for p, g in zip(params, last_grad)]
        else:
            # No gradient available, do small random step
            return inject_diversity(params, scale=0.01)