#!/usr/bin/env node
const { spawn, execSync } = require('child_process');
const REPO_PATH = __dirname;

function findPython() {
  const cmds = process.platform === 'win32' 
    ? ['python', 'py', 'python3'] 
    : ['python3', 'python', 'py'];
  
  for (const cmd of cmds) {
    try {
      execSync(`${cmd} --version`, { stdio: 'ignore' });
      console.error(`✅ Python bulundu: ${cmd}`);  // ← console.error
      return cmd;
    } catch {}
  }
  console.error("❌ Python bulunamadı! python.org'dan kur.");
  process.exit(1);
}

function isInstalled(python) {
  try {
    execSync(`${python} -c "import contextforge"`, { stdio: 'ignore' });
    return true;
  } catch { return false; }
}

function install(python) {
  console.error('🔧 ContextForge Python paketi kuruluyor...');
  try {
    execSync(`${python} -m pip install "${REPO_PATH}" --quiet`, { 
      stdio: 'inherit', cwd: REPO_PATH 
    });
    console.error('✅ Kurulum tamamlandı.');
  } catch (e) {
    console.error('❌ Kurulum hatası:', e.message);
    process.exit(1);
  }
}

async function main() {
  const python = findPython();
  if (!isInstalled(python)) install(python);
  console.error('🚀 ContextForge başlatılıyor...');
  
  const child = spawn(python, ['-m', 'contextforge'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, PYTHONUNBUFFERED: '1' }
  });
  
  process.stdin.pipe(child.stdin);
  child.stdout.pipe(process.stdout);   // ← SADECE MCP mesajları
  child.stderr.pipe(process.stderr);   // ← Loglar buraya
  
  child.on('exit', (code) => process.exit(code || 0));
  process.on('SIGINT', () => child.kill('SIGINT'));
}

main();