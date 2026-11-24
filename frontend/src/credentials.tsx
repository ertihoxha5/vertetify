import { FormEvent, useEffect, useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'

async function api(path: string, method='GET', data?: unknown) {
  const res = await fetch('/api/v1/' + path, {
    method, headers: {'Content-Type':'application/json','X-Vertetify':'workspace'},
    body: data === undefined ? undefined : JSON.stringify(data)
  })
  if (!res.ok) throw new Error(res.status === 401 ? 'Sign-in required.' : 'Request failed. Check your input and try again.')
  return res.json()
}
type Item = {id:string, snapshot:Record<string,string>, state:string, reference:string|null}
type Role = 'registrar'|'holder'|'auditor'
const example = {subject_display_name:'Drita Demo',program_name:'Shkencë Kompjuterike',award_name:'BSc',award_date:'2026-06-30'}
const labels = {subject_display_name:'Synthetic graduate',program_name:'Programme',award_name:'Award',award_date:'Award date'}
const sourceName = (mode:string) => mode === 'compellio-local' ? 'Compellio · local test blockchain' : 'Local simulator'

export function Credentials() {
  const [role,setRole] = useState<Role|null>(null)
  const [items,setItems] = useState<Item[]>([])
  const [message,setMessage] = useState('')
  const [link,setLink] = useState('')
  const [busy,setBusy] = useState(false)
  async function refresh(){
    const result = await api('diplomas')
    setRole(result.role); setItems(result.items)
  }
  useEffect(()=>{ refresh().catch(()=>{}) },[])
  useEffect(()=>{
    if(!items.some(item=>['registered','dispatching','queued'].includes(item.state))) return
    const timer = window.setTimeout(()=>refresh().catch(()=>setMessage('Refresh to check issuance.')),3000)
    return ()=>clearTimeout(timer)
  },[items])
  async function run(action:()=>Promise<void>) {
    setBusy(true); setMessage('')
    try { await action() } catch(error){ setMessage(error instanceof Error ? error.message : 'Request failed.') }
    finally {setBusy(false)}
  }
  function signIn(e:FormEvent<HTMLFormElement>){
    e.preventDefault()
    const fields = Object.fromEntries(new FormData(e.currentTarget))
    void run(async()=>{await api('session','POST',fields); await refresh()})
  }
  return <section><h2>{role ? role === 'holder' ? 'Graduate wallet' : 'Institution workspace' : 'Staff and graduate sign-in'}</h2>
    {!role ? <form onSubmit={signIn}>
      <label>Fixture account<select name="member"><option>fixture-registrar</option><option>fixture-holder</option><option>fixture-auditor</option></select></label>
      <label>Local password<input type="password" name="password" required autoComplete="current-password"/></label>
      <button disabled={busy}>Sign in</button></form> : <>
      <p>Signed in as {role}. <button disabled={busy} onClick={()=>run(async()=>{await api('session','DELETE');setRole(null);setLink('');setItems([])})}>Sign out</button></p>
      {role==='registrar' && <form onSubmit={e=>{e.preventDefault(); const fields=Object.fromEntries(new FormData(e.currentTarget)); void run(async()=>{await api('diplomas','POST',fields);await refresh()})}}>
        {Object.entries(example).map(([k,v])=><label key={k}>{labels[k as keyof typeof labels]}<input required name={k} defaultValue={v} type={k==='award_date'?'date':'text'}/></label>)}
        <button disabled={busy}>Create draft for fixture holder</button></form>}
      {items.map(i=><article key={i.id}><div><strong>{i.snapshot.award_name} · {i.snapshot.program_name}</strong>
        <p>{i.snapshot.subject_display_name} · {i.snapshot.award_date}</p><small>{i.state}{i.reference && ' · '+i.reference}</small></div>
        {role==='registrar' && i.state==='draft' && <button disabled={busy} onClick={()=>run(async()=>{await api('diplomas/'+i.id+'/issue','POST');await refresh()})}>Confirm issuance</button>}
        {role==='holder' && <button disabled={busy} onClick={()=>run(async()=>{const r=await api('diplomas/'+i.id+'/share','POST');setLink(location.origin+'/verify#t='+r.token)})}>Share award, programme, date and institution</button>}</article>)}
      {!items.length && <p>No diplomas available for this account.</p>}
      {link && <div><h3>Verification link · 7 days</h3><QRCodeSVG value={link} size={144} title="Verification link QR code"/>
        <p><a href={link} target="_blank" rel="noreferrer">Open verification link</a></p>
        <button onClick={()=>run(async()=>{await api('shares/disable','POST',{token:link.split('#t=')[1]});setLink('');setMessage('Share disabled.')})}>Disable this link</button></div>}
    </>}<p role="status">{message}</p></section>
}

export function Verifier(){
  const [result,setResult] = useState<{status:string,source?:string,checked_at?:string,diploma?:Record<string,string>}>({status:'Checking proof…'})
  useEffect(()=>{
    let sequence = 0
    function checkLink() {
      const current = ++sequence
      const token = new URLSearchParams(location.hash.slice(1)).get('t')
      history.replaceState(null,'',location.pathname)
      if (!token) { setResult({status:'Reopen the original verification link.'});return }
      setResult({status:'Checking proof…'})
      api('public/verify','POST',{token})
        .then(value => { if (current === sequence) setResult(value) })
        .catch(() => { if (current === sequence) setResult({status:'Proof unavailable'}) })
    }
    checkLink()
    window.addEventListener('hashchange',checkLink)
    return () => { sequence++; window.removeEventListener('hashchange',checkLink) }
  },[])
  const states:Record<string,string> = {verified_local_chain:'Registry and local blockchain evidence match',matched_simulator:'Local simulator records match',link_unavailable:'Link expired, disabled or unavailable',proof_unavailable:'Registry proof unavailable',evidence_mismatch:'Evidence mismatch',not_found:'Registry record missing'}
  return <main><p className="eyebrow">Vertetify · Synthetic diploma</p><h1>Credential verification</h1><section aria-live="polite"><h2>{states[result.status] || result.status}</h2>
    {result.source && <p>{sourceName(result.source)} · {result.checked_at}</p>}
    {result.diploma && <dl>{Object.entries(result.diploma).map(([k,v])=><div key={k}><dt>{k.replace('_',' ')}</dt><dd>{v}</dd></div>)}</dl>}</section></main>
}
