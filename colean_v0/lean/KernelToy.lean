namespace CoLeanKernelToy

theorem dyadic_mass_toy (a b : Nat) : a + b = b + a := by
  exact Nat.add_comm a b

theorem incidence_identity_toy (a b c : Nat) : (a + b) + c = a + (b + c) := by
  exact Nat.add_assoc a b c

theorem tube_density_toy (a b : Nat) (h : a <= b) : a <= b := by
  exact h

end CoLeanKernelToy
