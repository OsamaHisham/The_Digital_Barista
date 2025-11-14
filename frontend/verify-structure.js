#!/usr/bin/env node

/**
 * Frontend Structure Verification Script
 * Checks that all required files exist and have correct content
 */

const fs = require('fs');
const path = require('path');

const REQUIRED_FILES = {
  root: [
    'package.json',
    '.env',
    '.gitignore',
    'README.md'
  ],
  public: [
    'index.html'
  ],
  src: [
    'index.js',
    'index.css',
    'App.js',
    'App.css'
  ],
  'src/components': [
    'ChatWindow.js',
    'ChatWindow.css',
    'Message.js',
    'Message.css',
    'ToolBadge.js',
    'ToolBadge.css'
  ]
};

const REQUIRED_FEATURES = {
  'src/components/ChatWindow.js': [
    'localStorage',
    'sessionId',
    'handleSendMessage',
    'handleReset',
    '/reset',
    'BACKEND_URL',
    'fetch',
    'tool_used',
    'ToolBadge'
  ],
  'src/components/Message.js': [
    'type',
    'content',
    'timestamp',
    'message-avatar',
    'message-content'
  ],
  'src/components/ToolBadge.js': [
    'Calculator',
    'Product RAG',
    'Outlet Text2SQL',
    'tool-badge'
  ]
};

function checkFileExists(filePath) {
  return fs.existsSync(filePath);
}

function checkFileContains(filePath, keywords) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const missing = keywords.filter(keyword => !content.includes(keyword));
  return {
    exists: true,
    missing: missing
  };
}

function verify() {
  console.log('========================================');
  console.log('Frontend Structure Verification');
  console.log('========================================\n');

  let allPassed = true;
  const frontendRoot = __dirname;

  // Check directory structure
  console.log('1. Checking directory structure...');
  for (const [dir, files] of Object.entries(REQUIRED_FILES)) {
    const dirPath = dir === 'root' ? frontendRoot : path.join(frontendRoot, dir);
    
    if (!fs.existsSync(dirPath) && dir !== 'root') {
      console.log(`   [FAIL] Missing directory: ${dir}`);
      allPassed = false;
      continue;
    }

    for (const file of files) {
      const filePath = path.join(dirPath, file);
      if (checkFileExists(filePath)) {
        console.log(`   [OK] ${dir}/${file}`);
      } else {
        console.log(`   [FAIL] Missing: ${dir}/${file}`);
        allPassed = false;
      }
    }
  }

  console.log('\n2. Checking required features in files...');
  for (const [filePath, keywords] of Object.entries(REQUIRED_FEATURES)) {
    const fullPath = path.join(frontendRoot, filePath);
    if (!checkFileExists(fullPath)) {
      console.log(`   [FAIL] File not found: ${filePath}`);
      allPassed = false;
      continue;
    }

    const check = checkFileContains(fullPath, keywords);
    if (check.missing.length === 0) {
      console.log(`   [OK] ${filePath} has all required features`);
    } else {
      console.log(`   [FAIL] ${filePath} missing features:`);
      check.missing.forEach(feature => {
        console.log(`        - ${feature}`);
      });
      allPassed = false;
    }
  }

  console.log('\n3. Checking package.json...');
  try {
    const packageJson = JSON.parse(
      fs.readFileSync(path.join(frontendRoot, 'package.json'), 'utf-8')
    );
    
    const requiredDeps = ['react', 'react-dom', 'react-scripts'];
    const requiredScripts = ['start', 'build', 'test'];
    
    const missingDeps = requiredDeps.filter(dep => !packageJson.dependencies[dep]);
    const missingScripts = requiredScripts.filter(script => !packageJson.scripts[script]);

    if (missingDeps.length === 0) {
      console.log('   [OK] All required dependencies present');
    } else {
      console.log('   [FAIL] Missing dependencies:', missingDeps);
      allPassed = false;
    }

    if (missingScripts.length === 0) {
      console.log('   [OK] All required npm scripts present');
    } else {
      console.log('   [FAIL] Missing npm scripts:', missingScripts);
      allPassed = false;
    }
  } catch (error) {
    console.log('   [FAIL] Error reading package.json:', error.message);
    allPassed = false;
  }

  console.log('\n4. Checking .env configuration...');
  const envPath = path.join(frontendRoot, '.env');
  if (checkFileExists(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    if (envContent.includes('REACT_APP_BACKEND_URL')) {
      console.log('   [OK] REACT_APP_BACKEND_URL configured');
    } else {
      console.log('   [FAIL] REACT_APP_BACKEND_URL not found in .env');
      allPassed = false;
    }
  }

  console.log('\n========================================');
  if (allPassed) {
    console.log('✓ All verification checks PASSED!');
    console.log('\nNext steps:');
    console.log('  1. npm install');
    console.log('  2. npm start');
    console.log('  3. Open http://localhost:3000');
  } else {
    console.log('✗ Some verification checks FAILED!');
    console.log('Please fix the issues above before running npm start.');
  }
  console.log('========================================');

  return allPassed ? 0 : 1;
}

process.exit(verify());
