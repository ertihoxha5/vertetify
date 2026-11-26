import { useState } from 'react'

const destinations = [
  ['Platform','/?page=platform'], ['How it works','/?how'], ['For universities','/?page=universities'],
  ['For graduates','/?page=graduates'], ['Verify a diploma','/verify'], ['Sign in','/?workspace'],
  ['Request institution access','/?access']
]
export function RegistryHeader({ source, workspace }: { source?: string, workspace?:boolean }) {
  const [open,setOpen]=useState(false)
  return <header className="masthead"><div className="mast-inner">
    <a className="wordmark" href="/" aria-label="Vertetify home"><img src="/vertetify-logo.png" width="2188" height="718" alt=""/></a>
    <button className="menu-toggle secondary" aria-expanded={open} aria-controls="main-nav" onClick={()=>setOpen(!open)}>{open?'Close menu':'Menu'}</button>
    <nav id="main-nav" data-open={open} aria-label="Main navigation" onKeyDown={e=>{if(e.key==='Escape'){setOpen(false);document.querySelector<HTMLButtonElement>('.menu-toggle')?.focus()}}}>
      {destinations.filter(([label])=>!workspace || label!=='Sign in').map(([label,url])=><a key={url} href={url}>{label}</a>)}</nav>
  </div>{source && <div className="source-line">{source}</div>}</header>
}

export function DiplomaArtwork() {
  return <div className="artwork" aria-hidden="true">
    <div className="paper shadow-paper" />
    <div className="paper diploma-paper">
      <div className="paper-top">VERTETIFY <span>ACADEMIC REGISTRY</span></div>
      <div className="paper-title">Diploma</div>
      <div className="rule long" /><div className="rule" />
      <div className="medallion"><div className="rosette">
        {Array.from({length:20}, (_,i) => <i key={i} style={{transform:`rotate(${i*9}deg)`}} />)}
        <b>V</b>
      </div></div>
      <div className="paper-bottom">SYNTHETIC SPECIMEN</div>
    </div>
  </div>
}
