# Image Placement for Documentation

This directory contains images for the project documentation. To make the README more visually informative, place screenshots of your generated PDF files here.

## Required Images

Please add the following images to this directory after running the project:

1. **optimized_schedule.png** - Screenshot of the optimized Gantt chart (from gantt_optimized.pdf)
2. **non_optimized_schedule.png** - Screenshot of the non-optimized Gantt chart (from gantt_non_optimized.pdf)
3. **comparison_chart.png** - Screenshot of the performance comparison chart (from comparison_chart.pdf)

## How to Create the Images

1. Run the project following the instructions in the main README:
   ```
   python -m deepThought.simulator.simulator --scheduler genetic --output output.pickle
   python run_visualizer.py
   ```

2. Open each of the generated PDF files:
   - gantt_optimized.pdf
   - gantt_non_optimized.pdf
   - comparison_chart.pdf

3. Take screenshots of each file:
   - For Windows: Use Snipping Tool or press Windows+Shift+S
   - For macOS: Press Command+Shift+4
   - For Linux: Use Screenshot tool or press PrintScreen

4. Save each screenshot with the corresponding name in this directory

## Image Sizes

For best display in the README:
- Use PNG format for clarity
- Keep images under 1MB each
- Recommended resolution: 800-1200px width
- Maintain aspect ratio

## Example

Here's how the images will appear in the main README:

```markdown
![Optimized Schedule Gantt Chart](docs/images/optimized_schedule.png)
*Sample optimized schedule Gantt chart showing efficient resource allocation and task parallelization*
``` 