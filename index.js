#!/usr/bin/env node
/**
 * ContextForge — Node.js wrapper
 * 
 * Bu dosya, ContextForge'u npx ile çalıştırmak için bir wrapper'dır.
 * Arkada Python paketini kurar ve çalıştırır.
 * 
 * Kullanım:
 *   npx -y github:Qinshiaa/contextforge
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const REPO_PATH = __dirname;
const PYTHON_CMDS = ['python3', 'python', 'py'];

function findPython() {
  for (const cmd of PYTHON_CMDS) {
    try {
      execSync(`${cmd} --version`, { stdio: 'ignore' });
      return cmd;
    } catch {}
  }
  console.error(`
╔══════════════════════════════════════════════════════════════════╗
║  HATA: Python bulunamadı!                                        ║
║                                                                  ║
║  ContextForge Python 3.10+ gerektirir.                           ║
║  Lütfen Python kurun: https://python.org/downloads               ║
║                                                                  ║
║  son im crine😭 ama kurunca düzelir.                            ║
╚══════════════════════════════════════════════════════════════════╝
`);
  process.exit(1);
}

function isContextForgeInstalled(python) {
  try {
    execSync(`${python} -c "import contextforge"`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

function installContextForge(python) {
  console.log('🔧 ContextForge Python paketi kuruluyor...');
  try {
    // Önce pip'in varlığını kontrol et
    try {
      execSync(`${python} -m pip --version`, { stdio: 'ignore' });
    } catch {
      console.log('   pip kuruluyor...');
      execSync(`${python} -m ensurepip --upgrade`, { stdio: 'inherit' });
    }

    // Bu repo'dan kur
    execSync(`${python} -m pip install "${REPO_PATH}" --quiet`, { stdio: 'inherit' });
    console.log('✅ Kurulum tamamlandı.');
  } catch (e) {
    console.error(`
╔══════════════════════════════════════════════════════════════════╗
║  Kurulum hatası: ${e.message}                                    ║
║                                                                  ║
║  Manuel kurulum için:                                            ║
║    pip install git+https://github.com/Qinshiaa/contextforge.git ║
╚══════════════════════════════════════════════════════════════════╝
`);
    process.exit(1);
  }
}

async function main() {
  const python = findPython();

  if (!isContextForgeInstalled(python)) {
    installContextForge(python);
  }

  console.log('🚀 ContextForge başlatılıyor...');

  const child = spawn(python, ['-m', 'contextforge'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, PYTHONUNBUFFERED: '1' }
  });

  // stdin → child.stdin
  process.stdin.pipe(child.stdin);

  // child.stdout → process.stdout
  child.stdout.on('data', (data) => {
    process.stdout.write(data);
  });

  // child.stderr → process.stderr
  child.stderr.on('data', (data) => {
    process.stderr.write(data);
  });

  child.on('exit', (code) => {
    process.exit(code || 0);
  });

  process.on('SIGINT', () => {
    child.kill('SIGINT');
  });

  process.on('SIGTERM', () => {
    child.kill('SIGTERM');
  });
}

main();
