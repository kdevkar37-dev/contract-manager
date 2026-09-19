import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Login from "./pages/login";
import Dashboard from "./pages/dashboard";
import Contracts from "./pages/contracts";
import ContractDetails from "./pages/contractDetails";
import MainLayout from "./layouts/mainLayout";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<MainLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/contracts" element={<Contracts />} />
          <Route
            path="/contracts/:contractId"
            element={<ContractDetails />}
          />
        </Route>

        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;