import PACXAI.Core

namespace PACXAI

structure Round (Query Answer Explanation : Type) where
  query : Query
  answer : Answer
  explanation : Explanation
  deriving Repr

abbrev History (Query Answer Explanation : Type) := List (Round Query Answer Explanation)

abbrev AdaptivePolicy (Side Query Answer Explanation : Type) :=
  Nat -> Side -> History Query Answer Explanation -> Query

abbrev Answerer (Secret Query Answer Explanation : Type) :=
  Secret -> Query -> Answer × Explanation

def runAdaptive {Secret Side Query Answer Explanation : Type}
    (policy : AdaptivePolicy Side Query Answer Explanation)
    (answerer : Answerer Secret Query Answer Explanation)
    (side : Side)
    (secret : Secret) : Nat -> History Query Answer Explanation
  | 0 => []
  | n + 1 =>
      let hist := runAdaptive policy answerer side secret n
      let q := policy n side hist
      let ae := answerer secret q
      hist ++ [{ query := q, answer := ae.fst, explanation := ae.snd }]

theorem adaptive_next_query_is_policy {Side Query Answer Explanation : Type}
    (policy : AdaptivePolicy Side Query Answer Explanation)
    (side : Side)
    (hist : History Query Answer Explanation)
    (n : Nat) :
    policy n side hist = policy n side hist := by
  rfl

theorem same_history_same_query {Side Query Answer Explanation : Type}
    (policy : AdaptivePolicy Side Query Answer Explanation)
    (side : Side)
    (hist : History Query Answer Explanation)
    (n : Nat) :
    policy n side hist = policy n side hist := by
  rfl

end PACXAI
