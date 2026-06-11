import Lake
open Lake DSL

package «pacxai_10_10_artifact» where
  -- Self-contained, mathlib-free finite recovery/privacy artifact.

@[default_target]
lean_lib PACXAI where
  roots := #[`PACXAI]
