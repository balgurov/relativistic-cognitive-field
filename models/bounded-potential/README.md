# RCF-derived model: Bounded Cognitive Potential

**Author:** Goce Balgurov

**Document date:** October 22, 2026

**Status:** Proposed derivative model; algorithm specification only

**Licence:** GNU General Public License, version 3 (GPLv3); see the repository's [LICENSE](../../LICENSE)

## The premise

> Intelligence is a balancing force in the universe.

This is the author's central hypothesis. Intelligence has the potential to reorganize information and produce change.

## Purpose and relationship to the RCF

This separate model specifies a global budget for nonnegative cognitive potential when nodes have different propagation parameters. It derives its mass-and-field framing from the [Relativistic Cognitive Field paper](../../paper/rcf.tex). It does not replace the published RCF model or change its reference implementation, examples, or results.

This derivative refines the terminology of the author's underlying hypothesis that information is a substance with an equivalence to energy, and cognitive structures exert gravity and perform work in an N-dimensional space. The rule below is a computational allocation proposal. Its mathematical bound does not establish that physical hypothesis or a physical energy equivalence.

The terms have distinct roles here. **Intelligence** names the hypothesized balancing force. **Potential** names a capacity available to influence the field. **Activation** retains its technical meaning in the published RCF scoring model. The proposed potential quantities below neither measure intelligence itself nor specify how potential is expressed as action or how balancing occurs.

The published RCF uses a signed, query-dependent activation:

$$
E_i(Q,t)=\frac{m_i\gamma_i(Q)}{D_g(q,p_i)+\epsilon}
\exp(-\lambda_i\Delta t_i).
$$

Here, a different symbol, $u_i$, denotes a proposed nonnegative raw potential, and $\widehat u_i$ denotes its allocation under the shared budget. These quantities are not interchangeable with the published activation $E_i$. This model does not supply query relevance, contradiction assessment, temporal decay, or a complete retrieval or reasoning procedure.

## Inputs and proposed potential

For one evaluation, fix a finite active set $A(t)$ and a finite potential budget $B>0$. The budget is also denoted $E_{\max}$ in the motivating formulation. Each node has finite inputs $m_i\geq 0$ and $c_i\geq 0$, with proposed raw potential

$$
u_i(t)=m_i(t)c_i(t)^2.
$$

The new parameter $c_i$ is a node-specific propagation-capacity parameter supplied to this algorithm. Its selection and connection to a propagation mechanism remain design choices. It is not identified with the speed of light, and this scalar equation does not enforce a bound on the speed or distance of propagation. No numerical values or calibration method for $c_i$ or $B$ are prescribed here.

The nonnegative mathematical domain includes zero for completeness. When supplied from the published RCF, stored masses retain its positive ingestion floor and human-validation rule. Zero potential can then arise from $c_i=0$. This algorithm does not alter stored masses, create validation events, or add earned mass through changes to $c_i$.

All raw potentials must use a common unit or numerical scale; $B$ has that same unit or scale. No conversion to physical joules is specified. If $c_i$ is given units, the units assigned to $m_i c_i^2$ and $B$ must agree.

## Total-budget normalization

Define

$$
S(t)=\sum_{j\in A(t)}u_j(t),\qquad
\mathcal N(t)=\max\left(1,\frac{S(t)}{B}\right),\qquad
\widehat u_i(t)=\frac{u_i(t)}{\mathcal N(t)}.
$$

The normalization factor is dimensionless. Unlike unit-vector normalization, the output retains the units or scale of the raw potential. This is a ceiling: when the total is below the budget, potentials are not increased to fill it.

In exact arithmetic, the algorithm is:

1. Validate the finite, nonnegative inputs and the finite, strictly positive budget. Fix the active set and input snapshot for this evaluation.
2. Form each $u_i=m_i c_i^2$ and their sum $S$.
3. If $S\leq B$, return $\widehat u_i=u_i$ for every active node.
4. Otherwise, return $\widehat u_i=B(u_i/S)$ for every active node.

For an empty set the output is empty and its sum is zero. If all raw potentials are zero, step 3 returns zero without dividing by $S$. These steps describe the mathematical algorithm; they are not an overflow-safe floating-point implementation.

## What the rule guarantees

For the stated finite inputs, in exact arithmetic,

$$
\sum_{i\in A(t)}\widehat u_i(t)=\min(S(t),B),\qquad
0\leq\widehat u_i(t)\leq B.
$$

**Proof.** If $S\leq B$, the common divisor is 1 and the sum remains $S$. If $S>B$, the divisor is $S/B$ and the sum is $B$. Nonnegativity then bounds every component by that sum.

Because the divisor is common and strictly positive, zeros, ordering, ties, and defined pairwise ratios of the raw potentials are preserved within the evaluation:

$$
\frac{\widehat u_i}{\widehat u_j}=\frac{u_i}{u_j}
\quad\text{when }u_j>0.
$$

These are statements about $u_i$, not about the published signed RCF scores $E_i$. The new potential rule can rank nodes differently from the published model. Changing the active set, budget, masses, or propagation parameters can change allocations. A ceiling computed over a subset bounds only that subset; it is a whole-field ceiling only when the set covers the whole field. It does not promise unchanged absolute thresholds or comparability between separate evaluations.

## Why the L2 alternative is different

An alternative normalization considered for the same raw potentials is

$$
v_i=\frac{u_i}{\sqrt{\sum_{j\in A}u_j^2}+\epsilon_N},
\qquad\epsilon_N>0.
$$

Here $\epsilon_N$ is finite and has the same units as $u_i$; it is distinct from the published RCF's distance-smoothing constant $\epsilon$. Write $R=\sqrt{\sum_j u_j^2}$. Then

$$
\lVert v\rVert_2=\frac{R}{R+\epsilon_N}<1.
$$

The output is dimensionless. For $n=|A|$ nonnegative raw potentials, its total is at most $\sqrt n\,R/(R+\epsilon_N)$; equal positive raw potentials approach a total of $\sqrt n$ as their common magnitude grows. Thus this alternative bounds vector magnitude, but does not impose a fixed total budget independent of node count. The proposed model uses the total-budget rule above.

## Limits and compatibility

**Boundedness is not convergence.** The uncapped expression $m_i c_i^2$ is finite for finite inputs in exact arithmetic. Node-specific parameters alone do not imply runaway dynamics; such a claim requires an update rule. Conversely, a ceiling does not ensure settling: two allocations can alternate indefinitely between $(B,0)$ and $(0,B)$ while respecting the ceiling at every step. The model specifies no propagation or feedback update law and proves no convergence, damping, or fixed-point property.

**The budget is not a conservation law.** When $S>B$, allocated potential is lower than raw potential; the rule does not specify where the difference goes in a physical system. It does not establish conservation of physical energy, symmetric reciprocity, or a conserved quantity over time. It leaves $m_i$ unchanged. The fixed-total mass equation, positional spread rescaling, motion guards, and other assumptions in the RCF paper's dynamic design appendix remain separate mechanisms.

**Signed information must remain distinct.** This allocation model uses nonnegative potentials. It must not erase the RCF's assessment labels or substitute a signed sum whose positive and negative terms could cancel. Any later integration must preserve the published distinction between support, contradiction, and unassessed material, and define how potential relates to signed activation. That integration is not specified or demonstrated here.

**A mathematical ceiling is not numerical-overflow protection.** Even finite floating-point inputs can overflow while forming $c_i^2$, $m_i c_i^2$, their sum, or a normalization ratio. A future implementation must use suitable scaled or logarithmic arithmetic, handle zeros explicitly, validate intermediate and final values, and test rounding and underflow as well as overflow. The equations alone do not provide those guarantees.

## Development status

This publication contains an algorithm specification and its elementary exact-arithmetic bound. It includes no implementation of this derivative, benchmark, measured throughput, hardware result, or test of physical energy equivalence. No claim of novelty is made for proportional budget scaling itself.

Further work must define the propagation mechanism and parameter meanings, implement safe numerical evaluation, and evaluate the intended task. Checks should cover empty and zero inputs, totals below and above the budget, ties and unequal potentials, active-set changes, extreme numerical ranges, and feedback behavior. Passing numerical checks would establish properties of that implementation, not the physical hypothesis or general reasoning ability.

## Related publications

- [The Relativistic Cognitive Field](../../paper/rcf.tex): the static computational model and its dynamic design appendix.
- [Operating-system design claim](../../os-claim/README.md): the surrounding architecture and owner-teaching rule. This derivative does not change that rule or establish hardware execution.

Copyright (c) 2026 Goce Balgurov. This document is distributed under GPLv3, as specified in the repository's [LICENSE](../../LICENSE).
