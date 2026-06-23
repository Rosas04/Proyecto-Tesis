import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";

import Input from "./pages/Input";
import Capture from "./pages/Capture";
import HtmlReplica from "./pages/HtmlReplica";
import Evaluation from "./pages/Evaluation";
import Report from "./pages/Report";

import ProtectedRoute from "./routes/ProtectedRoute";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/register" replace />} />

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/input"
          element={
            <ProtectedRoute>
              <Input />
            </ProtectedRoute>
          }
        />

        <Route
          path="/capture"
          element={
            <ProtectedRoute>
              <Capture />
            </ProtectedRoute>
          }
        />

        <Route
          path="/html"
          element={
            <ProtectedRoute>
              <HtmlReplica />
            </ProtectedRoute>
          }
        />

        <Route
          path="/evaluation"
          element={
            <ProtectedRoute>
              <Evaluation />
            </ProtectedRoute>
          }
        />

        <Route
          path="/report"
          element={
            <ProtectedRoute>
              <Report />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}