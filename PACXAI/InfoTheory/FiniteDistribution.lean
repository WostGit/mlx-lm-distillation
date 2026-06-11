import PACXAI.Core

namespace PACXAI
namespace InfoTheory

def sumBy {A : Type} (f : A -> Nat) : List A -> Nat
  | [] => 0
  | x :: xs => f x + sumBy f xs

structure FiniteDist (A : Type) where
  support : List A
  mass : A -> Nat

def totalMass {A : Type} (p : FiniteDist A) : Nat :=
  sumBy p.mass p.support

def mapDist {A B : Type} [BEq B]
    (f : A -> B)
    (p : FiniteDist A) : FiniteDist B where
  support := p.support.map f
  mass := fun b => sumBy (fun a => if f a == b then p.mass a else 0) p.support

abbrev Code (A : Type) := A -> Nat

def expectedCodeCost {A : Type} (p : FiniteDist A) (code : Code A) : Nat :=
  sumBy (fun a => p.mass a * code a) p.support

def relativeCodeCost {A : Type} (p : FiniteDist A) (pCode qCode : Code A) : Nat :=
  sumBy (fun a => p.mass a * (qCode a - pCode a)) p.support

def pullCode {A B : Type} (f : A -> B) (code : Code B) : Code A :=
  fun a => code (f a)

theorem expectedCodeCost_pullback {A B : Type}
    (p : FiniteDist A)
    (f : A -> B)
    (code : Code B) :
    sumBy (fun a => p.mass a * pullCode f code a) p.support =
    sumBy (fun a => p.mass a * code (f a)) p.support := by
  rfl

theorem totalMass_unfold {A : Type} (p : FiniteDist A) :
    totalMass p = sumBy p.mass p.support := by
  rfl

end InfoTheory
end PACXAI
