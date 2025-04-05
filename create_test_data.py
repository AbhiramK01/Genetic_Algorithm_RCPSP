#!/usr/bin/env python
import pickle
from deepThought.ORM.ORM import Job, Task, Resource, Capability, RequiredResource, DistributionType
import random
import math

# Create a simple job with tasks and resources
job = Job()

# Create some capabilities
capabilities = {}
for i in range(5):
    cap = Capability()
    cap.id = f"cap_{i}"
    cap.name = f"Capability {i}"
    capabilities[cap.id] = cap
    job.capabilities[cap.id] = cap

# Create some resources
resources = {}
for i in range(10):
    res = Resource()
    res.id = f"res_{i}"
    res.name = f"Resource {i}"
    res.set_max_share_count(1)
    
    # Each resource provides 1-3 capabilities
    num_caps = random.randint(1, 3)
    for j in range(num_caps):
        cap_id = random.choice(list(capabilities.keys()))
        res.provided_capabilities.append(job.capabilities[cap_id])
    
    resources[res.id] = res
    job.resources[res.id] = res

# Create some tasks with dependencies
num_tasks = 20
tasks = {}
for i in range(num_tasks):
    task = Task()
    task.id = i  # Use integer instead of string
    task.name = f"Task {i}"
    task.mean = random.uniform(10, 100)  # Random execution time between 10-100
    task.deviation = 0  # Use fixed distribution to avoid numerical issues
    task.distribution_type = DistributionType.FIXED
    
    # Each task requires 1-2 resources
    num_resources = random.randint(1, 2)
    for j in range(num_resources):
        req_res = RequiredResource()
        req_res.name = f"Required for Task {i}"
        req_res.number_required = 1
        
        # Add 1-2 required capabilities
        num_req_caps = random.randint(1, 2)
        for k in range(num_req_caps):
            cap_id = random.choice(list(capabilities.keys()))
            req_res.required_capabilities.append(job.capabilities[cap_id])
        
        # Find resources that can fulfill this requirement
        for res in job.resources.values():
            can_fulfill = True
            for cap in req_res.required_capabilities:
                if cap not in res.provided_capabilities:
                    can_fulfill = False
                    break
            if can_fulfill:
                req_res.fulfilled_by.append(res)
                res.required_by.append(task)
        
        task.required_resources.append(req_res)
    
    # Add task to job
    tasks[task.id] = task
    job.tasks[task.id] = task

# Mark as already initialized to skip phase-type distribution calculations
job.already_initialized = True

# Save the job to a pickle file
with open("sampleData/test_data.pickle", "wb") as f:
    pickle.dump(job, f)

print(f"Created test dataset with {num_tasks} tasks and {len(job.resources)} resources") 