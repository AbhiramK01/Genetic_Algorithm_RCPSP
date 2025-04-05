__author__ = 'jules'

import simpy
import argparse
import sys
import copy
import deepThought.ORM.ORM as ORM
import pickle

from deepThought.scheduler.referenceScheduler import ReferenceScheduler
from deepThought.scheduler.optimizedDependencyScheduler import OptimizedDependencyScheduler
from deepThought.scheduler.RBRS import RBRS
from deepThought.scheduler.PPPolicies import PPPolicies
from deepThought.scheduler.ABPolicy import ABPolicy
from deepThought.scheduler.JFPol import JFPol
from deepThought.simulator.simulationResult import *

from deepThought.simulator.simulationEntity import SimulationEntity
import random
import numpy as np
import time

import matplotlib.pylab as plt
import seaborn as sns
import datetime

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", help="The pickle file containing the testData")
    arg_parser.add_argument("--scheduler", help="specifies the scheduler to be used. Default is referenceScheduler. \
                                                Other possible values: optimizedDependencyScheduler")
    arg_parser.add_argument("--output", help="specifies the file where the result should be written to")
    arg_parser.add_argument("--precomputeprobability", help="precomputes the probability data. follwed by a number")
    arg_parser.add_argument("--show_gen_log", help="controls whether to show historic genetic data")
    args = arg_parser.parse_args()

    #comment out if deterministic solutions are required
    np.random.seed(int(time.time()))
    random.seed()

    try:
        job = ORM.deserialize(args.file)
    except IOError:
        Logger.error("The file specified was not found.")
        sys.exit(127)

    assert isinstance(job, ORM.Job)


    Logger.debug("instantiating scheduler")
    schedulers = {
        ReferenceScheduler.__name__ : ReferenceScheduler,
        OptimizedDependencyScheduler.__name__ : OptimizedDependencyScheduler,
        RBRS.__name__ : RBRS,
        PPPolicies.__name__ : PPPolicies,
        ABPolicy.__name__  : ABPolicy,
        JFPol.__name__ : JFPol
    }

    if args.scheduler is None:
        scheduler = ReferenceScheduler(job)
    else:
        try:
            scheduler =  schedulers[args.scheduler](job)
        except KeyError:
            Logger.error("The scheduler specified does not exist.")
            sys.exit(127)

    if args.precomputeprobability is not None:
        Logger.debug("initializing job")
        job.initialize()
        Logger.info("Precomputing probability...")
        for i, task in enumerate(job.tasks.values()):
            Logger.info("Computing probabilities for task %s" % (i))
            task.fill_pre_computed_execution_times(int(args.precomputeprobability))

        Logger.info("Calculating Resource dependencies...")
        scheduler.initialize()
        job.already_initialized = True
        Logger.info("Writing to file")
        pickle.dump(job, open(args.file, "wb"))
        sys.exit(0)

    start_time = datetime.datetime.now()
    if job.already_initialized == False:
        job.initialize()
        scheduler.initialize()
        Logger.debug("initializing job")
    else:
        # Make sure the scheduler is initialized even if the job is already initialized
        if hasattr(scheduler, 'initialize'):
            scheduler.initialize()



    Logger.debug("starting simulation...")
    result = simulate_schedule(scheduler)
    duration = datetime.datetime.now() - start_time
    Logger.warning("Simulation  complete. Duration: %s" % (duration))
    if args.show_gen_log is not None:
        log_list = scheduler.getListGALog()

        list_min = [datapoint['min'] for datapoint in log_list]
        list_max = [datapoint['max'] for datapoint in log_list]

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(2, 1, 1)
        p1 = ax.plot(list(range(len(list_min))),list_min, 'b-', marker='o')
        p2 = ax.plot(list(range(len(list_max))),list_max, 'r-', marker='x')

        ax.set_xlabel("ListGA Generation", fontsize=12)
        ax.set_ylabel("Fitness (execution time)", fontsize=12)
        plt.legend((p1[0], p2[0]), ('Best Fitness', 'Worst Fitness'))
        
        # Add improvement calculations and annotations
        if len(list_min) > 1:
            total_improvement = (list_min[0] - list_min[-1]) / list_min[0] * 100
            ax.annotate(f'Total improvement: {total_improvement:.1f}%', 
                        xy=(len(list_min)-1, list_min[-1]),
                        xytext=(len(list_min)-1, list_min[-1]*1.2),
                        arrowprops=dict(facecolor='green', shrink=0.05))
        
        # Add explanation text
        explanation = """
        ListGA Evolution: Shows how task sequence improves over generations.
        • Lower values = Better schedules (shorter execution time)
        • Blue line = Best solution in population
        • Red line = Worst solution in population
        • Downward trend shows genetic algorithm improvement
        """
        props = dict(boxstyle='round', facecolor='lightblue', alpha=0.5)
        ax.text(0.5, 0.05, explanation, transform=ax.transAxes, fontsize=9,
               bbox=props, horizontalalignment='center')

        ax = fig.add_subplot(2, 1, 2)

        log_arc = scheduler.getArcGALog()
        list_min = [datapoint['min'] for datapoint in log_arc]
        list_max = [datapoint['max'] for datapoint in log_arc]

        for entry in list_max:
            if type(entry) == tuple:
                list_max.remove(entry)
        p1 = ax.plot(list(range(len(list_min))),list_min, 'b-', marker='o')
        p2 = ax.plot(list(range(len(list_max))),list_max, 'r-', marker='x')

        ax.set_xlabel("ArcGA Generation", fontsize=12)
        ax.set_ylabel("Fitness", fontsize=12)
        plt.legend((p1[0], p2[0]), ('Best Fitness', 'Worst Fitness'))
        
        # Add ArcGA explanation text
        arc_explanation = """
        ArcGA Evolution: Shows how resource allocation improves over generations.
        • Lower values = Better resource assignments
        • ArcGA applies additional ordering constraints between tasks
        • Genetic algorithm explores solution space to find optimal configuration
        """
        props = dict(boxstyle='round', facecolor='lightblue', alpha=0.5)
        ax.text(0.5, 0.05, arc_explanation, transform=ax.transAxes, fontsize=9,
               bbox=props, horizontalalignment='center')
        
        # Add title explaining genetic algorithm
        fig.suptitle('Genetic Algorithm Evolution Progress\n' + 
                    'Shows how the genetic algorithm improves schedules over generations', 
                    fontsize=16)

        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for overall title
        
        if args.output is not None:
            # Save the GA evolution chart
            ga_chart_output = args.output.replace('.pickle', '_ga_evolution.pdf')
            plt.savefig(ga_chart_output, dpi=300)
            Logger.info(f"Genetic algorithm evolution chart saved to {ga_chart_output}")
        else:
            plt.show()

    if args.output is not None:
        try:
            save_simulation_result(result, args.output)
            Logger.info(f"Simulation result saved to file: {args.output}")
            
            # Add summary of scheduling results to console output
            print("\n" + "="*60)
            print("GENETIC ALGORITHM SCHEDULING RESULTS")
            print("="*60)
            print(f"\nTotal project duration: {result.total_time:.2f} time units")
            print(f"Total tasks executed: {len(result.execution_history)}")
            
            if hasattr(scheduler, 'getListGALog') and scheduler.getListGALog():
                log = scheduler.getListGALog()
                if log and len(log) > 1:
                    initial_fitness = log[0]['min']
                    final_fitness = log[-1]['min']
                    improvement = (initial_fitness - final_fitness) / initial_fitness * 100
                    print(f"\nGenetic Algorithm Improvement:")
                    print(f"  Initial best fitness: {initial_fitness:.2f}")
                    print(f"  Final best fitness: {final_fitness:.2f}")
                    print(f"  Improvement: {improvement:.2f}%")
            
            print("\nTo visualize the schedule with detailed metrics, run:")
            print(f"  python visualizer.py --pdf output_gantt.pdf --detailed {args.output}")
            print("="*60)
            
        except IOError:
            "The outputfile cannot be opened for writing."


def simulate_schedule(scheduler, stochastic=True, old_execution_history = None):
    env = simpy.Environment()
    #closure to capture scheduler Object
    def task_finished_callback(env):
        Logger.debug("Task finished. Current Simulation time: %s" % env.now)
        Logger.debug("%s tasks remaining" % len(scheduler.tasks_to_do))
        #as long as the scheduler has work to do, spawn tasks until resources are depleted
        while scheduler.has_next():
                SimulationEntity(env, scheduler.get_next(), task_finished_callback, stochastic, old_execution_history)

    #spawn tasks until resources are depleted
    while scheduler.has_next():
            SimulationEntity(env, scheduler.get_next(), task_finished_callback, stochastic, old_execution_history)
    env.run()
    if scheduler.no_tasks_executed != 44:
        Logger.warning("either too much or to few tasks executed")
    if scheduler.has_work_left():
        Logger.warning("The scheduler still has work left but can't continue! There is a Problem!")

    else:
        Logger.info("Simulation successful. Simulated Time: %s" % env.now)
    result = SimulationResult()
    result.total_time = env.now
    result.set_execution_history(scheduler.get_execution_history())

    return result

if __name__ == "__main__":
    main()