"""The refusing membrane: selective projection with a calibrated gate.

A plain holographic membrane never rejects a probe -- even a state
from far outside its library gets assigned to *some* pattern. This
module adds the missing refusal: an OES-style gate on the maximum
overlap. If no stored pattern matches the probe well enough, the
membrane says "I don't know" instead of guessing.

Gate: REJECT iff max_mu |<p^mu|probe>| < tau.

Calibration (self-calibrating, then frozen): on labeled calibration
probes (in-library vs out-of-library), sweep tau and maximize
Youden's J = TPR - FPR, where TPR = P(accept | in-library) and
FPR = P(accept | out-of-library). The chosen tau is frozen and all
reported metrics are measured on FRESH test probes -- calibrating
and evaluating on the same data would be cheating.
"""

import math
import random


def normalize(v):
    n = math.sqrt(sum(abs(c) ** 2 for c in v))
    return [c / n for c in v]


def overlap(field, pattern):
    return sum(p.conjugate() * f for p, f in zip(pattern, field))


def rand_state(n, rng):
    """Haar-random pure state via complex Gaussians."""
    return normalize([complex(rng.gauss(0, 1), rng.gauss(0, 1))
                      for _ in range(n)])


def noisy(state, sigma, rng):
    return normalize([c + complex(rng.gauss(0, sigma), rng.gauss(0, sigma))
                      for c in state])


class HolographicMembrane:
    def __init__(self, patterns):
        self.patterns = [normalize(p) for p in patterns]

    def overlaps(self, field):
        return [overlap(field, p) for p in self.patterns]

    def project(self, field):
        ms = self.overlaps(field)
        tot = sum(abs(m) ** 2 for m in ms)
        probs = [abs(m) ** 2 / tot for m in ms]
        return max(range(len(ms)), key=lambda i: abs(ms[i])), probs


class RefusingMembrane:
    def __init__(self, membrane, tau=None):
        self.mem = membrane
        self.tau = tau

    def max_overlap(self, field):
        return max(abs(m) for m in self.mem.overlaps(field))

    def decide(self, field):
        """('accept', winner, probs) or ('reject', None, probs)."""
        ms = self.mem.overlaps(field)
        tot = sum(abs(m) ** 2 for m in ms)
        if tot == 0:
            # Zero evidence: the probe is orthogonal to the whole
            # stored subspace. Refuse outright -- plain project()
            # would silently argmax over zeros and "classify" it.
            return ("reject", None, [0.0] * len(ms))
        probs = [abs(m) ** 2 / tot for m in ms]
        winner = max(range(len(ms)), key=lambda i: abs(ms[i]))
        if self.tau is not None and max(abs(m) for m in ms) < self.tau:
            return ("reject", None, probs)
        return ("accept", winner, probs)

    def calibrate(self, in_probes, ood_probes, grid=101):
        """Pick tau maximizing Youden's J on calibration probes.
        Freezes tau; returns the calibration report."""
        in_scores = [self.max_overlap(f) for f in in_probes]
        ood_scores = [self.max_overlap(f) for f in ood_probes]
        best = None
        for g in range(grid):
            tau = g / (grid - 1)
            tpr = sum(s >= tau for s in in_scores) / len(in_scores)
            fpr = sum(s >= tau for s in ood_scores) / len(ood_scores)
            if best is None or (tpr - fpr) > best[0]:
                best = (tpr - fpr, tau, tpr, fpr)
        self.tau = best[1]
        return {"tau": best[1], "J": best[0],
                "cal_accept_in": best[2], "cal_accept_ood": best[3]}
