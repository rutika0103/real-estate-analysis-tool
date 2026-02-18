import React, { useState } from "react";

export default function QueryBox({ apiBase }) {
  const [area, setArea] = useState("");
  const [compare, setCompare] = useState("");
  const [result, setResult] = useState(null);
  const [compResult, setCompResult] = useState(null);
  


  const analyze = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`${apiBase}/analyze?area=${encodeURIComponent(area)}`);
      setResult(await res.json());
    } catch (e) {
      setResult({ ok: false, error: e.message });
    } finally {
      setLoading(false);
    }
  };

  const doCompare = async () => {
    setLoading(true);
    setCompResult(null);
    try {
      const res = await fetch(`${apiBase}/compare?areas=${encodeURIComponent(compare)}`);
      setCompResult(await res.json());
    } catch (e) {
      setCompResult({ ok: false, error: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-3">
        <label>Analyze area</label>
        <div className="input-group">
          <input className="form-control"
            value={area}
            onChange={(e) => setArea(e.target.value)}
            placeholder="Wakad"
          />
          <button className="btn btn-primary" onClick={analyze}>
            Analyze
          </button>
        </div>
      </div>

      <div className="mb-3">
        <label>Compare multiple areas</label>
        <div className="input-group">
          <input className="form-control"
            value={compare}
            onChange={(e) => setCompare(e.target.value)}
            placeholder="Wakad,Baner,Hinjewadi"
          />
          <button className="btn btn-secondary" onClick={doCompare}>
            Compare
          </button>
        </div>
      </div>

      {result && (
        <pre style={{ background: "#eee", padding: 10 }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}

      {compResult && (
        <pre style={{ background: "#eee", padding: 10 }}>
          {JSON.stringify(compResult, null, 2)}
        </pre>
      )}
    </div>
  );
}
