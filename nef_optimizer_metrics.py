"""
Natural Equilibrium Framework Optimizer - Health Metrics

Contains the functions to calculate health metrics for the optimizer.
"""

import numpy as np

def calc_stability(params_history, window=10):
    """
    Measure parameter stability over recent updates.
    
    Args:
        params_history: List of parameter values over time
        window: Number of recent updates to consider
        
    Returns:
        Stability score (0-1)
    """
    if len(params_history) < window:
        return 1.0  # Assume stable at start
    
    # Calculate variance in each parameter over window
    recent_params = params_history[-window:]
    param_variances = []
    
    # Transpose to get list of values for each parameter
    for i in range(len(recent_params[0])):
        values = [p[i] for p in recent_params]
        param_variances.append(np.var(values))
    
    # Normalize variances and convert to stability score (1 - normalized_variance)
    avg_variance = np.mean(param_variances)
    stability = 1.0 / (1.0 + 10.0 * avg_variance)  # Scale factor of 10 to make it sensitive
    
    return min(max(stability, 0.0), 1.0)  # Clamp to [0,1]


def calc_diversity(grad_history, window=10):
    """
    Measure gradient diversity to detect dimensional collapse.
    
    Args:
        grad_history: List of gradient values over time
        window: Number of recent updates to consider
        
    Returns:
        Diversity score (0-1)
    """
    if len(grad_history) < window:
        return 1.0  # Assume diverse at start
    
    # Calculate the average direction of recent gradients
    recent_grads = grad_history[-window:]
    
    # Normalize each gradient
    normalized_grads = []
    for grad in recent_grads:
        norm = np.sqrt(sum(g**2 for g in grad))
        if norm > 1e-10:  # Avoid division by zero
            normalized_grads.append([g/norm for g in grad])
        else:
            normalized_grads.append(grad)
    
    # Calculate average direction
    avg_direction = np.mean(normalized_grads, axis=0)
    avg_norm = max(np.sqrt(sum(d**2 for d in avg_direction)), 1e-10)
    
    # If directions are diverse, avg_norm will be small
    # If all pointing same way, avg_norm will be close to 1
    diversity = 1.0 - min(avg_norm, 1.0)
    
    return diversity


def calc_resilience(loss_history, perturbation_tests=None, window=10):
    """
    Measure system's ability to recover from perturbations.
    
    Args:
        loss_history: List of loss values over time
        perturbation_tests: Optional results from explicit perturbation tests
        window: Number of recent updates to consider
        
    Returns:
        Resilience score (0-1)
    """
    if perturbation_tests:
        # If we have explicit perturbation tests, use those
        return perturbation_tests['recovery_score']
    
    # Otherwise, estimate from loss history
    if len(loss_history) < window:
        return 1.0  # Assume resilient at start
    
    # Look for recovery patterns in loss
    recoveries = []
    for i in range(len(loss_history) - window, len(loss_history) - 1):
        if loss_history[i] > loss_history[i-1] and loss_history[i+1] < loss_history[i]:
            # Found a spike that recovered
            recovery_ratio = (loss_history[i] - loss_history[i+1]) / (loss_history[i] - loss_history[i-1])
            recoveries.append(recovery_ratio)
    
    if not recoveries:
        # No recovery events detected
        return 0.8  # Assume moderately resilient
    
    resilience = min(1.0, np.mean(recoveries))
    return resilience


def calc_balance(objectives, params, params_history, window=10):
    """
    Measure balance between competing objectives.
    
    Args:
        objectives: Dict of objective functions
        params: Current parameters
        params_history: List of parameter values over time
        window: Number of recent updates to consider
        
    Returns:
        Balance score (0-1)
    """
    # If only one objective (e.g., Rosenbrock), return perfect balance
    if len(objectives) <= 1:
        return 1.0
        
    if len(params_history) < window:
        return 0.5  # Neutral balance at start
    
    # Calculate current values for each objective
    current_values = {name: obj_fn(params) for name, obj_fn in objectives.items()}
    
    # Calculate how each objective has changed over window
    previous_values = {name: obj_fn(params_history[-window]) for name, obj_fn in objectives.items()}
    changes = {name: (current - previous_values[name])/max(abs(previous_values[name]), 1e-10) 
              for name, current in current_values.items()}
    
    # Calculate standard deviation of changes - lower means more balanced
    change_stddev = np.std(list(changes.values()))
    
    # Convert to balance score (1 for perfect balance, 0 for completely imbalanced)
    balance = 1.0 / (1.0 + 5.0 * change_stddev)  # Scale factor of 5 for sensitivity
    
    return balance


def calc_integration(params, params_history, window=20):
    """
    Measure how well new updates integrate with existing knowledge.
    
    Args:
        params: Current parameters
        params_history: List of parameter values over time
        window: Number of recent updates to consider
        
    Returns:
        Integration score (0-1)
    """
    if len(params_history) < window:
        return 0.5  # Neutral integration at start
    
    # Calculate how smoothly parameters have evolved
    # Abrupt changes suggest poor integration
    param_trajectories = []
    for i in range(len(params)):
        values = [p[i] for p in params_history[-window:]]
        
        # Make sure we have enough values for second derivative
        if len(values) < 3:
            return 0.5
            
        # Calculate smoothness as inverse of second derivative magnitude
        seconds = [abs(values[j+2] - 2*values[j+1] + values[j]) for j in range(len(values)-2)]
        if seconds:
            avg_second = np.mean(seconds)
            param_trajectories.append(1.0 / (1.0 + 10.0 * avg_second))  # Scale factor for sensitivity
    
    integration = np.mean(param_trajectories) if param_trajectories else 0.5
    return min(max(integration, 0.0), 1.0)  # Clamp to [0,1]