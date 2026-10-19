# A Standalone Cognitive Operating System Booted from a Relativistic Cognitive Field: Design Claim and Software Prototype

**Author:** Goce Balgurov (`balgurov@giji.agency`)  
**Date:** 19 October 2026

## Abstract

This paper states the author's claim and design for a standalone cognitive operating system whose complete persistent state is a Relativistic Cognitive Field (RCF). The author states this system as his design and claim, accompanied by a working software prototype, rather than as a finished physical or hardware result. In this architecture, the field is the core: the owner's teaching, accepted lessons, judgments of agreement and contradiction, and a general-knowledge pool are held as rest mass, valence, and time, and the owner's acts are persisted in an append-only event log; booting loads the pool and replays that log into the field, without language-model weights. The system classifies user intent and composes plain-language answers with provenance directly from the active field, explaining every answer via log mass, log valence, distance, and decay. A language model is at most an optional peripheral at teaching time and is never on the default answer path.

## 1. Introduction

The central design claim of this paper is that a complete, standalone cognitive operating system can be booted and operated directly from a Relativistic Cognitive Field (RCF) without language-model weights in its core or on its default answer path. This work builds directly upon the author's published RCF paper ([https://github.com/balgurov/relativistic-cognitive-field](https://github.com/balgurov/relativistic-cognitive-field), tag v1.0), which introduced the static memory-scoring formulation in which stored patterns carry human-validated rest mass, query-dependent valence, a query-warped diagonal metric, and mass-scaled temporal decay. Where the prior paper defined the mathematical model and its elementary retrieval properties, the present document claims the surrounding operating system architecture as the author's design: an event-sourced cognitive core that boots by log replay, understands owner intent without command syntax, answers from the active field with exact mathematical diagnostics, learns through human validation and contradiction digestion, and treats any neural language model strictly as an optional teaching-time peripheral.

## 2. The Claim

The author states the following eight points as the author's claim and system design, not as a proven theorem or completed hardware result:

1. **The field is the core.** The complete persistent state of the intelligence is a Relativistic Cognitive Field (RCF), governed by the author's published activation law:
   $$E = \frac{m \cdot \gamma}{D_g + \epsilon} \exp(-\lambda \Delta t)$$
   The owner's teaching, accepted lessons, and judgments of agreement and contradiction are held as rest mass $m$, valence $\gamma$, and time $\Delta t$ and persisted as an append-only event log; the general-knowledge pool is the base over which the field is initialised. Booting the system means loading the pool and replaying that log into the field. No language-model weights are part of the core or needed to boot.

2. **Understanding without a model.** The system classifies what the owner means—a question, a statement to be taught, a correction, a yes or a no, an instruction to forget, a request for other views, a greeting, or an unclear message—by itself, without commands or keywords the owner must learn.

3. **Answering without a model.** Answers are composed from the field's active set in plain language, each with a provenance line naming the patterns used. When nothing in the field is relevant, the system states that it does not know.

4. **Learning from the owner.** Mass above the pool's base value comes only from the owner's acts of teaching and validation. Digestion judges what each new teaching agrees with or contradicts. Contradicted knowledge is pushed down only for questions to which the contradicting teaching is itself relevant (query-dependent valence, as defined in the RCF paper). Newer teaching supersedes older teaching it contradicts. The owner's words are restated once, cleanly, intended to keep the same meaning, while the original stays on record.

5. **A language model is an optional peripheral, never the core.** At most, a language model restates or helps judge teaching at the moment of teaching. It is on the answer path only if the owner switches on an optional rewording step, which is off by default. Booting, understanding, and answering make no language-model call; in the prototype a model is still called at teaching time (Section 4).

6. **Explainability in the field's terms.** Every answer is explainable by the field's mathematical terms—log mass, log valence, distance, and decay—shown in a live diagnostic panel.

7. **Direct execution (design only).** The core is designed to run directly on hardware as the operating layer of the machine, with the field evaluated per pattern in parallel, and with dedicated field-evaluation hardware as a future design. By operating layer the author means that the field, the log replay, and the understanding, answering and digestion functions are the machine's resident program, with no general-purpose operating system beneath them; by dedicated field-evaluation hardware he means hardware in which the activation $E$ of every stored pattern is computed in parallel for each query and the active set is selected by ranking those activations.

8. **Owner and public separation.** The owner teaches; public visitors may only ask. Public questions never change the owner's field.

## 3. Architecture

This section describes the architecture as the author's design. Section 4 states which parts exist today as a software prototype and which are design only.

**Boot from the log.** Persistence is strictly event-sourced. Every act of teaching, validation, confirmation, forgetting, or contradiction judgment is appended as an immutable record to an append-only event log. The system holds no opaque checkpoint files or neural weight matrices as its primary state. To boot the system is to initialise an empty field over the base general-knowledge pool and replay the append-only event log from the beginning, reconstructing the exact rest mass, valence relationships, and timestamps of every pattern.

**The field.** Once booted, the active state resides in the Relativistic Cognitive Field. Every entry in the general-knowledge pool and every lesson taught by the owner exists as a pattern in the field. For any incoming query, each pattern is scored by the activation equation $E = \frac{m \cdot \gamma}{D_g + \epsilon} \exp(-\lambda \Delta t)$, where $m$ is rest mass, whose increments above its base value come solely from the owner's teaching and validation, $\gamma$ is the query-dependent valence, $D_g$ is the distance under the query-warped metric, $\epsilon$ is the smoothing constant acting as the exchange rate between mass and proximity, and $\exp(-\lambda \Delta t)$ is the temporal decay, whose rate $\lambda$ falls with mass and whose clock $\Delta t$ resets upon reinforcement, as defined in the RCF paper.

**Understanding.** When the owner submits plain text, the system determines the communicative intent without invoking a language model and without requiring special command prefixes or keywords. It distinguishes, by sentence form and a small built-in vocabulary, whether the input is a question seeking an answer, a statement to be recorded as teaching, a correction of the last answer, a yes or a no to a pending action, an instruction to forget, a request to inspect alternative or contradicted views, a greeting, or something unclear, in which case it asks.

**Answering.** When the input is classified as a question or a request for other views, the field is evaluated across all stored patterns. The highest-activation patterns form the active set. The response is the text of the top-ranked patterns, presented in plain language with a provenance line naming them; no text is generated by a language model. If no pattern's relevance reaches the configured threshold, the system abstains and states that it does not know. Every answer is accompanied in the live diagnostic panel by its rows' mass, cosine, valence and activation together with their log terms.

**Digestion and restatement.** When the input is classified as teaching, correction, confirmation, or forgetting, the system updates the owner's field. Mass above the base value is granted or incremented only through these explicit owner acts. During digestion, the field proposes candidate patterns, and each is judged as agreeing with, contradicting, or neither, relative to the new teaching; in the prototype this judgment is one language-model call per teaching. In accordance with the RCF formulation, contradiction does not erase or globally zero out an older pattern; instead, it establishes a valence relationship so that contradicted knowledge is pushed down only for queries to which the contradicting teaching is itself relevant. When a newer teaching contradicts an older teaching from the owner, the newer teaching supersedes the older one. At the moment of teaching, the owner's words are restated once into a clean sentence with its subject (in the prototype, by one language-model call), intended to keep the same meaning, while the owner's exact original words remain permanently on record in the log.

**The model as peripheral.** A neural language model is never part of the cognitive core and is never called on the default question-answering path. By design a language model is only an optional peripheral; the present prototype calls one at teaching time, to restate the owner's teaching cleanly and to help judge agreement and contradiction during digestion. The system boots, understands, and answers without it.

**Owner and public.** The architecture enforces a strict boundary between the owner and public visitors. Only the owner, in owner mode, may issue teaching, corrections, confirmations, or forgetting events that append to the event log and alter rest mass or valence. In public mode visitors may only ask; their questions evaluate the field to produce answers, are recorded in a separate log, and never mutate the owner's field or append to the owner's event log.

## 4. Status and Limits

**Use case.** One use case is realised today: a personal intelligence that its owner teaches. The owner talks to it in plain language; it answers from its own field, offline, and shows where each answer came from; what the owner teaches reshapes its answers at once, and knowledge the owner contradicts recedes; in the interface's public mode, visitors may only ask it questions; their questions go to a separate log and never change the owner's field. The same core is intended as the operating layer of the standalone machine stated as design only in Claim 7 and under the heading "What is claimed only as design" below.


**What exists.** A working software prototype implemented in the Python standard library exists and demonstrates the software components of this claim. The prototype operates the Relativistic Cognitive Field over 13,705 general-knowledge entries together with the owner's teaching, accepted lessons and judgments. It includes an append-only event log replayed into the field at start, model-free intent understanding, model-free answer composition with a provenance line, teaching digestion and restatement (one language-model call each per teaching, two in total), a public mode in which visitors may only ask, and a local web interface with a live diagnostic panel showing, for each answer row, mass, cosine, valence, activation and their log terms, the pushed-down rows, and a counter of model calls.

**Measurement.** Evaluated on 48 test questions over the populated field, each written by a language model from one pool entry chosen across the pool's subject areas and paired with that entry as its intended answer, the prototype ranks the intended entry first in 40 of the 48 questions and within the top eight in all 48. This is the author's own measurement on the unpublished prototype. All 48 questions are answered with zero language-model calls. No evaluation beyond this stated measurement is claimed, and no performance claims are made beyond it.

**What is claimed only as design.** Three elements are stated strictly as the author's design and hypothesis, not as implemented results:
1. Direct execution of the cognitive core on bare hardware as the operating layer of the machine.
2. Dedicated parallel hardware for per-pattern field evaluation.
3. The dynamic field (moving patterns) as formulated in the appendix of the RCF paper.

**Honest limits.** In the current working prototype, pattern coordinates are lexical rather than dense learned representations; the system operates in English only; and while answering and intent classification require zero model calls, a language model is still called twice per teaching, once to restate the owner's words and once to judge candidate patterns as agreeing, contradicting, or neither; the diagnostic panel counts these calls.

## 5. Priority and Licence

This document is published as a dated public record of the author's design and claim as of 19 October 2026, in the folder `os-claim/` of the repository, alongside the Relativistic Cognitive Field paper ([https://github.com/balgurov/relativistic-cognitive-field](https://github.com/balgurov/relativistic-cognitive-field), tag v1.0). Copyright (C) 2026 Goce Balgurov. This document and the repository that publishes it are licensed under the GNU General Public License version 3 (GPLv3); a copy of the licence is included in that repository as `LICENSE`. The licence applies to this text; the prototype described in Section 4 is not part of this publication. The underlying architecture and ideas are placed on the public record as prior art, to establish priority and prevent third-party enclosure.

## References

[1] Goce Balgurov. *The Relativistic Cognitive Field: A Gravity-Inspired Activation Model for Memory Retrieval with Validated Mass, Contradiction Valence and Decay*. Public repository and paper, 2026, tag v1.0. https://github.com/balgurov/relativistic-cognitive-field
