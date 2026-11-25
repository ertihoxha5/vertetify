import { useEffect, useState, type FormEvent } from 'react'
import { api } from './api'

type Account = {member:string,password:string}
type Application = {id:string,name:string,contact:string,state:string}
type Operations = {requests:Application[],mode:string,start:string,end:string,issuance:Record<string,number>,outcomes:Record<string,number>}
type Member = {member:string,role:string}

function useAction() {
  const [busy,setBusy]=useState(false)
  const [message,setMessage]=useState('')
  async function run(action:()=>Promise<void>) {
    setBusy(true);setMessage('')
    try {await action()} catch(e){setMessage(e instanceof Error ? e.message : 'Request unavailable.')}
    finally {setBusy(false)}
  }
  return {run,busy,message}
}
export function InstitutionAccess() {
  const [token]=useState(()=>new URLSearchParams(location.hash.slice(1)).get('invite'))
  const [request,setRequest]=useState(()=>new URLSearchParams(location.search).get('request') || '')
  const [status,setStatus]=useState('')
  const [account,setAccount]=useState<Account>()
  const {run,busy,message}=useAction()
  function check(){return run(async()=>setStatus((await api('access/requests/'+encodeURIComponent(request))).status))}
  useEffect(()=>{if(token)history.replaceState(null,'','/?access');if(request)void check()},[])
  function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault()
    const fields=Object.fromEntries(new FormData(event.currentTarget))
    void run(async()=>{const result=await api('access/requests','POST',fields)
      setRequest(result.id);setStatus(result.status);history.replaceState(null,'','/?access&request='+result.id)})
  }
  return <section className="access-panel"><p className="eyebrow">Institution access</p><h1>{token?'Activate your invitation':'Request institution access'}</h1>
    {token ? account ? <><p>Save these sign-in details privately. They are displayed once.</p><dl><div><dt>Account ID</dt><dd>{account.member}</dd></div><div><dt>Local password</dt><dd>{account.password}</dd></div></dl><a href="/?workspace&invited">Sign in with your account</a></> :
    <><p>Activate your single-use invitation to receive an institution-managed account.</p><button disabled={busy} onClick={()=>run(async()=>setAccount(await api('access/activate','POST',{token})))}>Activate invitation</button></> :
    request ? <><p role="status">Request status: {status || 'Checking'}</p><p>Bookmark this page to check progress. An operator provides the first administrator invitation after reviewing the request.</p><button disabled={busy} onClick={check}>Refresh status</button></> :
    <><p>Submit a synthetic institution for operator review. Approval creates a private invitation for its first administrator.</p><form onSubmit={submit}><label>Institution name<input name="name" required minLength={2} maxLength={120}/></label><label>Institution contact<input name="contact" type="email" required maxLength={180} placeholder="registrar@example.test"/></label><button disabled={busy}>Submit access request</button></form></>}
    <p role="status">{message}</p></section>
}
function Counts({title,values,description}:{title:string,values:Record<string,number>,description:string}) {
  const max=Math.max(1,...Object.values(values))
  return <section><h3>{title}</h3><p>{description}</p>{Object.values(values).some(Boolean) ?
    <table><caption>{title} by category</caption><thead><tr><th>Category</th><th>Count</th></tr></thead><tbody>
    {Object.entries(values).map(([key,n])=><tr key={key}><th scope="row">{key.replaceAll('_',' ')}</th><td><meter aria-hidden="true" min={0} max={max} value={n}/> {n}</td></tr>)}</tbody></table> : <p>No observations in this period.</p>}</section>
}
export function Management({role}:{role:'superadmin'|'admin'}) {
  const [ops,setOps]=useState<Operations>()
  const [health,setHealth]=useState<Record<string,string>>({})
  const [members,setMembers]=useState<Member[]>([])
  const [invite,setInvite]=useState('')
  const {run,busy,message}=useAction()
  async function refresh(){
    if(role==='admin')setMembers(await api('access/team'))
    else {
      setOps(await api('access/operations'))
      try {setHealth(await api('access/health'))} catch {setHealth({Registry:'Unavailable',Chain:'Unavailable'})}
    }
  }
  useEffect(()=>{void run(refresh)},[role])
  function invitation(path:string,data?:unknown){
    void run(async()=>{setInvite('');const r=await api(path,'POST',data);setInvite(location.origin+'/?access#invite='+r.token);await refresh()})
  }
  return <div className="management"><button className="secondary" disabled={busy} onClick={()=>run(refresh)}>Refresh workspace</button>
    <p role="status">{message || (busy?'Loading…':'')}</p>
    {invite && <section><h3>Private invitation</h3><p>Give this link privately to the intended recipient. It expires in 48 hours and can be used once.</p><input readOnly aria-label="Invitation link" value={invite} onFocus={e=>e.target.select()}/><button onClick={()=>setInvite('')}>Hide invitation</button></section>}
    {role==='admin' ? <><h3>Institution team</h3><form onSubmit={e=>{e.preventDefault();invitation('access/team/invite',Object.fromEntries(new FormData(e.currentTarget)))}}><label>Invitation role<select name="role"><option>registrar</option><option>auditor</option><option value="holder">Graduate</option></select></label><button disabled={busy}>Create invitation</button></form>
    {members.map(m=><article key={m.member}><div><strong>{m.role}</strong><small>{m.member}</small></div>{['registrar','auditor','inactive'].includes(m.role) && <form onSubmit={e=>{e.preventDefault();const data=Object.fromEntries(new FormData(e.currentTarget));void run(async()=>{await api('access/team/'+m.member+'/role','POST',data);await refresh()})}}><label>Staff permission<select name="role" defaultValue={m.role}><option>registrar</option><option>auditor</option><option>inactive</option></select></label><button disabled={busy}>Save permission</button></form>}</article>)}</> :
    ops && <><section><h3>Institution requests</h3>{ops.requests.length===0 && <p>No requests received.</p>}{ops.requests.map(r=><article key={r.id}><div><strong>{r.name}</strong><small>{r.contact} · {r.state}</small></div>{r.state!=='active' && <button disabled={busy} onClick={()=>invitation('access/requests/'+r.id+'/approve')}>{r.state==='pending'?'Approve and invite':'Replace invitation'}</button>}</article>)}</section>
    <section><h3>System health</h3><ol className="system-path" aria-label="Registry request path"><li>Vertetify API<small>Operations response received</small></li><li>Compellio Registry<small>{health.Registry || 'Checking'}</small></li><li>Local test chain<small>{health.Chain || 'Checking'}</small></li></ol></section>
    <p>{ops.start} through {ops.end} UTC · {ops.mode}</p>
    <Counts title="Issuance volume" values={ops.issuance} description="Distinct diplomas with a successful issuance evidence match per UTC day."/>
    <Counts title="Verification outcomes" values={ops.outcomes} description="Completed public verification requests by outcome since counting began, within this date range."/></>}
  </div>
}
