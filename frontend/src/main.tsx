import { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './style.css'
import { Credentials, Verifier } from './credentials'
import { DiplomaArtwork, RegistryHeader } from './identity'

type Institution = { name: string, members: number }

function App() {
  const [mode,setMode] = useState<string | null>(null)
  const [schools, setSchools] = useState<Institution[]>([])
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading')
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    setState('loading')
    fetch('/api/workspace', {signal: controller.signal})
      .then(async response => {
        if (!response.ok) throw new Error()
        const result = await response.json()
        if (!['simulator','compellio-local'].includes(result.mode) || !Array.isArray(result.institutions)) throw new Error()
        setMode(result.mode)
        setSchools(result.institutions)
        setState('ready')
      })
      .catch(() => { if (!controller.signal.aborted) setState('error') })
    return () => controller.abort()
  }, [attempt])

  return <>
    <RegistryHeader source={mode === 'compellio-local' ? 'Compellio · local test blockchain' : mode === 'simulator' ? 'Local simulator' : state === 'error' ? 'Connection unavailable' : 'Connecting…'}/>
    <main className="workspace">
      <div className="hero"><div className="hero-copy"><p className="eyebrow">Academic credential registry</p>
        <h1>Registry <em>workspace</em></h1><p className="intro">Issue digital diplomas, manage graduate shares and verify academic records.</p></div>
        <DiplomaArtwork/>
      </div>
      <div className="workspace-grid"><Credentials/><section className="institutions"><p className="eyebrow">Directory</p><h2>Synthetic institutions</h2>
        <div aria-live="polite">{state === 'loading' ? <p>Loading institutions…</p> :
          state === 'error' ? <p>Workspace unavailable. <button onClick={() => setAttempt(attempt + 1)}>Retry</button></p> :
          schools.length === 0 ? <p>No fixtures loaded.</p> :
          schools.map(school => <article key={school.name}><span className="monogram" aria-hidden="true">{school.name.split(' ').slice(0,2).map(word=>word[0]).join('')}</span><div><strong>{school.name}</strong><small>{school.members} fixture {school.members === 1 ? 'member' : 'members'}</small></div></article>)}</div>
      </section></div><footer><span>Vertetify · BlockJump Kosovo</span><span>Synthetic credentials only</span></footer>
    </main></>
}

createRoot(document.getElementById('root')!).render(location.pathname === '/verify' ? <Verifier/> : <App />)
