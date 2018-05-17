#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `dtmc` package."""

import pytest


from dtmc import DiscreteTimeMarkovChain

import numpy as np

market_p = [[0.9, 0.075, 0.025], [0.15, 0.8, 0.05], [0.25, 0.25, 0.5]]
market_labels = ('bull', 'bear', 'stagnant')
market_chain = DiscreteTimeMarkovChain(market_p, market_labels)

weather_p = [[0.9, 0.1], [0.5, 0.5]]
weather_labels = ('sunny', 'rainy')
weather_chain = DiscreteTimeMarkovChain(weather_p, weather_labels)

sigman_p = [[1/2.0, 1/2.0, 0, 0],
            [1/2.0, 1/2.0, 0, 0],
            [1/3.0, 1/6.0, 1/6.0, 1/3.0],
            [0, 0, 0, 1]]
sigman_chain = DiscreteTimeMarkovChain(sigman_p)

periodic_p = [[0, 0, 1/2.0, 1/4.0, 1/4.0, 0, 0],
              [0, 0, 1/3.0, 0, 2/3.0, 0, 0],
              [0, 0, 0, 0, 0, 1/3.0, 2/3.0],
              [0, 0, 0, 0, 0, 1/2.0, 1/2.0],
              [0, 0, 0, 0, 0, 3/4.0, 1/4.0],
              [1/2.0, 1/2.0, 0, 0, 0, 0, 0],
              [1/4.0, 3/4.0, 0, 0, 0, 0, 0]]
periodic_chain = DiscreteTimeMarkovChain(periodic_p)

ravner_p = [[0, 1, 0, 0, 0, 0],
            [0.4, 0.6, 0, 0, 0, 0],
            [0.3, 0, 0.4, 0.2, 0.1, 0],
            [0, 0, 0, 0.3, 0.7, 0],
            [0, 0, 0, 0.5, 0, 0.5],
            [0, 0, 0, 0.3, 0, 0.7]]
ravner_chain = DiscreteTimeMarkovChain(ravner_p)


def random_markov_matrix(size):
    mat = np.random.rand(size, size)
    row_sums = mat.sum(axis=1, keepdims=True)
    return mat / row_sums


# ---- Random markov matrix is valid ----
def test_random_markov_matrix():
    DiscreteTimeMarkovChain(random_markov_matrix(10))


# ---- Acceptance of valid transition matrices ----

valid_chains = [
    (market_p, market_labels),
    (weather_p, weather_labels),
    (sigman_p, None),
    (periodic_p, None),
    (np.eye(10), None),
    (np.eye(10).T, None),
    (ravner_p, None)
]


@pytest.mark.parametrize('matrix, labels', valid_chains)
def test_accept_valid_chain(matrix, labels):
    DiscreteTimeMarkovChain(matrix, labels)


# ---- Rejection of invalid transition matrices ----

bad_chains = [
    (market_p, weather_labels),
    (weather_p, market_labels),
    (-1 * np.eye(10), None),
    (np.zeros((5, 4)), None),
    (np.eye(10) + np.eye(10).T, None),
    (np.eye(3), ['a', 'b', 'a'])
]


@pytest.mark.parametrize('matrix, labels', bad_chains)
def test_reject_bad_chain(matrix, labels):
    with pytest.raises(ValueError):
        DiscreteTimeMarkovChain(matrix, labels)


# ---- Test absorbing states ----

def test_all_absorbing():
    mc = DiscreteTimeMarkovChain(np.eye(10))
    assert np.array_equal(mc.absorbing_states(), np.arange(10))


def test_all_absorbing_labelled():
    labels = [str(i) for i in range(10)]
    mc = DiscreteTimeMarkovChain(np.eye(10), labels)
    assert mc.absorbing_states() == labels


# ---- Test communicating classes ---

def test_multiple_communicating_classes():
    classes = map(tuple, sigman_chain.communicating_classes())
    expected_classes = map(tuple, [{0, 1}, {2}, {3}])
    assert sorted(classes) == sorted(expected_classes)


# ---- Test irreducibility ----

reducible_chains = [
    (sigman_p, None),
    (np.eye(10), None)
]
irreducible_chains = [
    (market_p, market_labels),
    (weather_p, weather_labels)
]


@pytest.mark.parametrize('matrix, labels', reducible_chains)
def test_reducible_chain(matrix, labels):
    assert DiscreteTimeMarkovChain(matrix, labels).is_reducible()


@pytest.mark.parametrize('matrix, labels', irreducible_chains)
def test_irreducible_chain(matrix, labels):
    assert DiscreteTimeMarkovChain(matrix, labels).is_irreducible()


# ---- Test periodicity ----
def test_aperiodic_chain():
    assert weather_chain.period('sunny') == 1
    assert market_chain.period('bull') == 1


def test_periodic_chain():
    assert periodic_chain.period(0) == 3


# ---- Test transience and recurrence ----

def test_transient_classes():
    mc = DiscreteTimeMarkovChain(ravner_p)
    t_classes = mc.transient_classes()
    assert t_classes == [{2}]


def test_recurrent_classes():
    mc = DiscreteTimeMarkovChain(ravner_p)
    r_classes = mc.recurrent_classes()
    assert r_classes == [{0, 1}, {3, 4, 5}]


def test_transient_states():
    mc = DiscreteTimeMarkovChain(ravner_p)
    t_states = mc.transient_states()
    assert t_states == {2}


def test_recurrent_states():
    mc = DiscreteTimeMarkovChain(ravner_p)
    r_states = mc.recurrent_states()
    assert r_states == {0, 1, 3, 4, 5}


# ---- Test steady state distribution ----

fenix_p = [[0.8, 0.2],
           [0.4, 0.6]]


def test_steady_state():
    mc = DiscreteTimeMarkovChain(fenix_p)
    assert np.allclose(mc.steady_states(), [2/3.0, 1/3.0])
