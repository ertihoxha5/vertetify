import { useState } from 'react'
import { Disclosure } from './disclosure'

const previews = [
  ['University dashboard','dashboard','See the institution’s credential totals and registration workload.'],
  ['Diploma issuance','issue','Review the award, programme and graduate association before creating a draft.'],
  ['Graduate wallet','wallet','Open an award to review its details and choose what to share.'],
  ['Public result','result','Read the permitted fields and the evidence source for a single check.']
]

export function Showcase(){
  const [index,select]=useState(0)
  const [title,file,caption]=previews[index]
  return <section className="showcase"><div><p className="eyebrow">Product tour</p><h2>Inside Vertetify</h2>
    <div className="preview-choices">{previews.map(([label],i)=><button key={label} aria-pressed={index===i} onClick={()=>select(i)}>{label}<span aria-hidden="true">↗</span></button>)}</div></div>
    <figure aria-live="polite"><img key={file} loading="lazy" width="960" height="600" src={'/previews/'+file+'.webp'} alt={title+' interface with synthetic example data'}/><figcaption><b>Synthetic example</b> · {caption}</figcaption></figure></section>
}

export function EvidencePath(){
  return <section className="evidence-path"><p className="eyebrow">Verification architecture</p><h2>Where the evidence lives</h2>
    <ol>{[
      ['Academic credential','Vertetify keeps the institution’s diploma and its private nonce in PostgreSQL.'],
      ['Compellio Registry API','A Tokenised Asset Record (TAR) carries the commitment to that diploma.'],
      ['Local test blockchain','The versioned contract checksum anchors the canonical TAR payload.'],
      ['Public verification','A valid graduate share opens a fresh comparison and releases four permitted fields.']
    ].map(([title,text])=><li key={title}><strong>{title}</strong><p>{text}</p></li>)}</ol></section>
}

const pages:Record<string,[string,string,string,string]> = {
  platform:['The credential platform','Follow an academic award from the registrar’s desk to a recipient’s evidence check.','Explore the workflow','/?how'],
  universities:['For universities','Issue academic credentials and keep a traceable receipt for each registration.','Request institution access','/?access'],
  graduates:['For graduates','Your university connects your account to your awards. Choose a diploma and decide when to share it.','Open graduate wallet','/?workspace&graduate'],
  privacy:['Privacy and data handling','A share grants access to a limited view of one credential for seven days. The holder can disable it earlier.','Open public verifier','/verify']
}
export function EditorialPage({page}:{page:string}){
  const [title,body,label,url]=pages[page] || pages.platform
  return <div className="editorial guide"><header><p className="eyebrow">Vertetify / Platform guide</p><h1>{title}</h1><p>{body}</p><a className="ink-link" href={url}>{label} →</a></header>
    {page==='privacy' ? <Disclosure/> : page==='graduates' ? <><Disclosure/><p>Ask your institution for your graduate account. Open My diplomas, choose Share award, then send the link or show the QR code. Manage each share under Verification links.</p></> :
    page==='universities' ? <><section><h2>From approval to issuance</h2><ol><li>Submit an institution access request and keep the request status page.</li><li>Activate the approved first administrator invitation and invite staff.</li><li>A registrar creates a draft for an associated graduate and confirms issuance.</li></ol></section><EvidencePath/></> : <><Showcase/><EvidencePath/></>}
  </div>
}
export function Footer({source}:{source:string}){
  return <footer className="site-footer"><div><strong>Vertetify</strong><p>Academic credentials · BlockJump Kosovo</p><small>{source} · Synthetic credentials only</small></div>
    <div><b>Platform</b><a href="/?how">How it works</a><a href="/?page=privacy">Privacy and data handling</a></div>
    <div><b>Access</b><a href="/?workspace">Staff and graduate sign-in</a><a href="/?access">Request institution access</a></div>
    <div><b>Have a shared link?</b><a href="/verify">Verify a diploma →</a></div></footer>
}
