# rcf — Relativistic Cognitive Field, reference implementation

Activation of a stored pattern `P_i` for a query `Q`:

```
E(P_i, Q) = m_i * gamma_i(Q) / (sum_j g_j(Q) (q_j - p_ij)^2 + eps) * exp(-lambda_i * dt_i)

gamma_i(Q) = sigma_i(Q) * (1 + beta * kappa_i(Q)),  sigma in {-1, +1}, kappa in [0, 1]
lambda_i   = lambda0 / (1 + m_i / m_ref)
dt_i       = now - last_reinforced_i
```

Retrieval ranks by `|E|`. The label of each active-set member comes from the supplied assessment (`active_set(E, k, sigma=..., assessed=...)`) and is `"unassessed"` when none is supplied; it is never taken from `sign(E)`. `preselect_candidates` gives the exact candidate set for the top-`k`; `touch` resets a pattern's clock; `validate` records a human validation event that the caller reports (the library does not authenticate a human) and adds mass (positive only); `reinforce(idx, now, mass_delta)` is the shared primitive behind both, and a positive `mass_delta` through it counts as a validation. Masses below the ingestion floor `m_min` (the paper's $m_0$, default 0.01) are rejected.

## Install

```
pip install -e ".[dev]"
```

## Test

```
pytest
```

## Worked example (figure + tables used in the paper)

```
python examples/worked_example.py out
```

Writes `out/field.pdf`, `out/field.png`, `out/results.json` and the `table_*.tex` files.
