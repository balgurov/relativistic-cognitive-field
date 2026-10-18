import numpy as np
import pytest

from rcf import Field, activation, active_set, preselect_candidates, trace_normalized, valence, warped_distance


def unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def random_field(rng, n=50, d=16, eps=0.1, beta=1.0, lambda0=0.01):
    coords = unit(rng.normal(size=(n, d)))
    mass = rng.uniform(0.01, 100.0, size=n)
    return Field(coords, mass, np.zeros(n), lambda0=lambda0, mass_ref=1.0, eps=eps, beta=beta)


def test_bounded_by_mass_valence_over_eps():
    rng = np.random.default_rng(0)
    f = random_field(rng)
    q = unit(rng.normal(size=f.dim))
    sigma = rng.choice([-1.0, 1.0], size=f.n)
    kappa = rng.uniform(0.0, 1.0, size=f.n)
    E = activation(f, q, now=5.0, sigma=sigma, kappa=kappa)
    bound = f.mass.max() * (1.0 + f.beta) / f.eps
    assert np.all(np.abs(E) <= bound + 1e-12)
    assert np.all(np.isfinite(E))


def test_reduces_to_cosine_ranking():
    rng = np.random.default_rng(1)
    n, d = 40, 16
    coords = unit(rng.normal(size=(n, d)))
    f = Field(coords, np.ones(n), np.zeros(n), eps=0.1)
    q = unit(rng.normal(size=d))
    E = activation(f, q, now=0.0)
    cos = coords @ q
    assert np.array_equal(np.argsort(-E), np.argsort(-cos))
    d2 = warped_distance(q, coords)
    assert np.allclose(d2, 2.0 * (1.0 - cos))


def test_log_linear_decomposition():
    rng = np.random.default_rng(2)
    f = random_field(rng, n=10, d=4)
    f.mass = f.mass + 1.0
    q = rng.normal(size=f.dim)
    g = trace_normalized(rng.uniform(0.1, 2.0, size=f.dim))
    sigma = rng.choice([-1.0, 1.0], size=f.n)
    kappa = rng.uniform(0.0, 1.0, size=f.n)
    now = 7.0
    E = activation(f, q, now, g=g, sigma=sigma, kappa=kappa)
    gamma = valence(sigma, kappa, f.beta)
    expected = (
        np.log(f.mass)
        + np.log(np.abs(gamma))
        - np.log(warped_distance(q, f.coords, g) + f.eps)
        - f.decay_rate() * (now - f.last_reinforced)
    )
    assert np.allclose(np.log(np.abs(E)), expected)
    assert np.array_equal(np.sign(E), sigma)


def test_contradiction_enters_active_set_by_magnitude():
    coords = np.array([[0.0], [0.2], [0.25], [0.4], [0.6], [0.8]])
    f = Field(coords, np.ones(6), np.zeros(6), eps=0.1, beta=1.0)
    sigma = np.array([1.0, 1.0, -1.0, 1.0, 1.0, 1.0])
    kappa = np.array([0.0, 1.0, 1.0, 0.0, 0.0, 0.0])
    E = activation(f, q=np.array([0.0]), now=0.0, sigma=sigma, kappa=kappa)
    assert int(np.argsort(-E)[-1]) == 2
    order, signs = active_set(E, 3, sigma=sigma, assessed=np.ones(6, dtype=bool))
    assert 2 in order
    assert signs[list(order).index(2)] == -1


def test_negative_metric_weight_rejected():
    with pytest.raises(ValueError):
        warped_distance(np.zeros(2), np.ones((3, 2)), g=np.array([1.0, -1.0]))
    with pytest.raises(ValueError):
        trace_normalized([1.0, -0.5])


def test_valence_domain_checked():
    with pytest.raises(ValueError):
        valence([0.5], [0.0], 1.0)
    with pytest.raises(ValueError):
        valence([1.0], [1.5], 1.0)
    assert np.allclose(valence([1.0, -1.0], [0.0, 1.0], 2.0), [1.0, -3.0])


def test_trace_normalization():
    g = trace_normalized([3.0, 1.0, 0.0, 0.0])
    assert np.isclose(g.sum(), 4.0)
    assert np.allclose(g, [3.0, 1.0, 0.0, 0.0])


def test_decay_monotone_and_mass_dependent():
    coords = np.zeros((2, 2))
    f = Field(coords, np.array([1.0, 50.0]), np.zeros(2), lambda0=0.02, mass_ref=1.0, eps=0.1)
    q = np.zeros(2)
    e0 = activation(f, q, now=0.0)
    e1 = activation(f, q, now=60.0)
    ratio = e1 / e0
    assert ratio[0] < ratio[1] < 1.0
    assert np.isclose(ratio[0], np.exp(-0.01 * 60.0))
    assert np.isclose(ratio[1], np.exp(-0.02 / 51.0 * 60.0))
    with pytest.raises(ValueError):
        activation(f, q, now=-1.0)


def test_reinforcement_resets_clock_and_adds_mass():
    coords = np.zeros((2, 1))
    f = Field(coords, np.ones(2), np.zeros(2), lambda0=0.02, eps=0.1)
    f.validate(1, now=30.0, mass_delta=0.5)
    e = activation(f, q=np.zeros(1), now=60.0)
    assert e[1] > e[0]
    assert f.last_reinforced[1] == 30.0
    assert f.mass[1] == 1.5
    f.touch(0, now=45.0)
    assert f.last_reinforced[0] == 45.0 and f.mass[0] == 1.0
    with pytest.raises(ValueError):
        f.reinforce(0, now=50.0, mass_delta=-0.5)
    with pytest.raises(ValueError):
        f.validate(0, now=50.0, mass_delta=0.0)
    with pytest.raises(ValueError):
        f.touch(0, now=10.0)


def test_eps_sets_mass_proximity_exchange_rate():
    coords = np.array([[0.0], [1.0]])
    q = np.array([0.0])
    for eps in (0.1, 1.0):
        threshold = (1.0 + eps) / eps
        for M in (threshold * 0.9, threshold * 1.1):
            f = Field(coords, np.array([1.0, M]), np.zeros(2), eps=eps)
            E = activation(f, q, now=0.0)
            assert (E[1] > E[0]) == (M > threshold)


def test_invalid_field_construction():
    with pytest.raises(ValueError):
        Field(np.zeros((2, 2)), np.array([1.0, -1.0]), np.zeros(2))
    with pytest.raises(ValueError):
        Field(np.zeros((2, 2)), np.ones(2), np.zeros(2), eps=0.0)
    with pytest.raises(ValueError):
        Field(np.zeros((2, 2)), np.ones(3), np.zeros(2))
    with pytest.raises(ValueError):
        Field(np.zeros((2, 2)), np.array([1.0, 0.001]), np.zeros(2))
    with pytest.raises(ValueError):
        Field(np.zeros((2, 2)), np.ones(2), np.array([0.0, 5.0]), now=4.0)
    with pytest.raises(ValueError):
        Field(np.zeros((2, 2)), np.array([1.0, np.inf]), np.zeros(2))


def test_labels_come_from_assessment_not_sign():
    E = np.array([3.0, -2.0, 0.0, 1.0])
    order, labels = active_set(E, 4)
    assert labels == ["unassessed"] * 4
    order, labels = active_set(E, 4, sigma=[1.0, -1.0, -1.0, 1.0], assessed=[True, True, True, False])
    assert list(order) == [0, 1, 3, 2]
    assert labels == [1, -1, "unassessed", -1]
    with pytest.raises(ValueError):
        active_set(E, 4, sigma=[0.5, -1.0, -1.0, 1.0], assessed=[True, True, True, False])


def test_non_finite_inputs_rejected():
    f = Field(np.zeros((2, 2)), np.ones(2), np.zeros(2))
    with pytest.raises(ValueError):
        activation(f, q=np.array([np.nan, 0.0]), now=0.0)
    with pytest.raises(ValueError):
        activation(f, q=np.zeros(2), now=0.0, g=np.array([np.inf, 1.0]))
    with pytest.raises(ValueError):
        activation(f, q=np.zeros(2), now=np.nan)
    with pytest.raises(ValueError):
        activation(f, q=np.zeros(2), now=0.0, sigma=[1.0, 1.0], kappa=[np.nan, 0.0])
    with pytest.raises(ValueError):
        f.touch(0, now=np.nan)
    with pytest.raises(ValueError):
        f.validate(0, now=1.0, mass_delta=np.inf)
    with pytest.raises(ValueError):
        Field(np.zeros((2, 2)), np.ones(2), np.zeros(2), eps=np.nan)
    with pytest.raises(ValueError):
        trace_normalized([np.nan, 1.0])
    with pytest.raises(ValueError):
        valence([1.0], [0.0], beta=np.nan)
    with pytest.raises(ValueError):
        active_set([np.nan, 1.0], 1)


def test_preselect_candidates_is_exact():
    rng = np.random.default_rng(3)
    f = random_field(rng, n=60, d=8, beta=1.0)
    q = unit(rng.normal(size=f.dim))
    k = 5
    cand = preselect_candidates(f, q, now=0.0, k=k)
    sigma = rng.choice([-1.0, 1.0], size=f.n)
    for _ in range(20):
        kappa = rng.uniform(0.0, 1.0, size=f.n)
        E = activation(f, q, now=0.0, sigma=sigma, kappa=kappa)
        top, _ = active_set(E, k)
        assert set(top) <= set(cand)
