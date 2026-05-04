# tests/test_data_loader.py

import pandas as pd
import pytest
from tune_model import DataLoader

def test_load_training_data_happy_path(monkeypatch):
    fake_df = pd.DataFrame({
        "is_verified": [1, 0, 1],
        "days_since_last_login": [5, 30, 50],
        "login_count_7d": [3, 0, 1],
        "failed_login_attempts": [0, 4, 1],
        "feature_a": [0.1, 0.2, 0.3],
        "feature_b": [1, 2, 3],
    })

    monkeypatch.setattr(
        "src.tune_model.FEATURE_COLUMNS",
        ["feature_a", "feature_b"]
    )

    def fake_read_sql(query, conn):
        return fake_df

    monkeypatch.setattr("pandas.read_sql", fake_read_sql)

    loader = DataLoader("sqlite:///fake.db")
    X, y = loader.load_training_data()

    assert list(X.columns) == ["feature_a", "feature_b"]
    assert len(X) == 3
    assert len(y) == 3
    assert set(y.unique()).issubset({0, 1})


def test_load_training_data_empty_table(monkeypatch):
    fake_df = pd.DataFrame()

    def fake_read_sql(query, conn):
        return fake_df

    monkeypatch.setattr("pandas.read_sql", fake_read_sql)

    loader = DataLoader("sqlite:///fake.db")

    with pytest.raises(RuntimeError, match="customer_features table is empty"):
        loader.load_training_data()


def test_load_training_data_missing_required_columns(monkeypatch):
    fake_df = pd.DataFrame({
        "days_since_last_login": [1, 2],
        "login_count_7d": [0, 1],
    })

    def fake_read_sql(query, conn):
        return fake_df

    monkeypatch.setattr("pandas.read_sql", fake_read_sql)

    loader = DataLoader("sqlite:///fake.db")

    with pytest.raises(KeyError, match="Missing required columns"):
        loader.load_training_data()


def test_load_training_data_missing_feature_columns(monkeypatch):
    fake_df = pd.DataFrame({
        "is_verified": [1, 0],
        "days_since_last_login": [1, 2],
        "login_count_7d": [0, 1],
        "failed_login_attempts": [0, 2],
    })

    monkeypatch.setattr(
        "src.tune_model.FEATURE_COLUMNS",
        ["feature_a", "feature_b"]
    )

    def fake_read_sql(query, conn):
        return fake_df

    monkeypatch.setattr("pandas.read_sql", fake_read_sql)

    loader = DataLoader("sqlite:///fake.db")

    with pytest.raises(KeyError, match="Missing FEATURE_COLUMNS"):
        loader.load_training_data()