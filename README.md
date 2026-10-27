# Refusing Membrane

**Live demo:** [Holographic Thoughts](https://sparkainlp-x.github.io/holographic-thoughts/) (interactive browser view; synthetic, classical simulation; measured numbers are in this repo)

**A holographic memory that can say "I don't know."**

Selective projection for the complex outer-product holographic
memory: an OES-style gate on the maximum overlap refuses probes no
stored pattern matches well enough. The threshold self-calibrates
on labeled probes (Youden's J), freezes, and is evaluated on fresh
seeds. Stdlib-only Python. AGPL-3.0.

## Measured in this repo (SYNTHETIC — seeded classical simulation, output of `demo.py`)

- Calibrated τ = 0.700 (J = 0.735)
- Test: accept-in-library 0.935, reject-OOD 0.870,
  accuracy on accepted 0.995
- Distribution shift (σ 0.25 → 0.50): catches 75.6% of new errors
  at 37.7% cost on correct probes — trade-off reported, not hidden
- Zero-evidence probes (orthogonal to the library) refused
  unconditionally — plain projection crashed on these
- 7/7 tests pass

**Uncertainty (arithmetic on the counts above, no new runs).** Everything here is one seeded calibration set and one seeded test set (200 in-library and 200 out-of-library probes), so there is no spread across seeds. Treating the probes as independent, Wilson 95% intervals are: accept-in-library 187/200 = 0.935 (0.892–0.962); reject-OOD 174/200 = 0.870 (0.816–0.910); accuracy on accepted 186/187 = 0.995 (0.970–0.999); shift catch rate 31/41 = 0.756 (0.607–0.862); shift cost 60/159 = 0.377 (0.306–0.455). The catch rate at the main operating point rests on a single would-be error (n=1) and is not informative. These intervals cover test-set sampling only, not variation in the calibration set or the seeds; that would need new runs and is not done here.

All numbers are SYNTHETIC (fixed seeds, 4-dimensional toy vectors).
The test vectors are the Bell-state amplitude vectors used purely
as orthonormal complex vectors in an ordinary Python simulation:
no quantum hardware, no quantum effect and no quantum advantage is
claimed. Nothing here is a medical or clinical tool.

## Run it

```bash
python tests.py   # 7 tests
python demo.py    # calibration, evaluation, coverage-risk curve
```

## Honest limits

The gate sees overlap magnitude only — confidently-wrong probes
pass through; τ is calibrated to one noise level and OOD mix;
Youden's J weights both error types equally (the coverage-risk
curve is the real deliverable); toy scale (Bell states). Full
account in `DESIGN.md`.

## Acknowledgements

Mun Seok Lee is acknowledged for discussion only. We cannot verify any specific contribution to this repository, and no file here is known to derive from a package received under his name. He is not an author of this release, and no endorsement of this code or its conclusions is implied.
