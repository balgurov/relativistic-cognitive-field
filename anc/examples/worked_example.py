from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from rcf import Field, activation, active_set, trace_normalized, warped_distance


def unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def kendall_tau(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    n = len(a)
    s = 0
    for i in range(n):
        for j in range(i + 1, n):
            s += np.sign(a[i] - a[j]) * np.sign(b[i] - b[j])
    return s / (n * (n - 1) / 2)


def scene():
    coords = np.array(
        [
            [1.2, 0.3],
            [0.15, 0.1],
            [0.5, -0.4],
            [0.6, -0.6],
            [0.3, 1.6],
            [-0.9, 0.8],
        ]
    )
    mass = np.array([40.0, 1.0, 5.0, 5.0, 8.0, 3.0])
    last = np.array([0.0, 0.0, 0.0, 0.0, 0.0, -300.0])
    labels = ["anchor rule", "unverified near-duplicate", "thesis", "antithesis", "off-axis evidence", "stale entry"]
    sigma = np.array([1.0, 1.0, 1.0, -1.0, 1.0, 1.0])
    kappa = np.array([0.0, 0.0, 1.0, 1.0, 0.0, 0.0])
    return Field(coords, mass, last, lambda0=0.02, mass_ref=1.0, eps=0.1, beta=1.0), labels, sigma, kappa


def field_intensity(f, g, sigma, kappa, xs, ys, now=0.0):
    phi = np.zeros((len(ys), len(xs)))
    for i, y in enumerate(ys):
        for j, x in enumerate(xs):
            phi[i, j] = np.abs(activation(f, np.array([x, y]), now, g=g, sigma=sigma, kappa=kappa)).sum()
    return phi


def figure(out: Path):
    f, labels, sigma, kappa = scene()
    xs = np.linspace(-1.6, 2.0, 181)
    ys = np.linspace(-1.4, 2.2, 181)
    metrics = [("(a) unwarped metric, $g=(1,1)$", None), ("(b) warped metric, $g=(1.8,\\,0.2)$", trace_normalized([1.8, 0.2]))]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=True)
    phis = [field_intensity(f, g, sigma, kappa, xs, ys) for _, g in metrics]
    vmin = min(p.min() for p in phis)
    vmax = max(p.max() for p in phis)
    for ax, (title, g), phi in zip(axes, metrics, phis):
        im = ax.pcolormesh(xs, ys, phi, cmap="Blues", norm=LogNorm(vmin=vmin, vmax=vmax), shading="auto", rasterized=True)
        ax.contour(xs, ys, np.log10(phi), levels=8, colors="#1f3b5c", linewidths=0.4, alpha=0.6)
        sizes = 18 + 4.0 * f.mass
        ax.scatter(f.coords[:, 0], f.coords[:, 1], s=sizes, facecolors="white", edgecolors="#1f3b5c", linewidths=0.9, zorder=3)
        ax.scatter([0.0], [0.0], marker="x", s=50, color="#b3261e", linewidths=1.4, zorder=4)
        ax.annotate("Q", (0.0, 0.0), xytext=(-0.22, -0.28), fontsize=8, color="#b3261e")
        offsets = [(6, 4, "left"), (-3, 9, "right"), (6, 2, "left"), (6, -8, "left"), (6, 2, "left"), (6, 2, "left")]
        for (x, y), lab, s, (dx, dy, ha) in zip(f.coords, labels, sigma, offsets):
            tag = f"{lab} ($\\sigma=-1$)" if s < 0 else lab
            ax.annotate(tag, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=6.5, color="#222222", ha=ha)
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("axis 1 (domain-relevant)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_aspect("equal")
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    axes[0].set_ylabel("axis 2", fontsize=8)
    cbar = fig.colorbar(im, ax=axes, shrink=0.85, pad=0.02)
    cbar.set_label(r"field intensity $\Phi(q)=\sum_i |E(P_i,q)|$", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    fig.savefig(out / "field.pdf", bbox_inches="tight", pad_inches=0.08, dpi=200)
    fig.savefig(out / "field.png", bbox_inches="tight", pad_inches=0.08, dpi=200)
    plt.close(fig)


def scenario_reduction():
    rng = np.random.default_rng(7)
    n, d = 200, 32
    coords = unit(rng.normal(size=(n, d)))
    f = Field(coords, np.ones(n), np.zeros(n), eps=0.1)
    taus = []
    for _ in range(20):
        q = unit(rng.normal(size=d))
        E = activation(f, q, now=0.0)
        taus.append(kendall_tau(np.argsort(np.argsort(-E)), np.argsort(np.argsort(-(coords @ q)))))
    return {"n": n, "d": d, "queries": 20, "kendall_tau_min": float(min(taus)), "kendall_tau_mean": float(np.mean(taus))}


def scenario_exchange_rate():
    rows = []
    for eps in (0.01, 0.1, 1.0):
        threshold = (1.0 + eps) / eps
        for M in (5.0, 20.0, 200.0):
            f = Field(np.array([[0.0], [1.0]]), np.array([1.0, M]), np.zeros(2), eps=eps)
            E = activation(f, np.array([0.0]), now=0.0)
            rows.append({"eps": eps, "threshold": threshold, "M": M, "E_duplicate": float(E[0]), "E_anchor": float(E[1]), "winner": "anchor" if E[1] > E[0] else "duplicate"})
    return rows


def scenario_valence():
    f, labels, sigma, kappa = scene()
    q = np.array([0.0, 0.0])
    E = activation(f, q, now=0.0, sigma=sigma, kappa=kappa)
    by_signed = [labels[i] for i in np.argsort(-E)]
    order, signs = active_set(E, k=6, sigma=sigma, assessed=np.ones(len(sigma), dtype=bool))
    by_magnitude = [labels[i] for i in order]
    return {
        "E": {labels[i]: float(E[i]) for i in range(len(labels))},
        "rank_by_signed_E": by_signed,
        "rank_by_abs_E": by_magnitude,
        "antithesis_rank_signed": by_signed.index("antithesis") + 1,
        "antithesis_rank_abs": by_magnitude.index("antithesis") + 1,
        "valence_labels": {labels[i]: s for i, s in zip(order, signs)},
    }


def scenario_decay():
    f = Field(np.zeros((3, 1)), np.array([1.0, 1.0, 50.0]), np.zeros(3), lambda0=0.02, mass_ref=1.0, eps=0.1)
    q = np.zeros(1)
    e0 = activation(f, q, now=0.0)
    f.reinforce(1, now=30.0)
    e60 = activation(f, q, now=60.0)
    return {
        "lambda_i": f.decay_rate().tolist(),
        "retained_fraction_at_t60": (e60 / e0).tolist(),
        "labels": ["m=1, never reinforced", "m=1, reinforced at t=30", "m=50 anchor, never reinforced"],
    }


def scenario_concentration():
    rng = np.random.default_rng(11)
    rows = []
    eps = 0.1
    for d in (2, 8, 32, 128, 512, 2048):
        coords = unit(rng.normal(size=(2000, d)))
        q = unit(rng.normal(size=d))
        d2 = warped_distance(q, coords)
        term = -np.log(d2 + eps)
        rows.append({"d": d, "d2_min": float(d2.min()), "d2_max": float(d2.max()), "d2_mean": float(d2.mean()), "relative_spread": float((d2.max() - d2.min()) / d2.mean()), "distance_term_range_nats": float(term.max() - term.min())})
    return {"rows": rows, "mass_range_1_to_100_nats": float(np.log(100.0))}


def scenario_warp():
    f, labels, sigma, kappa = scene()
    q = np.array([0.0, 0.0])
    out = {}
    for name, g in (("unwarped", None), ("warped", trace_normalized([1.8, 0.2]))):
        d2 = warped_distance(q, f.coords, g)
        E = activation(f, q, now=0.0, g=g, sigma=sigma, kappa=kappa)
        order, _ = active_set(E, k=6, sigma=sigma, assessed=np.ones(len(sigma), dtype=bool))
        out[name] = {"d2": {labels[i]: float(d2[i]) for i in range(len(labels))}, "rank_by_abs_E": [labels[i] for i in order]}
    return out


def table(results, out: Path):
    v = results["valence"]
    dec = results["decay"]
    lines = []
    lines.append(r"\begin{tabular}{@{}llr@{}}")
    lines.append(r"\toprule")
    lines.append(r"Pattern & valence $\sigma$ & $E(P_i,Q)$ \\")
    lines.append(r"\midrule")
    for lab in v["rank_by_abs_E"]:
        s = "$-1$" if v["valence_labels"][lab] < 0 else "$+1$"
        lines.append(f"{lab} & {s} & ${v['E'][lab]:.2f}$ \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    (out / "table_valence.tex").write_text("\n".join(lines) + "\n")

    lines = []
    lines.append(r"\begin{tabular}{@{}rrrl@{}}")
    lines.append(r"\toprule")
    lines.append(r"$\epsilon$ & $(D+\epsilon)/\epsilon$ & $M$ & winner \\")
    lines.append(r"\midrule")
    for r in results["exchange_rate"]:
        lines.append(f"{r['eps']:g} & {r['threshold']:.0f} & {r['M']:g} & {r['winner']} \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    (out / "table_exchange.tex").write_text("\n".join(lines) + "\n")

    lines = []
    lines.append(r"\begin{tabular}{@{}lrr@{}}")
    lines.append(r"\toprule")
    lines.append(r"Pattern & $\lambda_i$ & $E(t{=}60)/E(t{=}0)$ \\")
    lines.append(r"\midrule")
    for lab, lam, frac in zip(dec["labels"], dec["lambda_i"], dec["retained_fraction_at_t60"]):
        lines.append(f"{lab} & ${lam:.4f}$ & ${frac:.3f}$ \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    (out / "table_decay.tex").write_text("\n".join(lines) + "\n")

    lines = []
    lines.append(r"\begin{tabular}{@{}rrrrr@{}}")
    lines.append(r"\toprule")
    lines.append(r"$d$ & $\min D$ & $\max D$ & $(\max D-\min D)/\bar{D}$ & range of $-\log(D+\epsilon)$ (nats) \\")
    lines.append(r"\midrule")
    for r in results["concentration"]["rows"]:
        lines.append(f"{r['d']} & {r['d2_min']:.3f} & {r['d2_max']:.3f} & {r['relative_spread']:.2f} & {r['distance_term_range_nats']:.2f} \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    (out / "table_concentration.tex").write_text("\n".join(lines) + "\n")

    w = results["warp"]
    lines = []
    lines.append(r"\begin{tabular}{@{}lrrrr@{}}")
    lines.append(r"\toprule")
    lines.append(r"Pattern & $D_{g=(1,1)}$ & rank & $D_{g=(1.8,0.2)}$ & rank \\")
    lines.append(r"\midrule")
    for lab in results["labels"]:
        r1 = w["unwarped"]["rank_by_abs_E"].index(lab) + 1
        r2 = w["warped"]["rank_by_abs_E"].index(lab) + 1
        lines.append(f"{lab} & {w['unwarped']['d2'][lab]:.3f} & {r1} & {w['warped']['d2'][lab]:.3f} & {r2} \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    (out / "table_warp.tex").write_text("\n".join(lines) + "\n")


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
    out.mkdir(parents=True, exist_ok=True)
    _, labels, _, _ = scene()
    results = {
        "labels": labels,
        "reduction": scenario_reduction(),
        "exchange_rate": scenario_exchange_rate(),
        "valence": scenario_valence(),
        "decay": scenario_decay(),
        "concentration": scenario_concentration(),
        "warp": scenario_warp(),
    }
    (out / "results.json").write_text(json.dumps(results, indent=2))
    table(results, out)
    figure(out)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
