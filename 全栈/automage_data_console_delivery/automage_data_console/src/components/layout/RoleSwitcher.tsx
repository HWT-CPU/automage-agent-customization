import { identityProfiles, type IdentityRole } from '../../config/identities'
import { useIdentityStore } from '../../store/useIdentityStore'

export function RoleSwitcher() {
  const { role, setRole } = useIdentityStore()

  return (
    <div className="flex items-center gap-2">
      {(['staff', 'manager', 'executive'] as IdentityRole[]).map((item) => (
        <button
          key={item}
          type="button"
          onClick={() => setRole(item)}
          className={`status-pill ${role === item ? 'bg-slate-900 text-white' : 'border border-slate-200 bg-white text-slate-700'}`}
        >
          {identityProfiles[item].role}
        </button>
      ))}
    </div>
  )
}
