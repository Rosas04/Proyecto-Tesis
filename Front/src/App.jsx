import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import ProtectedRoute from "./routes/ProtectedRoute";
import { AnalysisProvider } from "./context/AnalysisContext.jsx";

// Carga diferida por ruta: las páginas pesadas (jsPDF, html2canvas, recharts)
// sólo se descargan cuando el usuario las visita.
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const ForgotPassword = lazy(() => import("./pages/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/ResetPassword"));

const Home = lazy(() => import("./pages/Home"));
const Input = lazy(() => import("./pages/Input"));
const Capture = lazy(() => import("./pages/Capture"));
const HtmlReplica = lazy(() => import("./pages/HtmlReplica"));
const Evaluation = lazy(() => import("./pages/Evaluation"));
const Report = lazy(() => import("./pages/Report"));

const History = lazy(() => import("./pages/History.jsx"));
const InterfaceTabs = lazy(() => import("./components/InterfaceTabs.jsx"));

function PageLoader() {
  return (
    <div style={{ padding: "40px", fontFamily: "Helvetica" }}>
      Cargando...
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AnalysisProvider>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/input" element={<ProtectedRoute><Input /></ProtectedRoute>} />
            <Route path="/capture" element={<ProtectedRoute><Capture /></ProtectedRoute>} />
            <Route path="/html" element={<ProtectedRoute><HtmlReplica /></ProtectedRoute>} />
            <Route path="/evaluation" element={<ProtectedRoute><Evaluation /></ProtectedRoute>} />
            <Route path="/report" element={<ProtectedRoute><Report /></ProtectedRoute>} />
            <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
            <Route path="/interfaces" element={<ProtectedRoute><InterfaceTabs /></ProtectedRoute>} />
          </Routes>
        </Suspense>
      </AnalysisProvider>
    </BrowserRouter>
  );
}
