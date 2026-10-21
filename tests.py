"""Tests for refusing-membrane. Run: python tests.py"""

import random

from rmembrane import (HolographicMembrane, RefusingMembrane,
                       noisy, rand_state, normalize)

S2 = 2 ** -0.5


def bell_phi_plus():  return [S2, 0j, 0j, S2]
def bell_phi_minus(): return [S2, 0j, 0j, -S2]
def bell_psi_minus(): return [0j, S2, -S2, 0j]


def make_gate():
    mem = HolographicMembrane([bell_phi_plus(), bell_phi_minus()])
    return RefusingMembrane(mem)


def test_clean_pattern_accepted():
    rmem = make_gate()
    rmem.tau = 0.5
    d, w, _ = rmem.decide(bell_phi_plus())
    assert d == "accept" and w == 0


def test_orthogonal_state_rejected():
    # |Psi-> is orthogonal to both stored patterns: max overlap ~ 0.
    rmem = make_gate()
    rmem.tau = 0.5
    d, w, _ = rmem.decide(bell_psi_minus())
    assert d == "reject" and w is None


def test_no_tau_accepts_normal_probe():
    rmem = make_gate()  # tau=None: no threshold gate...
    d, w, _ = rmem.decide(bell_phi_plus())
    assert d == "accept" and w == 0


def test_zero_evidence_always_rejects():
    # ...but a probe orthogonal to the whole library is refused anyway:
    # there is no evidence to project.
    rmem = make_gate()  # tau=None
    d, w, probs = rmem.decide(bell_psi_minus())
    assert d == "reject" and w is None and probs == [0.0, 0.0]


def test_calibration_deterministic_and_sane():
    rng = random.Random(7)
    in_p = [noisy(bell_phi_plus(), 0.25, rng) for _ in range(60)]
    ood = [rand_state(4, rng) for _ in range(60)]
    r1, r2 = make_gate(), make_gate()
    rep1 = r1.calibrate(in_p, ood)
    rep2 = r2.calibrate(in_p, ood)
    assert rep1["tau"] == rep2["tau"]
    assert 0.0 < rep1["tau"] < 1.0
    assert rep1["J"] > 0.5  # the two score distributions separate well


def test_coverage_falls_with_tau():
    rmem = make_gate()
    rng = random.Random(11)
    probes = [noisy(bell_phi_plus(), 0.25, rng) for _ in range(60)]
    covs = []
    for tau in (0.0, 0.5, 0.99):
        rmem.tau = tau
        covs.append(sum(rmem.decide(f)[0] == "accept" for f in probes))
    assert covs[0] >= covs[1] >= covs[2]


def test_end_to_end_gate_helps():
    rng = random.Random(21)
    mem = HolographicMembrane([bell_phi_plus(), bell_phi_minus()])
    rmem = RefusingMembrane(mem)
    cal_in = [noisy(bell_phi_plus(), 0.25, rng) for _ in range(100)] + \
             [noisy(bell_phi_minus(), 0.25, rng) for _ in range(100)]
    cal_ood = [rand_state(4, rng) for _ in range(200)]
    rmem.calibrate(cal_in, cal_ood)
    tst_ood = [rand_state(4, rng) for _ in range(100)]
    rej = sum(rmem.decide(f)[0] == "reject" for f in tst_ood)
    assert rej / len(tst_ood) >= 0.80
    tst_in = [noisy(bell_phi_plus(), 0.25, rng) for _ in range(100)]
    acc = sum(rmem.decide(f)[0] == "accept" for f in tst_in)
    assert acc / len(tst_in) >= 0.80


if __name__ == "__main__":
    for name, fn in sorted(
            [(k, v) for k, v in globals().items() if k.startswith("test_")]):
        fn()
        print(f"PASS {name}")
    print("all tests passed")
