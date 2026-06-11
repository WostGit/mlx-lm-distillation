import PACXAI.Core
import PACXAI.Recovery
import PACXAI.InfoTheory.FiniteDistribution
import PACXAI.InfoTheory.DPI

namespace PACXAI
namespace InfoTheory

structure FanoStyleCertificate where
  total : Nat
  successes : Nat
  allowedErrors : Nat
  requiredInformation : Nat
  deriving Repr, BEq

def FanoStyleCertificate.Valid (c : FanoStyleCertificate) : Prop :=
  c.total <= c.successes + c.allowedErrors

def fanoStyleFromAttack {Secret Obs Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (obs : Observation Secret Obs)
    (attack : CandidateAttack Obs Guess)
    (allowedErrors requiredInformation : Nat) : FanoStyleCertificate :=
  { total := secrets.length,
    successes := observedSuccessCount secrets criterion obs attack,
    allowedErrors := allowedErrors,
    requiredInformation := requiredInformation }

theorem fanoStyle_student_transcript_success_eq
    {Secret Transcript Student Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (transcript : Observation Secret Transcript)
    (train : Transcript -> Student)
    (studentAttack : CandidateAttack Student Guess)
    (allowedErrors requiredInformation : Nat) :
    (fanoStyleFromAttack secrets criterion (postprocess transcript train) studentAttack allowedErrors requiredInformation).successes =
    (fanoStyleFromAttack secrets criterion transcript (liftedAttack train studentAttack) allowedErrors requiredInformation).successes := by
  rfl

theorem fanoStyle_valid_student_to_transcript
    {Secret Transcript Student Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (transcript : Observation Secret Transcript)
    (train : Transcript -> Student)
    (studentAttack : CandidateAttack Student Guess)
    (allowedErrors requiredInformation : Nat)
    (h : (fanoStyleFromAttack secrets criterion (postprocess transcript train) studentAttack allowedErrors requiredInformation).Valid) :
    (fanoStyleFromAttack secrets criterion transcript (liftedAttack train studentAttack) allowedErrors requiredInformation).Valid := by
  exact h

def violatesInfoBudget (budget : Nat) (cert : FanoStyleCertificate) : Prop :=
  cert.Valid ∧ budget < cert.requiredInformation

theorem fanoStyle_budget_violation_lifts
    {Secret Transcript Student Guess : Type}
    (secrets : Population Secret)
    (criterion : Criterion Secret Guess)
    (transcript : Observation Secret Transcript)
    (train : Transcript -> Student)
    (studentAttack : CandidateAttack Student Guess)
    (allowedErrors requiredInformation budget : Nat)
    (h : violatesInfoBudget budget (fanoStyleFromAttack secrets criterion (postprocess transcript train) studentAttack allowedErrors requiredInformation)) :
    violatesInfoBudget budget (fanoStyleFromAttack secrets criterion transcript (liftedAttack train studentAttack) allowedErrors requiredInformation) := by
  exact h

end InfoTheory
end PACXAI
