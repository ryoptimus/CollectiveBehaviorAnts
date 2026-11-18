#!/usr/bin/env python3
"""Gradescope grader for CSE 568 Project 05.

The grader imports /autograder/submission/student_solution.py and tests the
student-provided Ant class inside the Project 05 model scaffold.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import math
import os
import random
import signal
import sys
import traceback
from dataclasses import dataclass
from typing import Callable, List

RESULTS_DIR = os.environ.get("GRADESCOPE_RESULTS_DIR", "/autograder/results")
SOURCE_DIR = os.environ.get("GRADESCOPE_SOURCE_DIR", "/autograder/source")
SUBMISSION_DIR = os.environ.get("GRADESCOPE_SUBMISSION_DIR", "/autograder/submission")

# Make local execution easy while preserving Gradescope behavior.
if not os.path.isdir(SOURCE_DIR):
    SOURCE_DIR = os.getcwd()
if not os.path.isdir(SUBMISSION_DIR):
    SUBMISSION_DIR = os.getcwd()

for path in [SUBMISSION_DIR, SOURCE_DIR, os.path.join(SOURCE_DIR, "tests")]:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    os.chdir(SOURCE_DIR)
except Exception:
    pass

from project5_scaffold import AntModel, Environment, Food, Nest, all_ants, get_distance  # noqa: E402


class TimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):  # type: ignore[no-untyped-def]
    raise TimeoutError("Timed out while running this check")


def run_with_timeout(func: Callable[[], None], seconds: int = 20) -> None:
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(seconds)
    try:
        func()
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def canonical_state(agent) -> str:
    value = getattr(agent, "state", None)
    return str(value).strip().upper().replace("_", " ")


def assert_state(agent, expected: str, label: str = "ant") -> None:
    actual = canonical_state(agent)
    if actual != expected:
        raise AssertionError(f"{label} state should be {expected!r}, got {getattr(agent, 'state', None)!r}")


def assert_tandem(agent, expected: bool, label: str = "ant") -> None:
    actual = bool(getattr(agent, "tandem_running", None))
    if actual != expected:
        raise AssertionError(
            f"{label}.tandem_running should be {expected}, got {getattr(agent, 'tandem_running', None)!r}"
        )


def build_model(student, **kwargs):
    if not hasattr(student, "Ant"):
        raise AssertionError("student_solution.py must define class Ant")
    return AntModel(student.Ant, **kwargs)


def prepare_student_module(student) -> None:
    """Inject notebook scaffold names that student Ant methods may reference."""
    injections = {
        "Environment": Environment,
        "Nest": Nest,
        "Food": Food,
        "AntModel": AntModel,
        "get_distance": get_distance,
        "math": math,
        "random": random,
    }
    for name, value in injections.items():
        if not hasattr(student, name):
            setattr(student, name, value)


def check_constructor(student) -> None:
    model = build_model(
        student,
        N=1,
        alpha_A=0,
        alpha_B=0,
        beta_A=0,
        beta_B=0,
        lambda_A=0,
        lambda_B=0,
        seed=1,
    )
    ants = all_ants(model)
    if len(ants) != 1:
        raise AssertionError(f"Expected exactly 1 ant in the test model, got {len(ants)}")
    ant = ants[0]
    if not hasattr(ant, "step") or not callable(ant.step):
        raise AssertionError("Ant must define a callable step() method")
    assert_state(ant, "UNCOMMITTED")
    assert_tandem(ant, False)
    if getattr(ant, "home", None) is not model.nest:
        raise AssertionError("Ant.home should store the nest object passed to the constructor")
    if ant.pos != model.nest.pos:
        raise AssertionError(f"Ant should start at the nest location {model.nest.pos}, got {ant.pos}")


def check_uncommitted_random_move(student) -> None:
    model = build_model(
        student,
        N=1,
        alpha_A=0,
        alpha_B=0,
        beta_A=0,
        beta_B=0,
        lambda_A=0,
        lambda_B=0,
        seed=2,
    )
    ant = all_ants(model)[0]
    start = ant.pos
    ant.step()
    assert_state(ant, "UNCOMMITTED")
    if ant.pos == start:
        raise AssertionError("An uncommitted ant that is not at food should move to a neighboring cell")
    if get_distance(start, ant.pos) > math.sqrt(2) + 1e-9:
        raise AssertionError(f"Random move should move only one Moore-neighborhood cell, got {start} -> {ant.pos}")


def check_discovery_and_commitment(student) -> None:
    # Feeder A: alpha_A = 1, so discovery must commit to A and eat one unit.
    model_a = build_model(
        student,
        N=1,
        alpha_A=1,
        alpha_B=0,
        beta_A=0,
        beta_B=0,
        lambda_A=0,
        lambda_B=0,
        seed=3,
    )
    ant_a = all_ants(model_a)[0]
    model_a.grid.move_agent(ant_a, model_a.food_locs[0])
    before_a = model_a.foods[0].amount
    ant_a.step()
    assert_state(ant_a, "COMMITTED A", "ant at feeder A")
    if model_a.foods[0].amount != before_a - 1:
        raise AssertionError("An uncommitted ant that discovers feeder A should eat one food unit before/while committing")
    assert_tandem(ant_a, False, "ant at feeder A")

    # Feeder B: alpha_B = 1, so discovery must commit to B and eat one unit.
    model_b = build_model(
        student,
        N=1,
        alpha_A=0,
        alpha_B=1,
        beta_A=0,
        beta_B=0,
        lambda_A=0,
        lambda_B=0,
        seed=4,
    )
    ant_b = all_ants(model_b)[0]
    model_b.grid.move_agent(ant_b, model_b.food_locs[1])
    before_b = model_b.foods[1].amount
    ant_b.step()
    assert_state(ant_b, "COMMITTED B", "ant at feeder B")
    if model_b.foods[1].amount != before_b - 1:
        raise AssertionError("An uncommitted ant that discovers feeder B should eat one food unit before/while committing")
    assert_tandem(ant_b, False, "ant at feeder B")


def check_attrition(student) -> None:
    model = build_model(
        student,
        N=1,
        alpha_A=0,
        alpha_B=0,
        beta_A=0,
        beta_B=0,
        lambda_A=1,
        lambda_B=1,
        seed=5,
    )
    ant = all_ants(model)[0]
    ant.state = "COMMITTED A"
    ant.tandem_running = False
    start = ant.pos
    ant.step()
    assert_state(ant, "UNCOMMITTED", "committed A ant with lambda_A=1")
    assert_tandem(ant, False, "committed A ant with lambda_A=1")

    ant.state = "COMMITTED B"
    ant.tandem_running = True
    model.grid.move_agent(ant, start)
    ant.step()
    assert_state(ant, "UNCOMMITTED", "committed B ant with lambda_B=1")
    assert_tandem(ant, False, "committed B ant with lambda_B=1")


def check_tandem_movement_and_eating(student) -> None:
    model = build_model(
        student,
        N=1,
        alpha_A=0,
        alpha_B=0,
        beta_A=0,
        beta_B=0,
        lambda_A=0,
        lambda_B=0,
        seed=6,
    )
    ant = all_ants(model)[0]

    ant.state = "COMMITTED A"
    ant.tandem_running = True
    model.grid.move_agent(ant, (25, 5))
    target_a = model.food_locs[0]
    before_distance = get_distance(ant.pos, target_a)
    ant.step()
    after_distance = get_distance(ant.pos, target_a)
    assert_state(ant, "COMMITTED A", "tandem-running A ant")
    assert_tandem(ant, True, "tandem-running A ant not yet at food")
    if after_distance >= before_distance:
        raise AssertionError(
            f"A tandem-running ant committed to feeder A should move closer to {target_a}; "
            f"distance was {before_distance:.3f}, now {after_distance:.3f}"
        )

    model.grid.move_agent(ant, target_a)
    before_food = model.foods[0].amount
    ant.step()
    assert_state(ant, "COMMITTED A", "tandem-running A ant at food")
    assert_tandem(ant, False, "tandem-running A ant at food")
    if model.foods[0].amount != before_food - 1:
        raise AssertionError("A tandem-running ant at feeder A should eat one food unit")

    ant.state = "COMMITTED B"
    ant.tandem_running = True
    model.grid.move_agent(ant, (25, 5))
    target_b = model.food_locs[1]
    before_distance = get_distance(ant.pos, target_b)
    ant.step()
    after_distance = get_distance(ant.pos, target_b)
    assert_state(ant, "COMMITTED B", "tandem-running B ant")
    assert_tandem(ant, True, "tandem-running B ant not yet at food")
    if after_distance >= before_distance:
        raise AssertionError(
            f"A tandem-running ant committed to feeder B should move closer to {target_b}; "
            f"distance was {before_distance:.3f}, now {after_distance:.3f}"
        )


def check_recruitment(student) -> None:
    model_a = build_model(
        student,
        N=2,
        alpha_A=0,
        alpha_B=0,
        beta_A=1,
        beta_B=0,
        lambda_A=0,
        lambda_B=0,
        seed=7,
    )
    recruiter_a, recruit_a = all_ants(model_a)
    meeting_spot = (20, 20)
    model_a.grid.move_agent(recruiter_a, meeting_spot)
    model_a.grid.move_agent(recruit_a, meeting_spot)
    recruiter_a.state = "COMMITTED A"
    recruiter_a.tandem_running = False
    recruit_a.state = "UNCOMMITTED"
    recruit_a.tandem_running = False
    recruiter_a.step()
    assert_state(recruiter_a, "COMMITTED A", "A recruiter")
    assert_state(recruit_a, "COMMITTED A", "A recruit")
    assert_tandem(recruiter_a, True, "A recruiter")
    assert_tandem(recruit_a, True, "A recruit")

    model_b = build_model(
        student,
        N=2,
        alpha_A=0,
        alpha_B=0,
        beta_A=0,
        beta_B=1,
        lambda_A=0,
        lambda_B=0,
        seed=8,
    )
    recruiter_b, recruit_b = all_ants(model_b)
    model_b.grid.move_agent(recruiter_b, meeting_spot)
    model_b.grid.move_agent(recruit_b, meeting_spot)
    recruiter_b.state = "COMMITTED B"
    recruiter_b.tandem_running = False
    recruit_b.state = "UNCOMMITTED"
    recruit_b.tandem_running = False
    recruiter_b.step()
    assert_state(recruiter_b, "COMMITTED B", "B recruiter")
    assert_state(recruit_b, "COMMITTED B", "B recruit")
    assert_tandem(recruiter_b, True, "B recruiter")
    assert_tandem(recruit_b, True, "B recruit")


def check_model_integration(student) -> None:
    model = build_model(
        student,
        N=6,
        alpha_A=1,
        alpha_B=1,
        beta_A=1,
        beta_B=1,
        lambda_A=0,
        lambda_B=0,
        seed=9,
    )
    # Create a deterministic mini-simulation in the original 50x50 world.
    for food in model.foods:
        food.amount = 3
    ants = all_ants(model)
    for i, ant in enumerate(ants):
        model.grid.move_agent(ant, model.food_locs[0] if i < 3 else model.food_locs[1])
        ant.state = "UNCOMMITTED"
        ant.tandem_running = False

    model.step()
    if model.foods[0].amount > 0 and model.foods[1].amount > 0:
        # Depending on schedule order, one more step may be needed for all ants.
        model.step()
    if model.foods[0].amount != 0 or model.foods[1].amount != 0:
        raise AssertionError(
            "The full AntModel should run without errors and allow ants at feeders to consume food; "
            f"remaining food is A={model.foods[0].amount}, B={model.foods[1].amount}"
        )
    if len(model.dc.model_vars) == 0:
        raise AssertionError("AntModel.step() should collect feeder amounts with DataCollector")
    if model.running:
        raise AssertionError("AntModel.running should become False when a feeder is depleted")


@dataclass
class GradedCheck:
    name: str
    max_score: float
    func: Callable[[object], None]


def build_checks() -> List[GradedCheck]:
    return [
        GradedCheck("Q1 Ant constructor and required fields", 15, check_constructor),
        GradedCheck("Q1 uncommitted random movement", 10, check_uncommitted_random_move),
        GradedCheck("Q1 discovery, eating, and commitment at feeders", 20, check_discovery_and_commitment),
        GradedCheck("Q1 attrition/uncommit behavior", 15, check_attrition),
        GradedCheck("Q1 tandem movement and eating behavior", 20, check_tandem_movement_and_eating),
        GradedCheck("Q1 recruitment behavior", 15, check_recruitment),
        GradedCheck("Q1 full AntModel integration smoke test", 5, check_model_integration),
    ]


def result_entry(name: str, score: float, max_score: float, output: str) -> dict:
    return {
        "name": name,
        "score": score,
        "max_score": max_score,
        "output": output,
        "visibility": "visible",
    }


def write_results(payload: dict) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "results.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def main() -> int:
    tests = []
    total_score = 0.0
    max_score = 100.0

    try:
        submission_file = os.path.join(SUBMISSION_DIR, "student_solution.py")
        if not os.path.isfile(submission_file):
            py_files = sorted(name for name in os.listdir(SUBMISSION_DIR) if name.endswith(".py"))
            if len(py_files) == 1:
                submission_file = os.path.join(SUBMISSION_DIR, py_files[0])
            else:
                raise FileNotFoundError(
                    "Submit exactly one Python file named student_solution.py. "
                    f"Found Python files: {py_files}"
                )
        spec = importlib.util.spec_from_file_location("student_solution", submission_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load {submission_file}")
        student = importlib.util.module_from_spec(spec)
        sys.modules["student_solution"] = student
        spec.loader.exec_module(student)
        prepare_student_module(student)
    except Exception:
        output = (
            "Could not import student_solution.py. Make sure the file is named student_solution.py, "
            "defines class Ant, and does not run long notebook/demo code during import.\n\n"
        )
        output += traceback.format_exc(limit=20)
        payload = {
            "score": 0,
            "visibility": "visible",
            "stdout_visibility": "visible",
            "output": output,
            "tests": [result_entry("Import student_solution.py", 0, max_score, output)],
        }
        write_results(payload)
        print(output)
        return 0

    for check in build_checks():
        try:
            run_with_timeout(lambda check=check: check.func(student), seconds=25)
        except Exception:
            output = traceback.format_exc(limit=8)
            tests.append(result_entry(check.name, 0, check.max_score, output))
            print(f"FAIL: {check.name}\n{output}")
        else:
            tests.append(result_entry(check.name, check.max_score, check.max_score, "Passed"))
            total_score += check.max_score
            print(f"PASS: {check.name}")

    payload = {
        "score": total_score,
        "visibility": "visible",
        "stdout_visibility": "visible",
        "output": f"Project 05 autograder score: {total_score:.1f} / {max_score:.1f}",
        "tests": tests,
    }
    write_results(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
