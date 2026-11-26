import type { ReactNode } from 'react'

const navigation = {
  registrar: [['records','Credential register'], ['issue','Issue a diploma']],
  holder: [['wallet','My diplomas'], ['sharing','Verification links']],
  admin: [['team','Institution team']],
  superadmin: [['requests','Approval queue'], ['health','Registry health'], ['volume','Issuance volume']],
  auditor: []
}

export type Role = keyof typeof navigation
const labels:Record<Role,string> = {
  registrar:'Registrar', holder:'Graduate', admin:'University administrator',
  superadmin:'Platform operator', auditor:'Auditor'
}

export function Dashboard({role,institution,title,children,onLogout,busy}:{
  role:Role,institution:string,title:string,children:ReactNode,onLogout:()=>void,busy:boolean
}) {
  return <div className="dashboard">
    <aside className="dash-rail">
      <p className="eyebrow">Workspace</p><strong>{institution}</strong><small>{labels[role]}</small>
      <nav aria-label="Dashboard navigation"><a href="#dashboard-top">Overview</a>
        {navigation[role].map(([id,label])=><a key={id} href={'#'+id} onClick={()=>{
          const target=document.getElementById(id)
          if(target instanceof HTMLDetailsElement) target.open=true
        }}>{label}</a>)}
      </nav>
      <button className="rail-exit" onClick={onLogout} disabled={busy}>Sign out</button>
    </aside>
    <section className="dash-body" id="dashboard-top">
      <header className="dash-title"><small>{institution} / Overview</small><p className="eyebrow">{labels[role]} dashboard</p><h1>{title}</h1></header>
      {children}
    </section>
  </div>
}
