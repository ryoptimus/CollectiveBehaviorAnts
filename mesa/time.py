"""Minimal scheduler classes used by the Project 05 autograder."""

from __future__ import annotations

import random


class SimultaneousActivation:
    """Old-Mesa-compatible scheduler.

    The project notebook schedules Nest, Food, Environment, and Ant objects.
    Static agents inherit no-op step/advance methods from the local Agent shim.
    """

    def __init__(self, model):
        self.model = model
        self.agents = []
        self.steps = 0
        self.time = 0

    def add(self, agent):
        if agent not in self.agents:
            self.agents.append(agent)

    def remove(self, agent):
        if agent in self.agents:
            self.agents.remove(agent)

    def step(self):
        # Mesa's schedulers operate over a copy so agents may alter schedules.
        agents = list(self.agents)
        rng = getattr(self.model, "random", None)
        # Preserve insertion order by default. Students can still use random moves.
        for agent in agents:
            step = getattr(agent, "step", None)
            if callable(step):
                step()
        for agent in agents:
            advance = getattr(agent, "advance", None)
            if callable(advance):
                advance()
        self.steps += 1
        self.time += 1

    def get_agent_count(self):
        return len(self.agents)
