from __future__ import annotations

from dataclasses import dataclass

import numpy as np

UNASSESSED = "unassessed"


def _finite(value, name: str) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


@dataclass
class Field:
    coords: np.ndarray
    mass: np.ndarray
    last_reinforced: np.ndarray
    lambda0: float = 0.01
    mass_ref: float = 1.0
    eps: float = 0.1
    beta: float = 1.0
    m_min: float = 0.01
    now: float | None = None

    def __post_init__(self) -> None:
        self.coords = np.asarray(self.coords, dtype=float)
        self.mass = np.asarray(self.mass, dtype=float)
        self.last_reinforced = np.asarray(self.last_reinforced, dtype=float)
        if self.coords.ndim != 2:
            raise ValueError("coords must have shape (n, d)")
        n = self.coords.shape[0]
        if self.mass.shape != (n,) or self.last_reinforced.shape != (n,):
            raise ValueError("mass and last_reinforced must have shape (n,)")
        if not (self.m_min > 0):
            raise ValueError("m_min must be positive")
        if np.any(self.mass < self.m_min):
            raise ValueError("mass must be at least the ingestion floor m_min")
        if self.eps <= 0:
            raise ValueError("eps must be positive")
        if self.lambda0 < 0 or self.beta < 0 or self.mass_ref <= 0:
            raise ValueError("lambda0 and beta must be non-negative, mass_ref positive")
        if not (np.all(np.isfinite(self.coords)) and np.all(np.isfinite(self.mass)) and np.all(np.isfinite(self.last_reinforced))):
            raise ValueError("coords, mass and last_reinforced must be finite")
        for name in ("lambda0", "mass_ref", "eps", "beta", "m_min"):
            _finite(getattr(self, name), name)
        if self.now is not None:
            _finite(self.now, "now")
        if self.now is not None and np.any(self.last_reinforced > self.now):
            raise ValueError("last_reinforced must not be in the future at ingestion")

    @property
    def n(self) -> int:
        return self.coords.shape[0]

    @property
    def dim(self) -> int:
        return self.coords.shape[1]

    def decay_rate(self) -> np.ndarray:
        return self.lambda0 / (1.0 + self.mass / self.mass_ref)

    def reinforce(self, idx, now: float, mass_delta: float = 0.0) -> None:
        _finite(now, "now")
        _finite(mass_delta, "mass_delta")
        if mass_delta < 0:
            raise ValueError("mass_delta must be non-negative")
        if np.any(self.last_reinforced[idx] > now):
            raise ValueError("now must not precede the current reinforcement time")
        self.last_reinforced[idx] = now
        self.mass[idx] = self.mass[idx] + mass_delta

    def touch(self, idx, now: float) -> None:
        self.reinforce(idx, now, 0.0)

    def validate(self, idx, now: float, mass_delta: float = 1.0) -> None:
        if not (mass_delta > 0):
            raise ValueError("a validation must add positive mass")
        self.reinforce(idx, now, mass_delta)


def warped_distance(q, coords, g=None) -> np.ndarray:
    q = _finite(q, "q")
    coords = _finite(coords, "coords")
    diff = coords - q
    if g is None:
        return np.sum(diff * diff, axis=-1)
    g = _finite(g, "g")
    if g.shape != q.shape:
        raise ValueError("g must have the same shape as q")
    if np.any(g < 0):
        raise ValueError("metric weights must be non-negative")
    return np.sum(g * diff * diff, axis=-1)


def trace_normalized(weights) -> np.ndarray:
    w = _finite(weights, "weights")
    if np.any(w < 0) or w.sum() <= 0:
        raise ValueError("weights must be non-negative with positive sum")
    return w * (w.size / w.sum())


def valence(sigma, kappa, beta: float) -> np.ndarray:
    sigma = _finite(sigma, "sigma")
    kappa = _finite(kappa, "kappa")
    _finite(beta, "beta")
    if not np.all(np.isin(sigma, (-1.0, 1.0))):
        raise ValueError("sigma must be -1 or +1")
    if np.any((kappa < 0) | (kappa > 1)):
        raise ValueError("kappa must lie in [0, 1]")
    return sigma * (1.0 + beta * kappa)


def activation(field: Field, q, now: float, g=None, sigma=None, kappa=None) -> np.ndarray:
    n = field.n
    sigma = np.ones(n) if sigma is None else sigma
    kappa = np.zeros(n) if kappa is None else kappa
    gamma = valence(sigma, kappa, field.beta)
    d2 = warped_distance(q, field.coords, g)
    dt = _finite(now, "now") - field.last_reinforced
    if np.any(dt < 0):
        raise ValueError("now must not precede any reinforcement time")
    decay = np.exp(-field.decay_rate() * dt)
    return field.mass * gamma / (d2 + field.eps) * decay


def preselect_candidates(field: Field, q, now: float, k: int, g=None) -> np.ndarray:
    s = np.abs(activation(field, q, now, g))
    if k <= 0 or s.size == 0:
        return np.zeros(0, dtype=int)
    kth = np.sort(s)[::-1][min(k, s.size) - 1]
    return np.flatnonzero(s >= kth / (1.0 + field.beta))


def active_set(E, k: int, sigma=None, assessed=None):
    E = _finite(E, "E")
    order = np.argsort(-np.abs(E), kind="stable")[:k]
    if sigma is None or assessed is None:
        return order, [UNASSESSED] * len(order)
    sigma = _finite(sigma, "sigma")
    assessed = np.asarray(assessed, dtype=bool)
    if sigma.shape != E.shape or assessed.shape != E.shape:
        raise ValueError("sigma and assessed must have the shape of E")
    if not np.all(np.isin(sigma[assessed], (-1.0, 1.0))):
        raise ValueError("assessed sigma values must be -1 or +1")
    return order, [int(sigma[i]) if assessed[i] else UNASSESSED for i in order]
