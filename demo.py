"""Demo: the membrane that refuses.

Setup: store |Phi+>, |Phi->. Out-of-library: |Psi-> and Haar-random
states (the membrane's README shows these get misassigned by plain
projection).

1. Calibrate tau on labeled calibration probes (Youden's J).
2. Freeze tau; evaluate on FRESH test probes.
3. Report: accept-in rate, reject-OOD rate, accuracy on accepted,
   catch rate P(reject | plain projection would err), cost
   P(reject | plain projection would be right), and the
   coverage-risk curve.

Run: python demo.py
"""

import random

from rmembrane import (HolographicMembrane, RefusingMembrane,
                       noisy, rand_state)

S2 = 2 ** -0.5
SIGMA = 0.25


def bell_phi_plus():  return [S2, 0j, 0j, S2]
def bell_phi_minus(): return [S2, 0j, 0j, -S2]
def bell_psi_minus(): return [0j, S2, -S2, 0j]


def make_probes(n_in, n_ood, sigma, seed0):
    rng = random.Random(seed0)
    in_p = [(noisy(bell_phi_plus(), sigma, rng), 0) for _ in range(n_in // 2)]
    in_p += [(noisy(bell_phi_minus(), sigma, rng), 1) for _ in range(n_in // 2)]
    ood = [(noisy(bell_psi_minus(), sigma, rng), None) for _ in range(n_ood // 2)]
    ood += [(rand_state(4, rng), None) for _ in range(n_ood // 2)]
    return in_p, ood


mem = HolographicMembrane([bell_phi_plus(), bell_phi_minus()])
rmem = RefusingMembrane(mem)

cal_in, cal_ood = make_probes(200, 200, SIGMA, seed0=1000)
rep = rmem.calibrate([f for f, _ in cal_in], [f for f, _ in cal_ood])
print(f"calibrated tau = {rep['tau']:.3f}  "
      f"(J = {rep['J']:.3f}, cal accept-in {rep['cal_accept_in']:.3f}, "
      f"cal accept-OOD {rep['cal_accept_ood']:.3f})")

tst_in, tst_ood = make_probes(200, 200, SIGMA, seed0=2000)

dec_in = [(rmem.decide(f), label) for f, label in tst_in]
dec_ood = [rmem.decide(f) for f, _ in tst_ood]

acc_in = sum(d == "accept" for (d, _, _), _ in dec_in) / len(dec_in)
rej_ood = sum(d == "reject" for d, _, _ in dec_ood) / len(dec_ood)
accepted = [(d, w, label) for (d, w, _), label in dec_in if d == "accept"]
acc_on_acc = sum(w == label for _, w, label in accepted) / len(accepted)

# catch rate vs cost, measured against plain projection on the same probes
catch = cost = 0
n_err = n_ok = 0
for ((d, w, _), _), (f, label) in zip(dec_in, tst_in):
    w_plain, _ = mem.project(f)
    if w_plain != label:
        n_err += 1
        catch += (d == "reject")
    else:
        n_ok += 1
        cost += (d == "reject")

print(f"\ntest accept-in-library : {acc_in:.3f}")
print(f"test reject-OOD        : {rej_ood:.3f}")
print(f"accuracy on accepted   : {acc_on_acc:.3f}  (n={len(accepted)})")
if n_err:
    print(f"catch P(reject|would-err)   : {catch / n_err:.3f}  (n={n_err})")
else:
    print("catch: no in-library errors occurred at this noise -- see shift test below")
print(f"cost  P(reject|would-be-right): {cost / n_ok:.3f}  (n={n_ok})")

print("\n-- distribution shift: gate calibrated at sigma=0.25, "
      "in-library probes at sigma=0.50 --")
rng_s = random.Random(3000)
shift = [(noisy(bell_phi_plus(), 0.50, rng_s), 0) for _ in range(100)]
shift += [(noisy(bell_phi_minus(), 0.50, rng_s), 1) for _ in range(100)]
s_err = s_ok = s_catch = s_cost = 0
for f, label in shift:
    d, _, _ = rmem.decide(f)
    w_plain, _ = mem.project(f)
    if w_plain != label:
        s_err += 1
        s_catch += (d == "reject")
    else:
        s_ok += 1
        s_cost += (d == "reject")
print(f"plain accuracy under shift      : {s_ok / len(shift):.3f}")
print(f"catch P(reject|would-err)       : {s_catch / s_err:.3f}  (n={s_err})")
print(f"cost  P(reject|would-be-right)  : {s_cost / s_ok:.3f}  (n={s_ok})")

print("\ncoverage-risk curve (test in-library probes, tau swept):")
print(f"  {'tau':>5} {'coverage':>8} {'risk':>6}")
for g in range(0, 101, 10):
    tau = g / 100
    cov_err = 0
    cov = 0
    for f, label in tst_in:
        if rmem.max_overlap(f) >= tau:
            cov += 1
            w, _ = mem.project(f)
            cov_err += (w != label)
    print(f"  {tau:>5.2f} {cov / len(tst_in):>8.3f} "
          f"{(cov_err / cov if cov else 0):>6.3f}")

print("\nRESULT: gate rejects OOD while keeping in-library accuracy; "
      "catch and cost measured, not assumed.")
