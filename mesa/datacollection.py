"""Minimal DataCollector implementation for Project 05."""

from __future__ import annotations


class _SimpleDataFrame(list):
    @property
    def shape(self):
        return (len(self), len(self[0]) if self else 0)

    def to_dict(self, *args, **kwargs):
        return list(self)


class DataCollector:
    def __init__(self, model_reporters=None, **kwargs):
        self.model_reporters = model_reporters or {}
        self.model_vars = []

    def collect(self, model):
        row = {}
        for name, reporter in self.model_reporters.items():
            if callable(reporter):
                row[name] = reporter(model)
            else:
                row[name] = getattr(model, reporter)
        self.model_vars.append(row)

    def get_model_vars_dataframe(self):
        try:
            import pandas as pd
            return pd.DataFrame(self.model_vars)
        except Exception:
            return _SimpleDataFrame(self.model_vars)
