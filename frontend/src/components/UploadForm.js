import React, { useState } from "react";

export default function UploadForm({ apiBase }) {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMsg("Select a file first.");
      return;
    }
    const fd = new FormData();
    fd.append("file", file);
    try {
      const res = await fetch(`${apiBase}/upload`, {
        method: "POST",
        body: fd
      });
      const data = await res.json();
      if (data.ok) setMsg(`Uploaded OK: ${data.rows} rows.`);
      else setMsg(`Upload failed: ${data.error}`);
    } catch (err) {
      setMsg("Upload error: " + err.message);
    }
  };

  return (
    <div className="mb-3">
      <form onSubmit={onSubmit}>
        <label className="form-label">Upload dataset (Excel)</label>
        <input className="form-control" type="file" accept=".xlsx,.xls"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button className="btn btn-primary mt-2" type="submit">
          Upload
        </button>
      </form>
      {msg && <div className="alert alert-info mt-2">{msg}</div>}
    </div>
  );
}
