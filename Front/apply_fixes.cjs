const fs = require('fs');
const path = require('path');

function walkDir(dir, callback) {
  fs.readdirSync(dir).forEach(f => {
    let dirPath = path.join(dir, f);
    let isDirectory = fs.statSync(dirPath).isDirectory();
    isDirectory ? walkDir(dirPath, callback) : callback(dirPath);
  });
}

walkDir('src', function(filePath) {
  if (!filePath.endsWith('.jsx')) return;
  
  let content = fs.readFileSync(filePath, 'utf8');
  let originalContent = content;

  // 1. Remove console.logs
  content = content.replace(/console\.(log|error|warn)\([^)]*\);?/g, '');

  // 2. Image WebP fixes
  if (
    filePath.includes('Login.jsx') || 
    filePath.includes('Register.jsx') || 
    filePath.includes('Sidebar.jsx') || 
    filePath.includes('ForgotPassword.jsx') || 
    filePath.includes('ResetPassword.jsx') || 
    filePath.includes('ReportDashboard.jsx')
  ) {
    // Both double and single quotes
    content = content.replace(/import logoImg from ["']\.\.\/assets\/logo\.png["'];/g, 'import logoImgWebp from "../assets/logo.webp";\nimport logoImgPng from "../assets/logo.png";');
    content = content.replace(/import heroImg from ["']\.\.\/assets\/hero\.png["'];/g, 'import heroImgWebp from "../assets/hero.webp";\nimport heroImgPng from "../assets/hero.png";');
    
    content = content.replace(/<img src=\{logoImg\}\s+([^>]+)\s*\/>/g, '<picture><source srcSet={logoImgWebp} type="image/webp" /><img src={logoImgPng} $1 /></picture>');
    content = content.replace(/<img src=\{heroImg\}\s+([^>]+)\s*\/>/g, '<picture><source srcSet={heroImgWebp} type="image/webp" /><img src={heroImgPng} $1 /></picture>');
  }

  // 3. aria-labels in forms
  if (filePath.includes('Login.jsx')) {
    content = content.replace(/<input\s+type="email"/g, '<input type="email" aria-label="Correo electrónico"');
    content = content.replace(/<input\s+type="password"/g, '<input type="password" aria-label="Contraseña"');
  }
  
  if (filePath.includes('Register.jsx')) {
    content = content.replace(/<input\s+type="email"/g, '<input type="email" aria-label="Correo electrónico"');
    content = content.replace(/<input\s+type="password"/g, '<input type="password" aria-label="Contraseña"');
    content = content.replace(/<input\s+type="text"/g, '<input type="text" aria-label="Nombre"');
  }
  
  if (filePath.includes('Input.jsx')) {
    content = content.replace(/<input\s+type="text"\s+placeholder="https/g, '<input type="text" aria-label="URL del proyecto" required placeholder="https');
    content = content.replace(/<input\s+type="file"\s+accept="\.zip"/g, '<input type="file" aria-label="Archivo ZIP del proyecto" required accept=".zip"');
  }

  // 4. aria-labels in scroll buttons
  if (filePath.includes('Capture.jsx') || filePath.includes('HtmlReplica.jsx')) {
    content = content.replace(/<button\s+className="tabs-scroll-btn"\s+onClick=\{[^}]*left: -200[^}]*\}\s*>/g, '<button className="tabs-scroll-btn" aria-label="Desplazar a la izquierda" onClick={() => tabsRef.current?.scrollBy({ left: -200, behavior: "smooth" })}>');
    content = content.replace(/<button\s+className="tabs-scroll-btn"\s+onClick=\{[^}]*left: 200[^}]*\}\s*>/g, '<button className="tabs-scroll-btn" aria-label="Desplazar a la derecha" onClick={() => tabsRef.current?.scrollBy({ left: 200, behavior: "smooth" })}>');
  }

  // 5. History.jsx
  if (filePath.includes('History.jsx')) {
    content = content.replace(
      /const MoreIcon = \(\) => \(\s*<svg[^>]+>\s*<circle[^>]+><\/circle>\s*<circle[^>]+><\/circle>\s*<circle[^>]+><\/circle>\s*<\/svg>\s*\);/g, 
      'const DownloadIcon = () => (<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>);'
    );
    content = content.replace(/<button className="btn-more"/g, '<button className="btn-more" aria-label="Descargar PDF"');
    content = content.replace(/<MoreIcon \/>/g, '<DownloadIcon />');
  }

  // 6. Report.jsx
  if (filePath.includes('Report.jsx')) {
    if (!content.includes('import { ReportWebDashboard }')) {
      content = content.replace(/import { useNavigate } from "react-router-dom";/, 'import { useNavigate } from "react-router-dom";\nimport { ReportWebDashboard } from "../components/ReportWebDashboard";');
    }
    
    const blockToReplaceRegex = /\{\!loading && reportResult && \(\s*<div className="pdf-card"[\s\S]*?<\/div>\s*\)\}/;
    const newBlock = `{!loading && reportResult && (
          <ReportWebDashboard 
            reportResult={reportResult} 
            summary={summary} 
            findings={findings} 
            scores={scores} 
            sourceLabel={sourceLabel} 
            inputType={inputType} 
            getScoreColorUI={getScoreColorUI} 
            getScoreLabelUI={getScoreLabelUI} 
            getBadgeClassUI={getBadgeClassUI} 
          />
        )}`;
    content = content.replace(blockToReplaceRegex, newBlock);
  }

  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
  }
});

console.log('done');
