import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Input from "./pages/Input";
import Capture from "./pages/Capture";
import HtmlReplica from "./pages/HtmlReplica";
import Evaluation from "./pages/Evaluation";
//import Report from "./pages/Report";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/input" replace />} />
        <Route path="/input" element={<Input />} />
        <Route path="/capture" element={<Capture />} />
        <Route path="/html" element={<HtmlReplica />} />
        <Route path="/evaluation" element={<Evaluation />} />
        
      </Routes>
    </BrowserRouter>
  );
}

/**
 * <Route path="/report" element={<Report />} />
 */