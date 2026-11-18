# CSE 568 Project 05 - Collective Behavior in Ants

Submit a file named `student_solution.py` containing your completed `Ant` class.

The autograder supplies the non-student notebook components: `Environment`, `Nest`, `Food`, `AntModel`, a small Mesa-compatible API, and the `get_distance(pos_1, pos_2)` helper. Your `Ant` class should work with the same interface used in the zyBooks notebook.

## Required class

```python
from mesa import Agent

class Ant(Agent):
    def __init__(self, unique_id, home, model, moore=True):
        ...

    def step(self):
        ...
```

## Required behavior

The constructor should:

- store the nest/home object,
- start the ant at the nest location,
- initialize `state` to `"UNCOMMITTED"`, and
- initialize `tandem_running` to `False` or `0`.

The `step()` method should implement the flow chart from the project notebook:

- uncommitted ants move randomly unless they are at a feeder;
- uncommitted ants at feeder A/B eat one unit and commit with probability `alpha_A`/`alpha_B`;
- committed ants uncommit with probability `lambda_A`/`lambda_B`;
- tandem-running committed ants move toward their feeder, eat at the feeder, and stop tandem running;
- committed ants that are not tandem running recruit an uncommitted ant in the same cell with probability `beta_A`/`beta_B`; and
- successful recruitment commits the recruit to the same feeder and sets both ants' tandem-running flags to true.

Use the exact state strings from the notebook:

```text
UNCOMMITTED
COMMITTED A
COMMITTED B
```

The autograder awards partial credit for constructor fields, uncommitted movement, food discovery/commitment, attrition, tandem movement/eating, recruitment, and full-model integration.
