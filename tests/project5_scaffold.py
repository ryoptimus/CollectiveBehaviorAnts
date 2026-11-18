"""Project 05 scaffold used by the Gradescope autograder.

This mirrors the non-student portions of the zyBooks notebook and lets the
student-provided Ant class plug into the model.
"""

from __future__ import annotations

import math
import random
from typing import List, Optional, Type

from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


class Environment(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos

    def get_pos(self):
        return self.pos


class Nest(Agent):
    """The ant nest."""

    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos


class Food(Agent):
    """A food cache for the ants."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.amount = 0

    def add(self, amount):
        self.amount += amount

    def eaten(self):
        if self.any_food():
            self.amount -= 1

    def any_food(self):
        return self.amount > 0


def get_distance(pos_1, pos_2):
    """Get the Euclidean distance between two coordinate tuples."""
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)


class AntModel(Model):
    """A model for ant foraging, parameterized by a student Ant class."""

    def __init__(
        self,
        AntClass,
        N=100,
        width=50,
        height=50,
        alpha_A=0.0125 * 60,
        alpha_B=0.0125 * 60,
        beta_A=0.015 * 60,
        beta_B=0.006 * 60,
        lambda_A=0.009,
        lambda_B=0.038,
        seed: Optional[int] = None,
        add_environment: bool = True,
    ):
        super().__init__(seed=seed)
        if seed is not None:
            self.random.seed(seed)
            random.seed(seed)

        self.num_agents = N
        self.alpha_A = alpha_A
        self.alpha_B = alpha_B
        self.beta_A = beta_A
        self.beta_B = beta_B
        self.lambda_A = lambda_A
        self.lambda_B = lambda_B

        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(width, height, False)

        nest_loc = (25, 5)
        self.food_locs = ((10, 40), (40, 40))

        self.nest = Nest(self.next_id(), nest_loc, self)
        self.foods: List[Food] = []
        self.grid.place_agent(self.nest, nest_loc)
        self.schedule.add(self.nest)

        self.ants = []
        for _ in range(self.num_agents):
            ant = AntClass(self.next_id(), self.nest, self)
            self.grid.place_agent(ant, self.nest.pos)
            self.schedule.add(ant)
            self.ants.append(ant)

        for loc in self.food_locs:
            food = Food(self.next_id(), self)
            food.add(100)
            self.grid.place_agent(food, loc)
            self.schedule.add(food)
            self.foods.append(food)

        if add_environment:
            for _contents, x, y in self.grid.coord_iter():
                cell = Environment(self.next_id(), (x, y), self)
                self.grid.place_agent(cell, (x, y))
                self.schedule.add(cell)

        self.running = True
        self.dc = DataCollector(
            {
                "Feeder A:": lambda m: m.foods[0].amount,
                "Feeder B:": lambda m: m.foods[1].amount,
            }
        )

    def step(self):
        self.schedule.step()
        self.dc.collect(self)
        if not self.foods[0].any_food() or not self.foods[1].any_food():
            self.running = False


def all_ants(model):
    return list(getattr(model, "ants", []))
