import { useEffect, useState } from "react";
import { healthCheck } from "../services/api";

function Dashboard() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    healthCheck()
      .then((data) => {
        setStatus(data.status);
      })
      .catch(() => {
        setStatus("Backend unavailable");
      });
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <p className="mt-4">
        Backend status: <strong>{status}</strong>
      </p>
    </div>
  );
}

export default Dashboard;
