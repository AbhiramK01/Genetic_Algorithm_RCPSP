__author__ = 'jules'

import sys
import argparse
import matplotlib.pyplot as plt
from deepThought.util import Logger
from deepThought.simulator.simulationResult import load_simulation_result
from .gantt import determine_top_resources, create_gantt_chart, plot_gantt
import deepThought.ORM.ORM as ORM


def main():
    """
    Main function for the visualizer
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="The pickle file containing the result")
    parser.add_argument("--pdf", help="specifies the file where the graphic should be stored as pdf")
    parser.add_argument("--dpi", help="specifies to dpi of the output file (default: 300)", type=int, default=300)
    parser.add_argument("--detailed", help="show detailed analysis of the schedule", action="store_true")
    
    args = parser.parse_args()
    
    try:
        data = load_simulation_result(args.file)
    except Exception as e:
        Logger.error(f"Error loading file: {e}")
        return
    
    resource_list = determine_top_resources(data.execution_history, 7)
    
    if args.pdf:
        save_gantt_chart(data, args.pdf, args.dpi)
    
    # If detailed analysis is requested, print it to the console
    if args.detailed:
        print_detailed_analysis(data, resource_list)


def save_gantt_chart(test_run_data, output_file, dpi):
    """
    Creates a Gantt chart and saves it to a file.
    Enhanced with performance metrics and explanations.
    """
    # Call the create_gantt_chart function
    fig, ax = create_gantt_chart(test_run_data)
    
    # Add performance metrics to the chart
    add_performance_metrics(fig, ax, test_run_data)
    
    # Add explanation of colors
    add_color_legend_explanation(fig)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=dpi)


def add_performance_metrics(fig, ax, result):
    """Add key performance metrics to the Gantt chart"""
    # Calculate metrics
    total_time = result.total_time
    
    # Calculate resource utilization
    resources = {}
    total_resource_time = 0
    max_possible_resource_time = 0
    
    for task in result.execution_history:
        task_duration = task.executionTime
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
        start = int(task.startTime)
        end = int(task.startTime + task.executionTime)
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
        f"• Total Tasks: {len(result.execution_history)}"
    )
    
    # Add explanation of what the metrics mean
    explanation = (
        "WHAT THIS MEANS:\n"
        "• Lower duration = faster project completion\n"
        "• Higher resource utilization = better efficiency\n"
        "• More concurrent tasks = better parallelization\n"
        "• Genetic algorithm optimizes these metrics"
    )
    
    # Combine metrics and explanation
    full_text = f"{metrics_text}\n\n{explanation}"
    
    # Add text box with metrics
    props = dict(boxstyle='round', facecolor='white', alpha=0.8)
    ax.text(1.02, 0.5, full_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='center', horizontalalignment='left', bbox=props)


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


def print_detailed_analysis(data, resource_list):
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
        for resource in task.usedResources:
            if resource.name not in resources:
                resources[resource.name] = 0
            resources[resource.name] += task.executionTime
    
    for name, time in sorted(resources.items(), key=lambda x: x[1], reverse=True):
        utilization = (time / data.total_time) * 100
        print(f"  {name}: {utilization:.1f}% ({time:.1f}/{data.total_time:.1f} time units)")
    
    # Task execution timeline
    print("\nTASK EXECUTION TIMELINE:")
    for task in sorted(data.execution_history, key=lambda t: t.startTime):
        start = task.startTime
        end = task.startTime + task.executionTime
        resources_used = ", ".join([r.name for r in task.usedResources])
        print(f"  {task.name}: Start={start:.1f}, End={end:.1f}, Duration={task.executionTime:.1f}, Resources={resources_used}")
    
    # Critical path analysis (simplified)
    task_dict = {task.id: task for task in data.execution_history}
    end_time = data.total_time
    critical_tasks = [task for task in data.execution_history if abs(task.startTime + task.executionTime - end_time) < 1.0]
    
    print("\nPOTENTIAL CRITICAL PATH TASKS:")
    for task in critical_tasks:
        print(f"  {task.name} (ends at {task.startTime + task.executionTime:.1f})")
    
    print("\nNOTE: This analysis shows how the genetic algorithm optimized task ordering and resource allocation to minimize project duration.")


if __name__ == "__main__":
    main()