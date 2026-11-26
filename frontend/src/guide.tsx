import { useEffect, useRef, useState } from 'react'
import { Showcase, EvidencePath } from './editorial'
import { Disclosure } from './disclosure'

const steps = [
  ['University', 'A university seals the award', 'A Juniper registrar confirms a synthetic BSc in Computer Science. Vertetify stores the diploma privately before registration.'],
  ['Registry', 'A fingerprint goes on record', 'Vertetify sends a commitment to the Compellio Registry. It reads back the TAR and compares its checksum with the local contract.'],
  ['Graduate', 'The graduate chooses the audience', 'The graduate opens their wallet, previews the four disclosure fields and creates a seven-day verification link with a QR code.'],
  ['Verifier', 'A recipient checks the evidence', 'The recipient opens the shared link. Vertetify checks its validity and compares the diploma commitment with the recorded evidence.']
]
export function ProductGuide() {
  const [step, select] = useState(0)
  const guide=useRef<HTMLDivElement>(null)
  useEffect(()=>{
    if (!guide.current || !('IntersectionObserver' in window)) return
    const observer=new IntersectionObserver(entries=>{
      for(const entry of entries) if(entry.isIntersecting) {
        entry.target.classList.add('in-view')
        observer.unobserve(entry.target)
      }
    },{threshold:0.08})
    guide.current.querySelectorAll(':scope > section').forEach(section=>observer.observe(section))
    return ()=>observer.disconnect()
  },[])
  return <div className="guide" ref={guide} id="how">
    <section className="tour"><div><p className="eyebrow">Synthetic example · Juniper Valley</p><h2>How it works</h2>
      <div className="step-buttons" aria-label="Walkthrough steps">{steps.map(([title],index)=><button key={title} aria-pressed={step===index} onClick={()=>select(index)}>{title}</button>)}</div></div>
      <div aria-live="polite"><div className="step-content" key={step}><h3>{steps[step][1]}</h3><p>{steps[step][2]}</p>
        <dl className="step-specimen">{[
          [['Award','BSc'],['Programme','Computer Science']],
          [['TAR payload','Diploma commitment'],['Contract check','Version checksum']],
          [['Visible to recipient','Four academic fields'],['Link lifetime','Seven days']],
          [['Compared on request','Diploma, TAR and chain'],['If evidence is unavailable','Details withheld']]
        ][step].map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
      </div></div></section>
    <Showcase/><EvidencePath/><Disclosure/>
    <section className="entry-grid" id="entry" aria-label="Choose your workspace">
    <div><h3>Universities</h3><p>Request access for your institution or sign in to issue diplomas.</p><a href="/?access">Request institution access</a></div>
    <div><h3>Graduates</h3><p>Open your wallet to review your diplomas and manage verification links.</p><a href="/?workspace&graduate">Open graduate wallet</a></div>
    <div><h3>Verifiers</h3><p>Check a diploma shared with you by a graduate.</p><a href="/verify">Open public verifier</a></div></section>
    <section className="questions"><h2>Common questions</h2><div>{[
      ['Do I need an account?', 'Anyone with a valid shared link can verify. Issuing and sharing require an authorized account.'],
      ['How do I get a shared link?', 'Ask the graduate to create one in their wallet. A QR code opens the same link.'],
      ['Why has my link stopped working?', 'A link expires after seven days. The graduate can also disable it earlier. Ask for a new link.'],
      ['Does a match establish accreditation?', 'A match confirms integrity on the selected registry. Check accreditation and the identity of the person presenting the diploma separately.'],
      ['Which registry did my result use?', 'Each result identifies the local Compellio test chain or the development simulator and shows when the check ran.'],
      ['What if the evidence is unavailable?', 'Try again later. The verifier withholds diploma details when evidence cannot be confirmed.']
    ].map(([question,answer])=><details key={question}><summary>{question}</summary><p>{answer}</p></details>)}</div></section>
    <section className="final-action"><h2>Received a diploma?</h2><a className="ink-link" href="/verify">Open the verifier →</a></section>
  </div>
}
