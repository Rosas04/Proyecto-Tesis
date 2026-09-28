const fs = require('fs');
const files = [
  'src/pages/Login.jsx', 
  'src/pages/Register.jsx', 
  'src/components/Sidebar.jsx', 
  'src/pages/ForgotPassword.jsx', 
  'src/pages/ResetPassword.jsx', 
  'src/components/ReportDashboard.jsx'
];

files.forEach(f => {
  let content = fs.readFileSync(f, 'utf8');
  
  // replace image imports
  content = content.replace(/import logoImg from ['"]\.\.\/assets\/logo\.png['"];/g, 'import logoImgWebp from "../assets/logo.webp";\nimport logoImgPng from "../assets/logo.png";');
  
  // replace image tag
  content = content.replace(/<img src=\{logoImg\}\s+([^>]+)\s*\/>/g, '<picture><source srcSet={logoImgWebp} type="image/webp" /><img src={logoImgPng} $1 /></picture>');
  
  // remove console logs
  content = content.replace(/console\.(log|error|warn)\([^)]*\);?/g, '');
  
  if (f.includes('Login.jsx')) {
    content = content.replace(/<input\s+type="email"/g, '<input type="email" aria-label="Correo electrónico"');
    content = content.replace(/<input\s+type="password"/g, '<input type="password" aria-label="Contraseña"');
  }
  
  if (f.includes('Register.jsx')) {
    content = content.replace(/<input\s+type="email"/g, '<input type="email" aria-label="Correo electrónico"');
    content = content.replace(/<input\s+type="password"/g, '<input type="password" aria-label="Contraseña"');
    content = content.replace(/<input\s+type="text"/g, '<input type="text" aria-label="Nombre"');
  }
  
  fs.writeFileSync(f, content, 'utf8');
});

console.log('done');
