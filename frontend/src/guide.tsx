import { useState } from 'react'

const steps = [
  ['Issue', 'A university seals the award', 'A Juniper registrar confirms a synthetic BSc in Computer Science. Vertetify stores the diploma privately and registers a commitment through the Registry.'],
  ['Share', 'The graduate chooses the audience', 'The graduate opens their wallet, previews the four disclosure fields and creates a seven-day verification link with a QR code.'],
  ['Verify', 'A recipient checks the evidence', 'The recipient opens the shared link. Vertetify checks its validity and compares the diploma commitment with the recorded evidence.']
]
export function ProductGuide() {
  const [step, select] = useState(0)
  return <div className="guide" id="how">
    <section className="tour"><div><p className="eyebrow">Synthetic example · Juniper Valley</p><h2>How it works</h2>
      <div className="step-buttons" aria-label="Walkthrough steps">{steps.map(([title],index)=><button key={title} aria-pressed={step===index} onClick={()=>select(index)}>{title}</button>)}</div></div>
      <div aria-live="polite"><div className="step-content" key={step}><h3>{steps[step][1]}</h3><p>{steps[step][2]}</p></div></div></section>
    <section><h2>What gets verified?</h2><p>A local-chain match confirms that the sealed diploma corresponds to the Registry record and the checksum on the local test blockchain. The university issues the award. Accreditation and the identity of the person presenting a link require separate checks.</p>
    <p>The recipient sees the issuer identifier, award, programme and award date. A simulator result is labeled separately.</p></section>
    <section className="entry-grid" aria-label="Choose your workspace">
    <div><h3>Universities</h3><p>Request access for your institution or sign in to issue diplomas.</p><a href="/?access">Request institution access</a></div>
    <div><h3>Graduates</h3><p>Open your wallet to review your diplomas and manage verification links.</p><a href="/?workspace&graduate">Open graduate wallet</a></div>
    <div><h3>Verifiers</h3><p>Check a diploma shared with you by a graduate.</p><a href="/verify">Open public verifier</a></div></section>
    <section><h2>Common questions</h2>{[
      ['Do I need an account?', 'Anyone with a valid shared link can verify. Issuing and sharing require an authorized account.'],
      ['How do I get a shared link?', 'Ask the graduate to create one in their wallet. A QR code opens the same link.'],
      ['Why has my link stopped working?', 'A link expires after seven days. The graduate can also disable it earlier. Ask for a new link.'],
      ['What if the evidence is unavailable?', 'Try again later. The verifier withholds diploma details when evidence cannot be confirmed.']
    ].map(([question,answer])=><details key={question}><summary>{question}</summary><p>{answer}</p></details>)}</section>
  </div>
}
