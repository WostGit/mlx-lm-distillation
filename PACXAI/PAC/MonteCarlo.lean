import PACXAI.Core
import PACXAI.Recovery
import PACXAI.Conditioning

namespace PACXAI
namespace PAC

structure MonteCarloCertificate where
  samples : Nat
  successes : Nat
  allowedSuccesses : Nat
  confidenceNumerator : Nat
  confidenceDenominator : Nat
  deriving Repr, BEq

def MonteCarloCertificate.Passes (c : MonteCarloCertificate) : Prop :=
  c.successes <= c.allowedSuccesses

def monteCarloFromAttack {Secret Obs Guess : Type}
    (samples : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Obs)
    (attack : CandidateAttack Obs Guess)
    (allowedSuccesses confidenceNumerator confidenceDenominator : Nat) : MonteCarloCertificate :=
  { samples := samples.length,
    successes := observedSuccessCount samples criterion obs attack,
    allowedSuccesses := allowedSuccesses,
    confidenceNumerator := confidenceNumerator,
    confidenceDenominator := confidenceDenominator }

theorem monteCarlo_postprocess_success_eq {Secret Raw Out Guess : Type}
    (samples : Population Secret)
    (criterion : Criterion Secret Guess)
    (raw : Observation Secret Raw)
    (f : Raw -> Out)
    (attack : CandidateAttack Out Guess)
    (allowedSuccesses confidenceNumerator confidenceDenominator : Nat) :
    (monteCarloFromAttack samples criterion (postprocess raw f) attack allowedSuccesses confidenceNumerator confidenceDenominator).successes =
    (monteCarloFromAttack samples criterion raw (liftedAttack f attack) allowedSuccesses confidenceNumerator confidenceDenominator).successes := by
  rfl

theorem monteCarlo_transcript_pass_implies_student_pass {Secret Raw Out Guess : Type}
    (samples : Population Secret)
    (criterion : Criterion Secret Guess)
    (raw : Observation Secret Raw)
    (f : Raw -> Out)
    (attack : CandidateAttack Out Guess)
    (allowedSuccesses confidenceNumerator confidenceDenominator : Nat)
    (h : (monteCarloFromAttack samples criterion raw (liftedAttack f attack) allowedSuccesses confidenceNumerator confidenceDenominator).Passes) :
    (monteCarloFromAttack samples criterion (postprocess raw f) attack allowedSuccesses confidenceNumerator confidenceDenominator).Passes := by
  exact h

def monteCarloFromCandidateClass {Secret Obs Guess : Type}
    (samples : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Obs)
    (candidates : CandidateClass Obs Guess)
    (allowedSuccesses confidenceNumerator confidenceDenominator : Nat) : MonteCarloCertificate :=
  { samples := samples.length,
    successes := candidateBestSuccess samples criterion obs candidates,
    allowedSuccesses := allowedSuccesses,
    confidenceNumerator := confidenceNumerator,
    confidenceDenominator := confidenceDenominator }

theorem monteCarlo_candidateClass_postprocess_eq {Secret Raw Out Guess : Type}
    (samples : Population Secret)
    (criterion : Criterion Secret Guess)
    (raw : Observation Secret Raw)
    (f : Raw -> Out)
    (candidates : CandidateClass Out Guess)
    (allowedSuccesses confidenceNumerator confidenceDenominator : Nat) :
    monteCarloFromCandidateClass samples criterion (postprocess raw f) candidates allowedSuccesses confidenceNumerator confidenceDenominator =
    monteCarloFromCandidateClass samples criterion raw (liftCandidateClass f candidates) allowedSuccesses confidenceNumerator confidenceDenominator := by
  simp [monteCarloFromCandidateClass, candidateBest_postprocess_eq_lifted]

end PAC
end PACXAI
