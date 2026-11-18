"""Small Mesa-compatible shim for the CSE 568 Project 05 autograder.

It implements only the API surface used by the project notebook:
Agent, Model, SimultaneousActivation, MultiGrid, and DataCollector.
"""

from __future__ import annotations

import random as _random


class Agent:
    """Minimal old-Mesa-style Agent base class."""

    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.pos = None
        self.random = getattr(model, "random", _random.Random())

    def step(self):
        """Default no-op step so static environment agents can be scheduled."""
        return None

    def advance(self):
        """Default no-op advance for SimultaneousActivation compatibility."""
        return None


class Model:
    """Minimal old-Mesa-style Model base class."""

    def __init__(self, *args, **kwargs):
        seed = kwargs.get("seed", None)
        self.random = _random.Random(seed)
        self.running = True
        self._next_id = 0

    def next_id(self):
        self._next_id += 1
        return self._next_id

    def run_model(self, max_steps=10000):
        steps = 0
        while getattr(self, "running", True) and steps < max_steps:
            self.step()
            steps += 1
        return steps


try:  # re-export the project-used classes from submodules
    from .time import SimultaneousActivation  # noqa: F401
    from .space import MultiGrid  # noqa: F401
    from .datacollection import DataCollector  # noqa: F401
except Exception:
    pass
