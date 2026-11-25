export function RegistryHeader({ source }: { source: string }) {
  return <header className="masthead">
    <div className="mast-inner">
      <div className="wordmark"><i aria-hidden="true">V</i> Vertetify</div>
      <span className="network"><span aria-hidden="true" />{source}</span>
    </div>
  </header>
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
