# DESIGN — Deep think: the membrane that refuses

## The gap

The earlier plain-projection prototype documents it honestly:
"`project()` never rejects a probe." A state from far outside the
library still gets assigned to *some* pattern. Worse — found while
testing: a probe *orthogonal* to every stored pattern makes the
overlap vector all zeros, and plain projection either crashes
(division by zero) or silently argmaxes over nothing. The refusal
isn't a nicety; it fixes a real failure mode.

## The mechanism

Gate on the maximum overlap: REJECT iff
max_μ |⟨p^μ|probe⟩| < τ. One statistic, one threshold, no learned
machinery. A probe orthogonal to the whole library (total overlap
zero) is refused unconditionally — there is no evidence to project.

## Calibration without cheating

τ is chosen on *labeled calibration probes* (in-library noisy
patterns vs out-of-library states) by maximizing Youden's
J = P(accept|in-library) − P(accept|out-of-library), then **frozen**.
Every reported metric is measured on fresh test probes. Calibrating
and evaluating on the same data would be cheating, and the code
structure makes that impossible by accident: `calibrate()` sets the
threshold, the demo evaluates on different seeds.

## Measured (SYNTHETIC — seeds fixed, see demo.py)

- Calibrated τ = 0.700, J = 0.735.
- Test: accept-in-library 0.935, reject-OOD 0.870,
  accuracy on accepted 0.995.
- Coverage-risk curve is monotone and clean: risk stays ≤ 0.005
  down to coverage 0.935, then coverage collapses as τ → 1.
- Distribution shift (gate calibrated at σ = 0.25, in-library
  probes at σ = 0.50): plain accuracy falls to 0.795; the gate
  catches 75.6% of the errors it would have made, at a cost of
  rejecting 37.7% of probes it would have gotten right. That
  trade-off is the honest price of refusal under shift — reported,
  not hidden.

## Honest limits

- **The gate sees only overlap magnitude.** A confidently-wrong
  probe (high overlap with the wrong pattern — e.g., a nearby
  non-orthogonal pattern) sails through. Refusal covers
  *out-of-library*, not *ambiguous*.
- **τ is calibrated to a specific noise level and OOD mix.**
  Change the deployment distribution and the calibration is stale;
  the shift experiment shows the degradation is graceful, not
  catastrophic — but re-calibration is the correct response, not
  hope.
- **Youden's J is a choice.** It weights false accepts and false
  rejects equally. A deployment that fears false accepts more
  should optimize a different operating point off the
  coverage-risk curve — which is why the curve, not just τ, is
  the deliverable.
- **Two patterns, toy states.** The mechanism is general; the
  numbers are for Bell-state amplitude vectors used as classical
  4-dimensional complex vectors (no quantum hardware or effect). Scale claims need scale experiments.
