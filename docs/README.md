# Genetic Algorithm for Resource-Constrained Project Scheduling Problem (SRCPSP)

This project implements a genetic algorithm approach to solve the Resource-Constrained Project Scheduling Problem (RCPSP), which is a well-known NP-hard optimization problem in operations research and project management.

*Note: The optimized schedule can be viewed in the generated gantt_optimized.pdf file after running the visualization script.*

## Project Overview

The Resource-Constrained Project Scheduling Problem involves scheduling a set of tasks/activities with specified durations and resource requirements, while respecting precedence constraints (task dependencies) and resource limitations. The objective is typically to minimize the overall project makespan (completion time).

### Key Features

- **Genetic Algorithm Optimization**: Employs evolutionary computing to find near-optimal schedules
- **Resource Constraint Handling**: Manages limited resource availability across project tasks
- **Schedule Visualization**: Generates detailed Gantt charts to visualize task schedules
- **Performance Metrics**: Calculates and reports key schedule performance indicators
- **Comparison Analysis**: Demonstrates optimization benefits against non-optimized schedules

## Background

### The RCPSP Problem

In project management, resources (human resources, equipment, materials) are often limited, and tasks may have dependencies on one another. Finding the optimal sequence to schedule these tasks while respecting all constraints is computationally challenging. For even moderately sized projects, exhaustive search becomes infeasible.

### Genetic Algorithm Approach

Genetic algorithms mimic natural selection to evolve solutions over multiple generations:

1. **Population**: Maintains a set of potential schedules
2. **Selection**: Favors better-performing schedules (those with shorter durations)
3. **Crossover**: Combines aspects of good schedules to create new candidates
4. **Mutation**: Introduces small random changes to avoid local optima
5. **Fitness Evaluation**: Assesses schedules based on duration and constraint satisfaction

Through this evolutionary process, the algorithm converges toward increasingly efficient schedules, balancing resource usage and minimizing overall duration.

## Project Structure

```
Genetic-SRCPSP/
├── deepThought/              # Core implementation modules
│   ├── optimizer/            # Genetic algorithm implementation
│   ├── scheduler/            # Task scheduling algorithms
│   ├── simulator/            # Simulation engine for schedule execution
│   ├── visualizer/           # Visualization and Gantt chart generation
│   └── ORM/                  # Object-relational mapping for data models
├── sampleData/               # Example project datasets
├── run_visualizer.py         # Script for generating visualizations
├── output.pickle             # Simulation results from the most recent run
├── gantt_optimized.pdf       # Visualization of the optimized schedule
├── gantt_non_optimized.pdf   # Visualization of a non-optimized schedule
└── comparison_chart.pdf      # Performance comparison between schedules
```

## Data Model

The project works with the following data entities:

- **Tasks**: Individual activities with durations, dependencies, and resource requirements
- **Resources**: Entities with limited availability that tasks require to execute
- **Dependencies**: Predecessor-successor relationships between tasks
- **Schedule**: A solution representing start/end times for all tasks

## How to Run

### Prerequisites

- Python 3.7 or higher
- Required packages (install via `pip install -r requirements.txt`):
  - matplotlib
  - numpy
  - networkx (for graph operations)

### Running the Simulation

1. **Basic Run**:
   ```
   python -m deepThought.simulator.simulator --scheduler genetic --output output.pickle
   ```

2. **Generate Visualizations**:
   ```
   python run_visualizer.py
   ```
   This will create three files:
   - `gantt_optimized.pdf`: The optimized schedule
   - `gantt_non_optimized.pdf`: A non-optimized schedule for comparison
   - `comparison_chart.pdf`: Performance metrics comparison

3. **Advanced Options**:
   ```
   python -m deepThought.simulator.simulator --scheduler genetic --iterations 100 --population 50 --output output.pickle
   ```

### Command Line Arguments

- `--scheduler`: Scheduling algorithm to use (options: `genetic`, `reference`, `PPPolicies`)
- `--iterations`: Number of generations for the genetic algorithm (default: 50)
- `--population`: Population size for the genetic algorithm (default: 20)
- `--output`: File path to save simulation results (default: output.pickle)

## Understanding the Output

### Visualization Files

The visualization process generates several files:

1. **gantt_optimized.pdf**: Gantt chart showing the optimized schedule produced by the genetic algorithm
   - Color-coded by resource usage
   - Includes task durations and relationships
   - Contains summary metrics on project performance

2. **gantt_non_optimized.pdf**: Gantt chart showing a non-optimized schedule for comparison
   - Uses the same task set but with suboptimal scheduling
   - Demonstrates increased project duration and resource conflicts

3. **comparison_chart.pdf**: Bar chart comparing key performance metrics
   - Project duration reduction
   - Resource utilization improvement
   - Task parallelization comparison

### Example Output Interpretation

When you run the visualizer, you'll see output like this:

```
Loaded simulation result with 13 tasks
Total duration: 279.41

TOP RESOURCES USED IN SCHEDULE:
  1. Resource 3: Used 4 times
  2. Resource 1: Used 4 times
  3. Resource 6: Used 4 times
  
COMPARISON RESULTS:
Duration: 279.4 vs 470.5 time units (40.6% improvement)
Resource Utilization: 45.7% vs 38.0% (20.3% improvement)
Avg Concurrent Tasks: 2.44 vs 2.08 (17.5% improvement)
```

This shows that the genetic algorithm achieved a 40.6% reduction in project duration compared to a non-optimized approach.

### Performance Metrics

The visualizations and console output include several key performance indicators:

- **Total Duration**: Overall project completion time (lower is better)
- **Resource Utilization**: Percentage of available resource time effectively used
- **Average Concurrent Tasks**: Measure of task parallelization
- **Critical Path Tasks**: Tasks that directly impact the project completion time

## Sample Results

In a typical run with the provided test data, the genetic algorithm achieves:

- **Duration Reduction**: 30-40% shorter project completion time
- **Resource Utilization**: 15-25% improvement in resource usage efficiency
- **Task Parallelization**: Enhanced concurrent task execution

## Visualization Examples

After running the visualizer, the generated PDFs will look similar to these:

### Optimized Schedule
The optimized schedule shows efficient resource usage and task parallelization with a shorter overall duration.

*View `gantt_optimized.pdf` for a color-coded Gantt chart of the optimized schedule.*

### Non-Optimized Schedule
The non-optimized schedule shows less efficient resource allocation and longer project duration.

*View `gantt_non_optimized.pdf` for comparison.*

### Performance Comparison
The comparison chart provides a clear visualization of the improvements achieved by the genetic algorithm.

*View `comparison_chart.pdf` for a bar chart comparing key metrics.*

## Real-World Applications

This type of optimization is valuable in:

- **Construction Projects**: Optimizing use of equipment and labor
- **Software Development**: Managing developer assignments across sprints
- **Manufacturing**: Production planning with machine constraints
- **Event Planning**: Coordinating vendors and setup crews
- **Research Projects**: Allocating lab equipment and researcher time

## Limitations

- Does not account for partial resource allocation
- Assumes deterministic task durations (no uncertainty)
- May not find the global optimum due to the NP-hard nature of the problem

## References

- Hartmann, S. (1998). "A competitive genetic algorithm for resource-constrained project scheduling"
- Kolisch, R., & Hartmann, S. (2006). "Experimental investigation of heuristics for resource-constrained project scheduling"

## License

This project is licensed under the MIT License - see the LICENSE file for details.


