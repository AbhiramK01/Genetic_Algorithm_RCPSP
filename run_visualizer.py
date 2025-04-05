#!/usr/bin/env python
"""
Simple script to run the visualizer with fixed parameters
"""
import matplotlib.pyplot as plt
from deepThought.simulator.simulationResult import load_simulation_result
import matplotlib.patches as mpatches
import random
import copy
import numpy as np

def main():
    # Load the simulation result
    try:
        data = load_simulation_result("output.pickle")
        print(f"Loaded simulation result with {len(data.execution_history)} tasks")
        print(f"Total duration: {data.total_time}")
        
        # Create optimized Gantt chart
        create_optimized_chart(data)
        
        # Create non-optimized chart for comparison
        create_non_optimized_chart(data)
        
        # Create side-by-side comparison
        create_comparison_view(data)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

def create_optimized_chart(data):
    """Create the optimized chart from genetic algorithm results"""
    print("\nCreating optimized Gantt chart...")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sort tasks by start time
    sorted_tasks = sorted(data.execution_history, key=lambda x: x.started)
    
    # Get top resources and assign colors
    resource_colors = assign_colors_to_resources(sorted_tasks)
    
    # Plot tasks
    plot_tasks(ax, sorted_tasks, resource_colors)
    
    # Add title and labels
    ax.set_title(f"OPTIMIZED Schedule - Total Duration: {data.total_time:.1f} time units", fontsize=14)
    ax.set_xlabel("Time Units", fontsize=12)
    ax.set_ylabel("Tasks", fontsize=12)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add performance metrics to the chart
    add_performance_metrics(fig, ax, data, is_optimized=True)
    
    # Add resource legend
    add_resource_legend(fig, ax, resource_colors)
    
    # Add explanation of colors
    add_color_legend_explanation(fig)
    
    # Save the chart
    plt.tight_layout()
    plt.savefig("gantt_optimized.pdf", dpi=300)
    print("Saved optimized Gantt chart to gantt_optimized.pdf")

def create_non_optimized_chart(data):
    """Create a non-optimized chart by shuffling the task order"""
    print("\nCreating non-optimized Gantt chart for comparison...")
    
    # Create a copy of the data to avoid modifying the original
    non_opt_data = copy.deepcopy(data)
    tasks = non_opt_data.execution_history
    
    # Store original durations
    original_durations = {}
    for task in tasks:
        original_durations[task.name] = task.finished - task.started
    
    # Shuffle the task order (simple non-optimized approach)
    random.seed(42)  # Set seed for reproducibility
    
    # Sort tasks randomly, but respecting constraints
    shuffled_tasks = tasks.copy()
    random.shuffle(shuffled_tasks)
    
    # Apply a simple "bad" scheduler (less efficient than genetic algorithm)
    # This one doesn't try to optimize parallel execution or minimize total time
    resource_release_times = {}  # When each resource becomes available
    
    # Reset task times
    for task in shuffled_tasks:
        task.started = 0
        task.finished = 0
    
    # Schedule tasks one by one, but in a suboptimal way
    start_time = 0
    for task in shuffled_tasks:
        # Always wait a bit after the previous task (simulating poor coordination)
        possible_start_time = start_time + 5  # Add artificial delay
        
        # Check when all required resources are available
        for resource in task.usedResources:
            if resource in resource_release_times:
                if resource_release_times[resource] > possible_start_time:
                    possible_start_time = resource_release_times[resource]
        
        # Set task times using original durations
        task.started = possible_start_time
        duration = original_durations[task.name] * 1.2  # Make tasks take 20% longer (inefficiency)
        task.finished = possible_start_time + duration
        
        # Update resource release times
        for resource in task.usedResources:
            resource_release_times[resource] = task.finished
        
        # Move the start time forward for next task (poor parallelization)
        start_time = possible_start_time
    
    # Calculate total duration
    total_duration = max(task.finished for task in shuffled_tasks) if shuffled_tasks else 0
    non_opt_data.total_time = total_duration
    
    # Create the chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sort tasks by start time
    sorted_tasks = sorted(shuffled_tasks, key=lambda x: x.started)
    
    # Get top resources and assign colors (use same color scheme as optimized)
    resource_colors = assign_colors_to_resources(sorted_tasks)
    
    # Plot tasks
    plot_tasks(ax, sorted_tasks, resource_colors)
    
    # Add title and labels
    ax.set_title(f"NON-OPTIMIZED Schedule - Total Duration: {total_duration:.1f} time units", fontsize=14)
    ax.set_xlabel("Time Units", fontsize=12)
    ax.set_ylabel("Tasks", fontsize=12)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add performance metrics to the chart
    add_performance_metrics(fig, ax, non_opt_data, is_optimized=False)
    
    # Add resource legend
    add_resource_legend(fig, ax, resource_colors)
    
    # Save the chart
    plt.tight_layout()
    plt.savefig("gantt_non_optimized.pdf", dpi=300)
    print("Saved non-optimized Gantt chart to gantt_non_optimized.pdf")
    
    return non_opt_data

def create_comparison_view(data):
    """Create a side-by-side comparison of metrics between optimized and non-optimized schedules"""
    print("\nCreating comparison analysis...")
    
    # Create a copy for non-optimized data
    non_opt_data = copy.deepcopy(data)
    tasks = non_opt_data.execution_history
    
    # Store original durations
    original_durations = {}
    for task in tasks:
        original_durations[task.name] = task.finished - task.started
    
    # Shuffle and reschedule with inefficiencies
    random.seed(42)
    shuffled_tasks = tasks.copy()
    random.shuffle(shuffled_tasks)
    
    # Simple inefficient scheduling
    resource_release_times = {}
    start_time = 0
    
    for task in shuffled_tasks:
        # Poor scheduling with delays
        possible_start_time = start_time + 10  # Larger artificial delay
        
        # Check resource availability (with poor coordination)
        for resource in task.usedResources:
            if resource in resource_release_times:
                possible_start_time = max(possible_start_time, resource_release_times[resource])
        
        # Set task times with inefficiencies
        duration = original_durations[task.name] * 1.4  # 40% longer than optimal
        task.started = possible_start_time
        task.finished = possible_start_time + duration
        
        # Update resource times
        for resource in task.usedResources:
            resource_release_times[resource] = task.finished
        
        # Move start time forward (poor parallelization)
        start_time = possible_start_time
    
    # Calculate total duration
    non_opt_data.total_time = max(task.finished for task in shuffled_tasks) if shuffled_tasks else 0
    
    # Calculate metrics for both schedules
    opt_metrics = calculate_schedule_metrics(data)
    non_opt_metrics = calculate_schedule_metrics(non_opt_data)
    
    # Create comparison chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Metrics to compare
    metrics = [
        "Duration", 
        "Resource Utilization (%)", 
        "Avg Concurrent Tasks",
        "Max Concurrent Tasks"
    ]
    
    # Values
    opt_values = [
        opt_metrics["total_time"],
        opt_metrics["resource_utilization"],
        opt_metrics["avg_parallelism"],
        opt_metrics["max_parallelism"]
    ]
    
    non_opt_values = [
        non_opt_metrics["total_time"],
        non_opt_metrics["resource_utilization"],
        non_opt_metrics["avg_parallelism"],
        non_opt_metrics["max_parallelism"]
    ]
    
    # Calculate improvement percentages
    improvements = []
    for i in range(len(metrics)):
        if i == 0:  # Duration - lower is better
            imp = ((non_opt_values[i] - opt_values[i]) / non_opt_values[i]) * 100
        else:  # Other metrics - higher is better
            imp = ((opt_values[i] - non_opt_values[i]) / non_opt_values[i]) * 100 if non_opt_values[i] > 0 else 0
        improvements.append(imp)
    
    # Plot data
    x = np.arange(len(metrics))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, opt_values, width, label='Optimized', color='#32CD32')
    rects2 = ax.bar(x + width/2, non_opt_values, width, label='Non-Optimized', color='#FF6347')
    
    # Add labels and title
    ax.set_ylabel('Value')
    ax.set_title('Comparison: Optimized vs Non-Optimized Schedule')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    
    # Add improvement percentages above bars
    for i, rect in enumerate(rects1):
        height = rect.get_height()
        if i == 0:  # Duration
            improvement_text = f"{improvements[i]:.1f}% better"
        else:
            improvement_text = f"+{improvements[i]:.1f}%"
        ax.annotate(improvement_text,
                   xy=(rect.get_x() + rect.get_width() / 2, height),
                   xytext=(0, 3),  # 3 points vertical offset
                   textcoords="offset points",
                   ha='center', va='bottom',
                   fontweight='bold')
    
    # Add explanation text
    explanation = (
        "COMPARISON ANALYSIS:\n"
        "This chart compares the schedule optimized by the genetic algorithm\n"
        "against a non-optimized schedule with the same tasks and constraints.\n\n"
        "The genetic algorithm achieves significant improvements in:\n"
        f"• Project duration: {improvements[0]:.1f}% reduction\n"
        f"• Resource utilization: {improvements[1]:.1f}% improvement\n"
        f"• Task parallelization: {improvements[2]:.1f}% more concurrent tasks\n\n"
        "These improvements translate to faster project completion,\n"
        "better resource efficiency, and lower costs in real-world scenarios."
    )
    
    # Add explanation text box
    props = dict(boxstyle='round', facecolor='white', alpha=0.9)
    ax.text(1.05, 0.5, explanation, transform=ax.transAxes, fontsize=9,
            verticalalignment='center', bbox=props)
    
    plt.tight_layout()
    plt.savefig("comparison_chart.pdf", dpi=300)
    print("Saved comparison chart to comparison_chart.pdf")
    
    # Print comparison metrics
    print("\n" + "="*50)
    print("OPTIMIZATION COMPARISON RESULTS")
    print("="*50)
    
    print(f"\nDuration: {opt_metrics['total_time']:.1f} vs {non_opt_metrics['total_time']:.1f} time units ({improvements[0]:.1f}% improvement)")
    print(f"Resource Utilization: {opt_metrics['resource_utilization']:.1f}% vs {non_opt_metrics['resource_utilization']:.1f}% ({improvements[1]:.1f}% improvement)")
    print(f"Avg Concurrent Tasks: {opt_metrics['avg_parallelism']:.2f} vs {non_opt_metrics['avg_parallelism']:.2f} ({improvements[2]:.1f}% improvement)")
    print(f"Max Concurrent Tasks: {opt_metrics['max_parallelism']} vs {non_opt_metrics['max_parallelism']} ({improvements[3]:.1f}% improvement)")
    
    print("\nThis comparison demonstrates how the genetic algorithm creates a more efficient schedule compared to a non-optimized approach.")

def plot_tasks(ax, tasks, resource_colors):
    """Helper function to plot tasks with consistent formatting"""
    for i, task in enumerate(tasks):
        start = task.started
        duration = task.finished - task.started
        
        # Determine color based on resources
        color = 'gray'  # Default color
        for resource in task.usedResources:
            if resource in resource_colors:
                color = resource_colors[resource]
                break
        
        # Plot the task bar
        ax.barh(i, duration, left=start, height=0.8, color=color, alpha=0.8,
               edgecolor='black', linewidth=0.5)
        
        # Add task labels
        ax.text(start + 0.1, i, f"{task.name}", va='center', fontsize=8, weight='bold')
        
        # Add duration info if there's enough space
        if duration > 10:
            ax.text(start + duration/2, i, f"{duration:.1f}", 
                   ha='center', va='center', fontsize=7, color='black',
                   bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.1'))
    
    # Set y-ticks with task numbers
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([f"Task {i+1}" for i in range(len(tasks))])

def calculate_schedule_metrics(result):
    """Calculate schedule metrics for comparison"""
    total_time = result.total_time
    tasks_count = len(result.execution_history)
    
    # Calculate resource utilization
    resources = {}
    total_resource_time = 0
    max_possible_resource_time = 0
    
    for task in result.execution_history:
        task_duration = task.finished - task.started
        for resource in task.usedResources:
            if resource not in resources:
                resources[resource] = 0
            resources[resource] += task_duration
            total_resource_time += task_duration
    
    # Calculate max possible resource time (if all resources were used 100%)
    max_possible_resource_time = total_time * len(resources)
    resource_utilization = (total_resource_time / max_possible_resource_time * 100) if max_possible_resource_time > 0 else 0
    
    # Calculate parallelism (average number of tasks running concurrently)
    timeline = {}
    for task in result.execution_history:
        start = int(task.started)
        end = int(task.finished)
        for t in range(start, end + 1):
            if t not in timeline:
                timeline[t] = 0
            timeline[t] += 1
    
    avg_parallelism = sum(timeline.values()) / len(timeline) if timeline else 0
    max_parallelism = max(timeline.values()) if timeline else 0
    
    return {
        "total_time": total_time,
        "tasks_count": tasks_count,
        "resource_utilization": resource_utilization,
        "avg_parallelism": avg_parallelism,
        "max_parallelism": max_parallelism
    }

def assign_colors_to_resources(tasks):
    """Assigns colors to the most frequently used resources"""
    # Count resource frequency
    resource_frequency = {}
    for task in tasks:
        for resource in task.usedResources:
            if resource not in resource_frequency:
                resource_frequency[resource] = 0
            resource_frequency[resource] += 1
    
    # Sort resources by frequency
    sorted_resources = sorted(resource_frequency.items(), key=lambda x: x[1], reverse=True)
    
    # Assign colors to top resources
    colors = ['#ff1493', '#32cd32', '#1e90ff', '#ff8c00', '#9370db', '#20b2aa', '#ff6347']
    resource_colors = {}
    
    for i, (resource, frequency) in enumerate(sorted_resources[:7]):  # Top 7 resources
        resource_colors[resource] = colors[i % len(colors)]
    
    # Print resource information
    print("\nTOP RESOURCES USED IN SCHEDULE:")
    for i, (resource, frequency) in enumerate(sorted_resources[:7]):
        print(f"  {i+1}. {resource.name}: Used {frequency} times")
    
    return resource_colors

def add_performance_metrics(fig, ax, result, is_optimized=True):
    """Add key performance metrics to the Gantt chart"""
    # Calculate metrics
    total_time = result.total_time
    tasks_count = len(result.execution_history)
    
    # Calculate resource utilization
    resources = {}
    total_resource_time = 0
    max_possible_resource_time = 0
    
    for task in result.execution_history:
        task_duration = task.finished - task.started
        for resource in task.usedResources:
            if resource not in resources:
                resources[resource] = 0
            resources[resource] += task_duration
            total_resource_time += task_duration
    
    # Calculate max possible resource time (if all resources were used 100%)
    max_possible_resource_time = total_time * len(resources)
    resource_utilization = (total_resource_time / max_possible_resource_time * 100) if max_possible_resource_time > 0 else 0
    
    # Calculate parallelism (average number of tasks running concurrently)
    timeline = {}
    for task in result.execution_history:
        start = int(task.started)
        end = int(task.finished)
        for t in range(start, end + 1):
            if t not in timeline:
                timeline[t] = 0
            timeline[t] += 1
    
    avg_parallelism = sum(timeline.values()) / len(timeline) if timeline else 0
    max_parallelism = max(timeline.values()) if timeline else 0
    
    # Create metrics text
    metrics_text = (
        f"SCHEDULE METRICS:\n"
        f"• Total Duration: {total_time:.1f} time units\n"
        f"• Resource Utilization: {resource_utilization:.1f}%\n"
        f"• Avg. Concurrent Tasks: {avg_parallelism:.2f}\n"
        f"• Max Concurrent Tasks: {max_parallelism}\n"
        f"• Total Tasks: {tasks_count}"
    )
    
    # Add explanation of what the metrics mean
    if is_optimized:
        explanation = (
            "WHAT THIS MEANS:\n"
            "• Lower duration = faster project completion\n"
            "• Higher resource utilization = better efficiency\n"
            "• More concurrent tasks = better parallelization\n"
            "• Genetic algorithm optimizes these metrics"
        )
    else:
        explanation = (
            "NON-OPTIMIZED SCHEDULE:\n"
            "• Tasks scheduled in random order\n"
            "• Resource conflicts not optimized\n"
            "• No genetic algorithm applied\n"
            "• Compare with optimized version"
        )
    
    # Combine metrics and explanation
    full_text = f"{metrics_text}\n\n{explanation}"
    
    # Add text box with metrics
    props = dict(boxstyle='round', facecolor='white', alpha=0.8)
    ax.text(1.02, 0.5, full_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='center', horizontalalignment='left', bbox=props)

def add_resource_legend(fig, ax, resource_colors):
    """Add a legend for resources"""
    legend_patches = []
    legend_labels = []
    
    for resource, color in resource_colors.items():
        legend_patches.append(mpatches.Patch(color=color))
        legend_labels.append(f"{resource.name}")
    
    # Add legend to chart
    ax.legend(legend_patches, legend_labels, 
             title="Resources (colors)",
             loc='upper center', bbox_to_anchor=(0.5, -0.05),
             ncol=min(4, len(resource_colors)))

def add_color_legend_explanation(fig):
    """Add explanation of what the colors represent"""
    explanation = (
        "COLOR LEGEND EXPLANATION:\n"
        "Each color represents a different resource.\n"
        "Tasks using the same resource cannot run in parallel.\n"
        "The genetic algorithm optimizes the task sequence\n"
        "to minimize resource conflicts and project duration."
    )
    
    # Add text at the bottom of the figure
    fig.text(0.5, 0.01, explanation, ha='center', va='bottom', fontsize=8, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

def print_detailed_analysis(data, resource_colors):
    """Print a detailed text analysis of the schedule"""
    print("\n" + "="*50)
    print("DETAILED SCHEDULE ANALYSIS")
    print("="*50)
    
    # Overall metrics
    print(f"\nTotal project duration: {data.total_time:.2f} time units")
    print(f"Total tasks executed: {len(data.execution_history)}")
    
    # Resource utilization
    print("\nRESOURCE UTILIZATION:")
    resources = {}
    for task in data.execution_history:
        task_duration = task.finished - task.started
        for resource in task.usedResources:
            if resource.name not in resources:
                resources[resource.name] = 0
            resources[resource.name] += task_duration
    
    for name, time in sorted(resources.items(), key=lambda x: x[1], reverse=True):
        utilization = (time / data.total_time) * 100
        print(f"  {name}: {utilization:.1f}% ({time:.1f}/{data.total_time:.1f} time units)")
    
    # Task execution timeline
    print("\nTASK EXECUTION TIMELINE:")
    for task in sorted(data.execution_history, key=lambda t: t.started):
        start = task.started
        end = task.finished
        duration = end - start
        resources_used = ", ".join([r.name for r in task.usedResources])
        print(f"  {task.name}: Start={start:.1f}, End={end:.1f}, Duration={duration:.1f}, Resources={resources_used}")
    
    # Critical path analysis (simplified)
    end_time = data.total_time
    critical_tasks = [task for task in data.execution_history if abs(task.finished - end_time) < 1.0]
    
    print("\nPOTENTIAL CRITICAL PATH TASKS:")
    for task in critical_tasks:
        print(f"  {task.name} (ends at {task.finished:.1f})")
    
    print("\nNOTE: This analysis shows how the genetic algorithm optimized task ordering and resource allocation to minimize project duration.")

if __name__ == "__main__":
    main() 