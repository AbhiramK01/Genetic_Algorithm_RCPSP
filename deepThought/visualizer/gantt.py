"""
based on https://bitbucket.org/DBrent/phd/raw/1d1c5444d2ba2ee3918e0dfd5e886eaeeee49eec/visualisation/plot_gantt.py
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import pylab as pylab
import matplotlib.patches as mpatches


def create_gantt_chart(test_run_data):
    """
    Creates a Gantt chart from the test run data.
    Enhanced with better labels and formatting.
    
    Returns:
        tuple: figure and axes for further customization
    """
    resource_list = determine_top_resources(test_run_data.execution_history, 7)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    
    # Call the plotting function
    plot_gantt(test_run_data, resource_list, ax)
    
    # Enhance the appearance
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Time Units', fontsize=12)
    ax.set_ylabel('Tasks', fontsize=12)
    ax.set_title('Project Schedule Gantt Chart', fontsize=14)
    
    # Add a legend explaining the resources
    legend_labels = []
    legend_handles = []
    
    for resource, color in resource_list:
        patch = mpatches.Patch(color=color, label=f"{resource[0].name}")
        legend_handles.append(patch)
        legend_labels.append(f"{resource[0].name}")
    
    ax.legend(handles=legend_handles, labels=legend_labels, 
             title="Resources (colors)", loc='center right')
    
    return fig, ax

def determine_top_resources(execution_history, n=7):
    """
    Determines the most frequently used resources and assigns colors.
    
    Args:
        execution_history: The execution history from test run data
        n: Number of top resources to return
        
    Returns:
        list: Tuples of (resource, color) for the top n resources
    """
    resource_frequency = {}
    for task in execution_history:
        for resource in task.usedResources:
            if resource.max_share_count != 0:
                if resource not in resource_frequency:
                    resource_frequency[resource] = 0
                resource_frequency[resource] += 1
    
    top_resources = []
    for resource, frequency in list(resource_frequency.items()):
        top_resources.append(((resource, frequency), None))  # Will assign color later
    
    top_resources.sort(key=lambda tup: tup[0][1], reverse=True)
    top_resources = top_resources[:n]
    
    # Print resource information to console
    print("\nTOP RESOURCES USED IN SCHEDULE:")
    for i, ((resource, frequency), _) in enumerate(top_resources):
        print(f"  {i+1}. {resource.name}: Used {frequency} times")
    
    # Assign colors to resources using a colorful palette
    colors = ['#ff1493', '#32cd32', '#1e90ff', '#ff8c00', '#9370db', '#20b2aa', '#ff6347', 
              '#ffd700', '#3cb371', '#87cefa', '#f08080', '#7b68ee', '#00fa9a', '#ffa07a']
    
    for i, ((resource, frequency), _) in enumerate(top_resources):
        color = colors[i % len(colors)]
        top_resources[i] = ((resource, frequency), color)
    
    return top_resources

def plot_gantt(simulation_result, top_resources, ax=None):
    """
    Plots a Gantt chart of the simulation result.
    Enhanced with clearer task labels and resource coloring.
    
    Args:
        simulation_result: The simulation result data
        top_resources: List of (resource, color) tuples
        ax: Matplotlib axes to plot on (optional)
        
    Returns:
        The matplotlib axes with the Gantt chart
    """
    if ax is None:
        ax = plt.gca()
    
    # Extract resource colors from top_resources
    resource_colors = {}
    for (resource, _), color in top_resources:
        resource_colors[resource] = color
    
    # Determine task label width based on the number of tasks
    num_tasks = len(simulation_result.execution_history)
    task_label_width = 30 if num_tasks < 30 else 15  # Adjust label length based on task count
    
    # Sort tasks by start time
    sorted_tasks = sorted(simulation_result.execution_history, key=lambda x: x.startTime)
    
    # Plot each task
    for i, task in enumerate(sorted_tasks):
        start = task.startTime
        duration = task.executionTime
        
        # Format the task label to include useful information
        task_name = task.name
        if len(task_name) > task_label_width:
            task_name = task_name[:task_label_width-3] + "..."
        
        # Determine the color based on the resource
        color = 'gray'  # Default color
        for resource in task.usedResources:
            if resource in resource_colors:
                color = resource_colors[resource]
                break
        
        # Plot the task bar
        ax.barh(i, duration, left=start, height=0.8, color=color, alpha=0.8, 
               edgecolor='black', linewidth=0.5)
        
        # Add task labels
        ax.text(start + 0.1, i, task_name, va='center', fontsize=8, weight='bold')
        
        # Add duration info if there's enough space
        if duration > 5:
            ax.text(start + duration/2, i, f"{duration:.1f}", 
                   ha='center', va='center', fontsize=7, color='black',
                   bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.1'))
    
    # Set y-ticks with task numbers
    ax.set_yticks(range(len(sorted_tasks)))
    ax.set_yticklabels([f"Task {i+1}" for i in range(len(sorted_tasks))])
    
    # Add vertical lines to mark time intervals
    max_time = simulation_result.total_time
    interval = max(1, int(max_time / 10))  # Ensure at least 10 intervals if possible
    
    for t in range(0, int(max_time) + interval, interval):
        ax.axvline(x=t, color='gray', linestyle='--', alpha=0.3)
    
    # Adjust axes limits
    ax.set_xlim(0, max_time * 1.05)  # Add a small margin
    ax.set_ylim(-1, len(sorted_tasks))
    
    return ax





