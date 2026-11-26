import { FormEvent, useEffect, useRef, useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { RegistryHeader } from './identity'

import { api } from './api'
import { Management } from './access'
type Item = {id:string, snapshot:Record<string,string>, state:string, reference:string|null,version:number|null,last_matched:string|null,registry_checksum?:string,mode?:string}
import { Dashboard, type Role } from './dashboard'
type ActiveShare = { id:string, expires:string, programme:string }
const example = {subject_display_name:'Drita Demo',program_name:'Shkencë Kompjuterike',award_name:'BSc',award_date:'2026-06-30'}
const labels = {subject_display_name:'Synthetic graduate',program_name:'Programme',award_name:'Award',award_date:'Award date'}
const sourceName = (mode:string) => mode === 'compellio-local' ? 'Compellio · local test blockchain' : mode==='simulator' ? 'Local simulator' : 'Unknown environment'

export function Credentials() {
  const [role,setRole] = useState<Role|null>(null)
  const [holders,setHolders] = useState<string[]>([])
  const [institution,setInstitution] = useState('')
  const [selected,setSelected] = useState<string|null>(null)
  const detail = useRef<HTMLDialogElement>(null)
  const [items,setItems] = useState<Item[]>([])
  const [query,setQuery]=useState('')
  const [filter,setFilter]=useState('')
  const [page,setPage]=useState(0)
  const [draft,setDraft]=useState(example)
  const visibleRows=items.filter(i=>(!filter || i.state===filter) && [i.id,i.snapshot.program_name,i.snapshot.award_name,i.reference].join(' ').toLowerCase().includes(query.trim().toLowerCase()))
  const pageCount=Math.ceil(visibleRows.length/12)
  const currentPage=Math.min(page,Math.max(0,pageCount-1))
  const [expired,setExpired]=useState<ActiveShare[]>([])
  const [shares,setShares] = useState<ActiveShare[]>([])
  const refreshSequence = useRef(0)
  const [message,setMessage] = useState('')
  const [link,setLink] = useState('')
  const [busy,setBusy] = useState(false)
  const [account,setAccount] = useState(new URLSearchParams(location.search).has('invited') ? 'invited' : new URLSearchParams(location.search).has('graduate') ? 'fixture-holder' : 'fixture-registrar')
  const sharePanel = useRef<HTMLHeadingElement>(null)
  useEffect(() => { if (link) sharePanel.current?.focus() }, [link])
  async function refresh(){
    const sequence = ++refreshSequence.current
    const result = await api('diplomas')
    const selectedId = new URLSearchParams(location.search).get('credential')
    const visible = result.items.some((item:Item)=>item.id===selectedId)
    const sharePath=selectedId ? 'shares?credential='+encodeURIComponent(selectedId) : 'shares'
    const [active,ended]=result.role==='holder' && (!selectedId || visible) ?
      await Promise.all([api(sharePath),api(sharePath+(selectedId?'&':'?')+'expired=true')]) : [[],[]]
    if (sequence !== refreshSequence.current) return
    setHolders(result.holders);setInstitution(result.institution); setRole(result.role); setItems(result.items); setShares(active); setExpired(ended)
  }
  useEffect(()=>{ refresh().catch(()=>{}) },[])
  useEffect(()=>{
    if(!items.some(item=>['registered','dispatching','queued'].includes(item.state))) return
    const timer = window.setTimeout(()=>refresh().catch(()=>setMessage('Refresh to check issuance.')),3000)
    return ()=>clearTimeout(timer)
  },[items])
  function resetSession() {
    refreshSequence.current++
    setRole(null); setItems([]); setShares([]); setExpired([]); setPage(0); setQuery(''); setFilter(''); setDraft(example); setLink(''); setSelected(null)
  }
  async function run(action:()=>Promise<void>) {
    setBusy(true); setMessage('')
    try { await action() } catch(error){ if (error instanceof Error && error.message === 'Sign-in required.') resetSession(); setMessage(error instanceof Error ? error.message : 'Request failed.') }
    finally {setBusy(false)}
  }
  function signIn(e:FormEvent<HTMLFormElement>){
    e.preventDefault()
    const fields = Object.fromEntries(new FormData(e.currentTarget))
    void run(async()=>{await api('session','POST',fields); await refresh()})
  }
  const detailKey = new URLSearchParams(location.search).get('credential')
  const walletItem = role === 'holder' ? items.find(i=>i.id===detailKey) : undefined
  const receipt = items.find(item => item.id === selected)
  useEffect(() => { if (receipt && !detail.current?.open) detail.current?.showModal() }, [receipt])
  if (!role) return <section className="access-panel"><p className="eyebrow">Account access</p><h1>Staff and graduate sign-in</h1><form onSubmit={signIn}>
      <label>Fixture account<select name={account==="invited"?undefined:"member"} value={account} onChange={e=>setAccount(e.target.value)}><option value="fixture-registrar">Registrar · Juniper Valley</option><option value="fixture-holder">Graduate · Juniper Valley</option><option value="fixture-auditor">Auditor · Alder Ridge</option><option value="fixture-operator">Platform operator</option><option value="invited">Invited account</option></select></label>
      {account==="invited" && <label>Account ID<input required name="member" autoComplete="username"/></label>}
      <label>Local password<input type="password" name="password" placeholder="Enter your local password" required autoComplete="current-password"/></label>
      <button disabled={busy}>Sign in <span aria-hidden="true">↗</span></button>{account!=="invited" && <details><summary>Find my local password</summary><p>Run this in the project terminal and enter the result above.</p><code>docker compose exec -T web python flows.py {account}</code></details>}</form><p role="status">{message}</p></section>
  const titles = {holder:'Graduate wallet',registrar:'Registry evidence',admin:'University administration',superadmin:'Platform operations',auditor:'Institution workspace'}
  return <Dashboard role={role} institution={institution} title={titles[role]} busy={busy}
    onLogout={()=>void run(async()=>{await api('session','DELETE');resetSession()})}>
      {(role==='admin' || role==='superadmin') && <Management role={role}/>}
      {role==='registrar' && <div className="overview" aria-label="Institution overview"><span><strong>{items.length}</strong> credentials</span><span><strong>{items.filter(i=>i.state==='issued').length}</strong> issued</span><span><strong>{items.filter(i=>i.state==='draft').length}</strong> drafts</span><span><strong>{items.filter(i=>['queued','dispatching','registered'].includes(i.state)).length}</strong> pending</span><span><strong>{items.filter(i=>i.state==='review').length}</strong> in review</span></div>}
      {role==='registrar' && items.length>0 && <details className="distribution"><summary>Credential status distribution</summary><p>Current records · all award dates · {sourceName(items[0].mode || '')}</p>{Array.from(new Set(items.map(i=>i.state))).sort().map(state=>{
        const count=items.filter(i=>i.state===state).length
        return <div key={state}><span>{state}</span><meter aria-label={state} value={count} max={items.length}/><b>{count} of {items.length}</b></div>
      })}</details>}
      {role==='registrar' && <details className="issue-form" id="issue"><summary>Issue a diploma</summary><form className="draft-form" onSubmit={e=>{e.preventDefault(); const fields=Object.fromEntries(new FormData(e.currentTarget)); void run(async()=>{await api('diplomas','POST',fields);await refresh()})}}>
        <label>Graduate account<select name="holder" required>{holders.map(h=><option key={h}>{h}</option>)}</select></label>
        {Object.entries(example).map(([k,v])=><label key={k}>{labels[k as keyof typeof labels]}<input required name={k} value={draft[k as keyof typeof draft]} onChange={e=>setDraft({...draft,[k]:e.target.value})} placeholder={v} type={k==='award_date'?'date':'text'}/></label>)}
        <aside className="draft-preview"><small>Diploma preview · draft</small><h3>{draft.award_name} · {draft.program_name}</h3><p>{draft.subject_display_name} · {draft.award_date}</p><em>{institution}</em></aside><button disabled={busy || !holders.length}>{holders.includes("fixture-holder") ? "Create draft for fixture holder" : "Create diploma draft"}</button></form></details>}
      {role==='registrar' && <section className="records" id="records"><h3>Institution credentials</h3>
        <div className="register-tools"><label>Search credentials<input type="search" placeholder="Award, programme, ID or TAR" value={query} onChange={e=>{setQuery(e.target.value);setPage(0)}}/></label>
        <label>Issuance state<select value={filter} onChange={e=>{setFilter(e.target.value);setPage(0)}}><option value="">All states</option>{Array.from(new Set(items.map(i=>i.state))).sort().map(s=><option key={s}>{s}</option>)}</select></label></div>
        <table><thead><tr><th>Credential</th><th>Award date</th><th>State</th></tr></thead><tbody>
        {visibleRows.slice(currentPage*12,currentPage*12+12).map(item=><tr key={item.id}><td><button className="record-link" onClick={()=>setSelected(item.id)}>{item.snapshot.award_name} &middot; {item.snapshot.program_name}<small>{item.id}</small></button></td>
          <td>{item.snapshot.award_date}</td><td><span className={'state state-'+item.state}>{item.state}</span></td></tr>)}</tbody></table>
        <div className="pager"><span role="status">{visibleRows.length ? `Records ${currentPage*12+1}–${Math.min(currentPage*12+12,visibleRows.length)} of ${visibleRows.length}` : 'No credentials match this view.'}</span>{pageCount>1 && <><button className="secondary" disabled={currentPage===0} onClick={()=>setPage(currentPage-1)}>Previous</button><button className="secondary" disabled={currentPage+1>=pageCount} onClick={()=>setPage(currentPage+1)}>Next</button></>}</div>
        <dialog className="receipt-drawer" ref={detail} onClose={()=>setSelected(null)} aria-labelledby="receipt-heading">{receipt && <>
          <p className="eyebrow">{institution}</p><h2 id="receipt-heading">Evidence details</h2><p>{receipt.snapshot.award_name} &middot; {receipt.snapshot.program_name}</p>
          <dl><div><dt>Credential</dt><dd>{receipt.id}</dd></div><div><dt>Issuance state</dt><dd>{receipt.state}</dd></div></dl>
          <dl><div><dt>Matched TAR version</dt><dd>{receipt.version ?? 'Unavailable'}</dd></div><div><dt>Last issuance evidence match</dt><dd>{receipt.last_matched ? new Date(receipt.last_matched).toLocaleString() : 'Awaiting match'}</dd></div></dl><dl><div><dt>Environment</dt><dd>{receipt.mode ? sourceName(receipt.mode) : 'Unavailable'}</dd></div></dl><h3>Registry reference</h3>{receipt.reference ? <code>{receipt.reference}</code> : <p>No receipt recorded.</p>}
          {receipt.reference && <CopyField value={receipt.reference} label="Copy reference"/>}
          {receipt.reference?.startsWith('urn:tar:eip155.') && <dl><div><dt>Chain ID</dt><dd>{receipt.reference.split(':')[2].split('.')[1]}</dd></div><div><dt>Contract</dt><dd><code>{receipt.reference.split(':')[3]}</code></dd></div></dl>}
          <h3>Issuance-time TAR checksum</h3>{receipt.registry_checksum ? <><code>{receipt.registry_checksum}</code><CopyField value={receipt.registry_checksum} label="Copy checksum"/></> : <p>No TAR checksum stored for this record.</p>}
          <p>{receipt.state==='issued' ? 'Evidence matched when the institution issued this diploma. Open a current graduate share for a fresh check.' :
            receipt.state==='review' ? 'An operator must review the evidence before issuance.' : receipt.state==='registered' ? 'Receipt recorded. Independent readback is pending.' : receipt.state==='draft' ? 'Ready for registrar confirmation.' : 'Issuance is pending.'}</p>
          {receipt.state==='draft' && <button disabled={busy} onClick={()=>run(async()=>{await api('diplomas/'+receipt.id+'/issue','POST');await refresh();detail.current?.close()})}>Confirm issuance</button>}
          <button className="secondary" onClick={()=>detail.current?.close()}>Close details</button></>}</dialog></section>}
      {role==='holder' && <div className="overview"><span><strong>{items.length}</strong> diplomas</span><span><strong>{shares.length}</strong> {detailKey ? 'active links for this diploma' : 'active verification links'}</span></div>}
      {role==='holder' && <h2 id="wallet">My diplomas</h2>}
      {role==='holder' && <p>Each share reveals the award, programme, award date and issuer. Your name stays private.</p>}
      {role==='holder' && detailKey && <><a href="/?workspace&graduate">Back to wallet</a>{!walletItem && <p>Credential unavailable for this account.</p>}</>}
      {role!=='registrar' && (detailKey ? items.filter(i=>i.id===walletItem?.id) : items).map(i=><article key={i.id}><div className="wallet-paper" data-credential={i.id}><small>Academic credential · {institution}</small><strong>{i.snapshot.award_name} · {i.snapshot.program_name}</strong>
        <a href={'/?workspace&graduate&credential='+i.id}>Open credential details</a>
        {detailKey && <dl><div><dt>Issuer identifier</dt><dd>{i.snapshot.issuer_id}</dd></div><div><dt>Programme</dt><dd>{i.snapshot.program_name}</dd></div><div><dt>Award</dt><dd>{i.snapshot.award_name}</dd></div><div><dt>Award date</dt><dd>{i.snapshot.award_date}</dd></div></dl>}
        <p>{i.snapshot.subject_display_name} · {i.snapshot.award_date}</p><span className={'state state-'+i.state}>{i.state}</span>{i.reference && <details><summary>Registry reference</summary><code>{i.reference}</code></details>}</div>
        {role==='holder' && <button disabled={busy} onClick={()=>run(async()=>{const r=await api('diplomas/'+i.id+'/share','POST');setLink(location.origin+'/verify#t='+r.token);await refresh()})}>Share award, programme, date and institution</button>}</article>)}
      {!items.length && role!=="admin" && role!=="superadmin" && <p>No diplomas available for this account.</p>}
      {link && <div className="share-panel"><h3 tabIndex={-1} ref={sharePanel}>Verification link · 7 days</h3><QRCodeSVG value={link} size={144} title="Verification link QR code"/>
        <p><a href={link} target="_blank" rel="noreferrer">Open verification link</a></p>
        <button disabled={busy} onClick={()=>run(async()=>{await navigator.clipboard.writeText(link);setMessage('Verification link copied.')})}>Copy link</button>{' '}
        <button disabled={busy} onClick={()=>run(async()=>{await api('shares/disable','POST',{token:link.split('#t=')[1]});setLink('');setMessage('Share disabled.');await refresh()})}>Disable this link</button></div>}
      {role==='holder' && <div className="share-list" id="sharing"><h3>Active verification links</h3>
        {shares.length===0 ? <p>No active links.</p> : shares.map(share=><article key={share.id}>
          <div><strong>{share.programme}</strong><small>Link {share.id.slice(0,8)} · Expires {new Date(share.expires).toLocaleString()}</small></div>
          <button className="secondary" disabled={busy} aria-label={'Disable link '+share.id.slice(0,8)} onClick={()=>run(async()=>{
            await api('shares/'+share.id,'DELETE');setLink('');setMessage('Share disabled.');await refresh()
          })}>Disable link</button></article>)}</div>}
      {role==='holder' && <details className="expired-shares"><summary>Expired links ({expired.length})</summary>{expired.length ? expired.map(s=><p key={s.id}>{s.programme} · Expired {new Date(s.expires).toLocaleString()}</p>) : <p>No expired links in this view.</p>}</details>}
    <p role="status">{message}</p></Dashboard>
}

function CopyField({value,label}:{value:string,label:string}){
  const [message,setMessage]=useState('')
  return <><button className="secondary" onClick={async()=>{try{await navigator.clipboard.writeText(value);setMessage('Copied.')}catch{setMessage('Select the value above to copy it.')}}}>{label}</button> <small role="status">{message}</small></>
}

export function Verifier(){
  const [result,setResult] = useState<{status:string,source?:string,checked_at?:string,diploma?:Record<string,string>}>({status:'Checking proof…'})
  const [input,setInput] = useState('')
  const generation = useRef(0)
  useEffect(()=>{
    function checkLink() {
      const current = ++generation.current
      const token = new URLSearchParams(location.hash.slice(1)).get('t')
      history.replaceState(null,'',location.pathname)
      if (!token) { setResult({status:'Paste the link shared by the graduate.'});return }
      setResult({status:'Checking proof…'})
      api('public/verify','POST',{token})
        .then(value => { if (current === generation.current) setResult(value) })
        .catch(() => { if (current === generation.current) setResult({status:'Proof unavailable'}) })
    }
    checkLink()
    window.addEventListener('hashchange',checkLink)
    return () => { generation.current++; window.removeEventListener('hashchange',checkLink) }
  },[])
  const states:Record<string,string> = {verified_local_chain:'Registry and local blockchain evidence match',matched_simulator:'Local simulator records match',link_unavailable:'Link expired, disabled or unavailable',proof_unavailable:'Registry proof unavailable',evidence_mismatch:'Evidence mismatch',not_found:'Registry record missing'}
  const positive = result.status==='verified_local_chain' || result.status==='matched_simulator'
  const fieldNames:Record<string,string> = {award_name:'Award',program_name:'Programme',award_date:'Award date',issuer_id:'Issuer identifier'}
  return <><RegistryHeader source={result.source ? sourceName(result.source) : 'Public verification'}/><main className="verify">
    <p className="eyebrow">Public verification</p><h1>Verify a diploma</h1><p>Scan the shared QR code or paste their shared link. No account is required.</p>
    <form onSubmit={event=>{
      event.preventDefault()
      try {
        const url = new URL(input.trim())
        if (url.origin !== location.origin || url.pathname !== '/verify' || url.username || url.password || url.search || !/^#t=[A-Za-z0-9_-]{43}$/.test(url.hash)) throw new Error()
        setInput('');location.hash=url.hash
      } catch {
        generation.current++;setResult({status:'Enter a verification link from this Vertetify site.'})
      }
    }}><label>Verification link<input value={input} onChange={event=>setInput(event.target.value)} required autoComplete="off" spellCheck={false}/></label><button>Verify</button></form>
    <section className={'proof-card '+(result.status==='verified_local_chain'?'positive':result.status==='Checking proof…'?'loading':result.status==='evidence_mismatch'?'mismatch':'neutral')} aria-live="polite"><p className="eyebrow">{result.source ? sourceName(result.source) : "Evidence check"}</p><h2>{states[result.status] || result.status}</h2>
    {result.checked_at && <p className="checked">Checked <time dateTime={result.checked_at}>{new Date(result.checked_at).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'long'})}</time></p>}
    {positive && result.diploma && <dl>{Object.entries(result.diploma).map(([k,v])=><div key={k}><dt>{fieldNames[k] || k}</dt><dd>{v}</dd></div>)}</dl>}</section></main></>
}
