import PACXAI.Core

namespace PACXAI

abbrev CandidateAttack (Observation Guess : Type) := Observation -> Guess

def observedSuccessCount {Secret Obs Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Obs)
    (attack : CandidateAttack Obs Guess) : Nat :=
  successCount secrets criterion (fun s => attack (obs s))

def observedSuccessRate {Secret Obs Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Obs)
    (attack : CandidateAttack Obs Guess) : EmpiricalRate :=
  successRate secrets criterion (fun s => attack (obs s))

abbrev CandidateClass (Obs Guess : Type) := List (CandidateAttack Obs Guess)

def candidateScores {Secret Obs Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Obs)
    (candidates : CandidateClass Obs Guess) : List Nat :=
  candidates.map (fun attack => observedSuccessCount secrets criterion obs attack)

def bestNat : List Nat -> Nat
  | [] => 0
  | x :: xs => Nat.max x (bestNat xs)

def candidateBestSuccess {Secret Obs Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Obs)
    (candidates : CandidateClass Obs Guess) : Nat :=
  bestNat (candidateScores secrets criterion obs candidates)

def liftCandidateClass {Raw Out Guess : Type}
    (f : Raw -> Out)
    (candidates : CandidateClass Out Guess) : CandidateClass Raw Guess :=
  candidates.map (liftedAttack f)

theorem candidateScores_postprocess_eq {Secret Raw Out Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Raw)
    (f : Raw -> Out)
    (candidates : CandidateClass Out Guess) :
    candidateScores secrets criterion (postprocess obs f) candidates =
    candidateScores secrets criterion obs (liftCandidateClass f candidates) := by
  induction candidates with
  | nil => rfl
  | cons a rest ih =>
      simp [candidateScores, liftCandidateClass, observedSuccessCount, postprocess, liftedAttack,
        successCount, countWhere]

theorem candidateBest_postprocess_eq_lifted {Secret Raw Out Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Raw)
    (f : Raw -> Out)
    (candidates : CandidateClass Out Guess) :
    candidateBestSuccess secrets criterion (postprocess obs f) candidates =
    candidateBestSuccess secrets criterion obs (liftCandidateClass f candidates) := by
  simp [candidateBestSuccess, candidateScores_postprocess_eq]

def empiricalRisk {Secret Obs Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Obs)
    (attack : CandidateAttack Obs Guess) : Nat :=
  failureCount secrets criterion (fun s => attack (obs s))

theorem empiricalRisk_postprocess_eq {Secret Raw Out Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Raw)
    (f : Raw -> Out)
    (attack : CandidateAttack Out Guess) :
    empiricalRisk secrets criterion (postprocess obs f) attack =
    empiricalRisk secrets criterion obs (liftedAttack f attack) := by
  rfl

end PACXAI
