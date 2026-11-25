export function RegistryHeader({ source }: { source?: string }) {
  return <header className="masthead"><div className="mast-inner">
    <a className="wordmark" href="/" aria-label="Vertetify home"><img src="/vertetify-logo.png" width="2188" height="718" alt=""/></a>
    <nav aria-label="Main navigation"><a href="/#how">How it works</a><a href="/verify">Verify a diploma</a><a href="/?workspace">Sign in</a></nav>
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
