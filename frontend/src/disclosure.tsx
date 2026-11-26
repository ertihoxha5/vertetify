import { useState } from 'react'

const panels = [
  {label:'Shared diploma', title:'What a recipient sees', rows:[
    ['Issuer identifier','juniper'], ['Award','BSc'], ['Programme','Computer Science'], ['Award date','30 June 2026']
  ]},
  {label:'Registry evidence', title:'What the Registry holds', rows:[
    ['Payload','Diploma commitment'], ['Profile reference','Registered TAR in @context'], ['Canonical format','RFC 8785 JSON'],
    ['Integrity check','SHA-256'], ['Local chain','31337']
  ]}
]

export function Disclosure() {
  const [selected,setSelected]=useState(0)
  const panel=panels[selected]
  return <section className="disclosure" id="evidence">
    <div><p className="eyebrow">Disclosure specimen</p><h2>What travels<br/><em>with a diploma?</em></h2>
      <p>The graduate shares four academic details. Their name stays in the institution’s record. The registry holds a cryptographic commitment to that record.</p>
      <p>When someone opens a link, Vertetify checks that it is still active and compares the evidence again.</p>
    </div>
    <div className="folio"><div className="folio-controls" aria-label="Inspect a synthetic example">
      {panels.map((p,i)=><button key={p.label} aria-pressed={selected===i} onClick={()=>setSelected(i)}>{p.label}</button>)}
    </div><div className="folio-sheet" key={panel.label} aria-live="polite"><p className="eyebrow">Synthetic example</p><h3>{panel.title}</h3>
      <dl>{panel.rows.map(([field,value])=><div key={field}><dt>{field}</dt><dd>{value}</dd></div>)}</dl>
    </div></div>
  </section>
}
