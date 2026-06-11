import PACXAI.Core

namespace PACXAI
namespace Leakage

def appears {Secret Out : Type} [BEq Out]
    (secrets : Population Secret)
    (obs : Observation Secret Out)
    (y : Out) : Bool :=
  secrets.any (fun s => obs s == y)

def outputCoverSize {Secret Out : Type} [BEq Out]
    (secrets : Population Secret)
    (obs : Observation Secret Out)
    (outputs : List Out) : Nat :=
  (outputs.filter (appears secrets obs)).length

def cartesian {A B : Type} : List A -> List B -> List (A × B)
  | [], _ => []
  | a :: as, bs => bs.map (fun b => (a,b)) ++ cartesian as bs

def pairObs {Secret A B : Type}
    (obsA : Observation Secret A)
    (obsB : Observation Secret B) : Observation Secret (A × B) :=
  fun s => (obsA s, obsB s)

theorem postprocess_output_pointwise {Secret Raw Out : Type}
    (obs : Observation Secret Raw)
    (f : Raw -> Out)
    (s : Secret) :
    (postprocess obs f) s = f (obs s) := by
  rfl

theorem pairObs_pointwise {Secret A B : Type}
    (obsA : Observation Secret A)
    (obsB : Observation Secret B)
    (s : Secret) :
    pairObs obsA obsB s = (obsA s, obsB s) := by
  rfl

end Leakage
end PACXAI
