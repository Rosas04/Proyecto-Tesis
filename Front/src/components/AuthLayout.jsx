import heroImg from "../assets/auth-hero.png";
import logoImgWebp from "../assets/logo.webp";
import logoImgPng from "../assets/logo.png";
import "./AuthLayout.css";

export default function AuthLayout({ title, subtitle, children }) {
  return (
    <main className="split-page">
      <aside className="split-hero" aria-hidden="true">
        <img src={heroImg} alt="" />
      </aside>

      <section className="split-panel">
        <div className="split-content">
          <div className="split-brand">
            <picture>
              <source srcSet={logoImgWebp} type="image/webp" />
              <img src={logoImgPng} alt="FrontMind AI" className="split-logo" />
            </picture>
            <span>FrontMind <b>AI</b></span>
          </div>

          <h1>{title}</h1>
          <p className="split-subtitle">{subtitle}</p>

          {children}
        </div>
      </section>
    </main>
  );
}

const iconProps = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
};

export function EyeIcon({ off }) {
  return (
    <svg {...iconProps}>
      {off ? (
        <>
          <path d="M17.94 17.94A10.9 10.9 0 0 1 12 20c-7 0-11-8-11-8a19.8 19.8 0 0 1 5.06-5.94M9.9 4.24A10.9 10.9 0 0 1 12 4c7 0 11 8 11 8a19.8 19.8 0 0 1-3.17 4.19M1 1l22 22" />
          <path d="M14.12 14.12A3 3 0 1 1 9.88 9.88" />
        </>
      ) : (
        <>
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z" />
          <circle cx="12" cy="12" r="3" />
        </>
      )}
    </svg>
  );
}

export function MailIcon() {
  return (
    <svg {...iconProps}>
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m3 7 9 6 9-6" />
    </svg>
  );
}

export function LockIcon() {
  return (
    <svg {...iconProps}>
      <rect x="4" y="11" width="16" height="10" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </svg>
  );
}
