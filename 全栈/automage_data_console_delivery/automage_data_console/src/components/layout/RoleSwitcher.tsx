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
          className={`status-pill ${role === item ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700'}`}
        >
          {identityProfiles[item].role}
        </button>
      ))}
    </div>
  )
}
