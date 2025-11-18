import React from "react";
import UploadForm from "./components/UploadForm";
import QueryBox from "./components/QueryBox";

function App() {
  const apiBase = "http://127.0.0.1:8000";

  return (
    <div className="container p-4">
      <h2>Real Estate Analysis Tool</h2>
      <UploadForm apiBase={apiBase} />
      <QueryBox apiBase={apiBase} />
    </div>
  );
}

export default App;
