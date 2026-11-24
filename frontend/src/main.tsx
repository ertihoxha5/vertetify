import { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './style.css'
import { Credentials, Verifier } from './credentials'

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
    <header><b>Vertetify</b><span>{mode === 'compellio-local' ? 'Compellio · local test blockchain' : mode === 'simulator' ? 'Local simulator' : 'Connecting…'}</span></header>
    <main><p className="eyebrow">BlockJump Kosovo · Certifications</p>
      <h1>Registry workspace</h1><p className="intro">Explore the fictional institutions prepared for local diploma verification rehearsals.</p>
      <Credentials/><section><h2>Synthetic institutions</h2>
        <div aria-live="polite">{state === 'loading' ? <p>Loading institutions…</p> :
          state === 'error' ? <p>Workspace unavailable. <button onClick={() => setAttempt(attempt + 1)}>Retry</button></p> :
          schools.length === 0 ? <p>No fixtures loaded.</p> :
          schools.map(school => <article key={school.name}><strong>{school.name}</strong><span>{school.members} fixture {school.members === 1 ? 'member' : 'members'}</span></article>)}</div>
      </section><footer>All records shown here are synthetic.</footer>
    </main></>
}

createRoot(document.getElementById('root')!).render(location.pathname === '/verify' ? <Verifier/> : <App />)
