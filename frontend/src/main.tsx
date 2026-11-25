import { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './style.css'
import { Credentials, Verifier } from './credentials'
import { DiplomaArtwork, RegistryHeader } from './identity'

function App() {
  const [source, setSource] = useState('Checking environment…')
  const workspace = new URLSearchParams(location.search).has('workspace')
  useEffect(() => {
    fetch('/api/workspace').then(async response => {
      if (!response.ok) throw new Error()
      const {mode} = await response.json()
      setSource(mode === 'compellio-local' ? 'Compellio · local test blockchain' :
        mode === 'simulator' ? 'Local simulator' : 'Unknown environment')
    }).catch(() => setSource('Environment unavailable'))
  }, [])
  return <><RegistryHeader/><main className={workspace ? 'workspace' : 'landing'}>
    {workspace ? <Credentials/> : <>
      <section className="hero"><div className="hero-copy">
        <h1><span>Digital diplomas.</span><em>Verifiable by anyone.</em></h1>
        <p className="intro">Universities issue. Graduates share. Anyone with a shared link can verify.</p>
        <div className="actions"><a href="/verify">Verify a diploma</a><a href="/?workspace">Staff and graduate sign-in</a></div>
      </div><DiplomaArtwork/></section>
      <section className="steps" id="how" aria-label="How it works">
        <div><h2>Issue</h2><p>A registrar issues the diploma and registers its proof.</p></div>
        <div><h2>Share</h2><p>The graduate chooses when to share a seven-day link or QR code.</p></div>
        <div><h2>Verify</h2><p>Open the shared link to check the evidence and see the disclosed award details.</p></div>
      </section></>}
    <footer><span>{source}</span><span>Synthetic credentials only</span></footer></main></>
}
createRoot(document.getElementById('root')!).render(location.pathname === '/verify' ? <Verifier/> : <App/>)
