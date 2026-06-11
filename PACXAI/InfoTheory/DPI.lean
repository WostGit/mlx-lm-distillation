import PACXAI.InfoTheory.FiniteDistribution
import PACXAI.Core

namespace PACXAI
namespace InfoTheory

abbrev DetChannel (A B : Type) := A -> B

def observedCodeCost {Secret Obs : Type}
    (p : FiniteDist Secret)
    (obs : Observation Secret Obs)
    (code : Code Obs) : Nat :=
  sumBy (fun s => p.mass s * code (obs s)) p.support

theorem deterministic_dpi_exact {Secret Raw Out : Type}
    (p : FiniteDist Secret)
    (raw : Observation Secret Raw)
    (f : DetChannel Raw Out)
    (outCode : Code Out) :
    observedCodeCost p (postprocess raw f) outCode =
    observedCodeCost p raw (pullCode f outCode) := by
  rfl

def restrictDist {A : Type}
    (p : FiniteDist A)
    (condition : A -> Bool) : FiniteDist A where
  support := p.support.filter condition
  mass := p.mass

theorem conditional_deterministic_dpi_exact {Secret Raw Out : Type}
    (p : FiniteDist Secret)
    (condition : Secret -> Bool)
    (raw : Observation Secret Raw)
    (f : DetChannel Raw Out)
    (outCode : Code Out) :
    observedCodeCost (restrictDist p condition) (postprocess raw f) outCode =
    observedCodeCost (restrictDist p condition) raw (pullCode f outCode) := by
  rfl

def infoGainCost {Secret Obs : Type}
    (p : FiniteDist Secret)
    (obs : Observation Secret Obs)
    (baseline observed : Code Obs) : Nat :=
  sumBy (fun s => p.mass s * (baseline (obs s) - observed (obs s))) p.support

theorem infoGain_postprocess_exact {Secret Raw Out : Type}
    (p : FiniteDist Secret)
    (raw : Observation Secret Raw)
    (f : DetChannel Raw Out)
    (baseline observed : Code Out) :
    infoGainCost p (postprocess raw f) baseline observed =
    infoGainCost p raw (pullCode f baseline) (pullCode f observed) := by
  rfl

end InfoTheory
end PACXAI
