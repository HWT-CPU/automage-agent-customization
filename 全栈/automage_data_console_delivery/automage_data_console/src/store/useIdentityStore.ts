import { create } from 'zustand'
import { identityProfiles, type IdentityProfile, type IdentityRole } from '../config/identities'

interface IdentityState {
  role: IdentityRole
  identity: IdentityProfile
  setRole: (role: IdentityRole) => void
}

export const useIdentityStore = create<IdentityState>((set) => ({
  role: 'staff',
  identity: identityProfiles.staff,
  setRole: (role) => set({ role, identity: identityProfiles[role] }),
}))
