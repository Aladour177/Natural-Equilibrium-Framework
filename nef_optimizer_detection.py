"""
Natural Equilibrium Framework Optimizer - Detection Functions

Contains functions for detecting plateaus, oscillations, anomalies, etc.
"""

import numpy as np

def detect_plateau(loss_history, window=10, threshold=0.001):
    """
    Detect plateaus in the loss function.
    
    Args:
        loss_history: List of loss values over time
        window: Number of recent updates to consider
        threshold: Relative change threshold to consider a plateau
        
    Returns:
        Boolean indicating whether a plateau was detected
    """
    if len(loss_history) < window:
        return False
    
    recent_losses = loss_history[-window:]
    max_loss = max(recent_losses)
    min_loss = min(recent_losses)
    
    # If the range is small relative to the average loss, consider it a plateau
    avg_loss = np.mean(recent_losses)
    return (max_loss - min_loss) / (avg_loss + 1e-10) < threshold


def detect_oscillation(grad_history, threshold=0.15, window=10):
    """
    Detect oscillations in the gradient.
    
    Args:
        grad_history: List of gradient values over time
        threshold: Threshold for sign flip ratio to detect oscillation
        window: Number of recent updates to consider
        
    Returns:
        Boolean indicating whether oscillation was detected
    """
    if len(grad_history) < window:
        return False
    
    # Check for sign flips in gradient components
    recent_grads = grad_history[-window:]
    sign_flips = 0
    total_components = 0
    
    for i in range(len(recent_grads[0])):
        grads = [g[i] for g in recent_grads]
        for j in range(1, len(grads)):
            if grads[j] * grads[j-1] < 0:
                sign_flips += 1
            total_components += 1
    
    flip_ratio = sign_flips / total_components if total_components > 0 else 0
    return flip_ratio > threshold


def detect_anomalies(health_details, threshold=0.2):
    """
    Detect anomalies in health metrics.
    
    Args:
        health_details: Dict of health metric details
        threshold: Threshold for detecting significant deviations
        
    Returns:
        List of detected anomalies
    """
    anomalies = []
    for metric, data in health_details.items():
        if metric != 'overall' and isinstance(data, dict) and 'value' in data:
            # Check for very low values (potential problems)
            if data['value'] < 0.3:
                anomalies.append({
                    'metric': metric, 
                    'value': data['value'], 
                    'severity': 1.0 - data['value']
                })
    return anomalies


def should_pause(loss_history, grad_history, health):
    """
    Determine whether to pause for integration.
    
    Args:
        loss_history: List of loss values over time
        grad_history: List of gradient values over time
        health: Overall health score
        
    Returns:
        Boolean indicating whether to pause
    """
    return (detect_plateau(loss_history, window=10, threshold=0.001) or 
            detect_oscillation(grad_history, threshold=0.15) or 
            health < 0.45)