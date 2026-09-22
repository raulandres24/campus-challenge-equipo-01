"""Pruebas iniciales.

Comprueban solo algunos de los comportamientos requeridos.
"""

from challenge_tools import (
    average_score,
    normalize_answer,
    rank_teams,
    round_score_to_ten,
    unique_tags,
)


def test_normalize_answer_removes_outer_spaces():
    assert normalize_answer("  Python  ") == "python"


def test_normalize_answer_supports_unicode_caseless_matching():
    assert normalize_answer("STRAẞE") == "strasse"


def test_round_score_handles_value_below_halfway():
    assert round_score_to_ten(21) == 20


def test_round_score_handles_second_value_below_halfway():
    assert round_score_to_ten(24) == 20


def test_rank_teams_orders_different_scores():
    assert rank_teams([("Beta", 10), ("Alpha", 30)]) == [
        ("Alpha", 30),
        ("Beta", 10),
    ]


def test_unique_tags_accepts_empty_input():
    assert unique_tags([]) == []


def test_average_score_handles_nonempty_input():
    assert average_score([10, 20, 30]) == 20