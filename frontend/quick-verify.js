#!/usr/bin/env node

/**
 * Quick Verification Script for ZUS Coffee AI Chatbot
 * Checks that all systems are ready to run
 */

const fs = require('fs');
const path = require('path');

console.log('\n╔════════════════════════════════════════════════╗');
console.log('║  ZUS Coffee AI Chatbot - Pre-Launch Verify    ║');
console.log('╚════════════════════════════════════════════════╝\n');

let allPassed = true;

// Check 1: Frontend structure
console.log('✓ Step 1: Checking Frontend Structure');
const requiredFiles = [
  'package.json',
  'public/index.html',
  'src/App.js',
  'src/index.js',
  'src/components/ChatWindow.js',
  'src/components/Message.js',
  'src/components/ToolBadge.js',
  '.env'
];

let structurePassed = true;
for (const file of requiredFiles) {
  const filePath = path.join(__dirname, file);
  if (!fs.existsSync(filePath)) {
    console.log(`  ✗ Missing: ${file}`);
    structurePassed = false;
    allPassed = false;
  }
}
if (structurePassed) {
  console.log('  ✓ All required files present\n');
} else {
  console.log('');
}

// Check 2: package.json
console.log('✓ Step 2: Checking package.json');
try {
  const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf-8'));
  
  const deps = ['react', 'react-dom', 'react-scripts'];
  const scripts = ['start', 'build', 'test'];
  
  let pkgPassed = true;
  deps.forEach(dep => {
    if (!pkg.dependencies[dep]) {
      console.log(`  ✗ Missing dependency: ${dep}`);
      pkgPassed = false;
      allPassed = false;
    }
  });
  
  scripts.forEach(script => {
    if (!pkg.scripts[script]) {
      console.log(`  ✗ Missing script: ${script}`);
      pkgPassed = false;
      allPassed = false;
    }
  });
  
  if (pkgPassed) {
    console.log('  ✓ All dependencies and scripts configured\n');
  } else {
    console.log('');
  }
} catch (e) {
  console.log(`  ✗ Error reading package.json: ${e.message}\n`);
  allPassed = false;
}

// Check 3: .env file
console.log('✓ Step 3: Checking .env Configuration');
try {
  const envPath = path.join(__dirname, '.env');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    if (envContent.includes('REACT_APP_BACKEND_URL')) {
      console.log('  ✓ REACT_APP_BACKEND_URL configured\n');
    } else {
      console.log('  ✗ REACT_APP_BACKEND_URL not found in .env\n');
      allPassed = false;
    }
  } else {
    console.log('  ✗ .env file not found\n');
    allPassed = false;
  }
} catch (e) {
  console.log(`  ✗ Error checking .env: ${e.message}\n`);
  allPassed = false;
}

// Check 4: CORS in main.py
console.log('✓ Step 4: Checking Backend CORS Configuration');
try {
  const mainPyPath = path.join(__dirname, '..', 'main.py');
  if (fs.existsSync(mainPyPath)) {
    const mainContent = fs.readFileSync(mainPyPath, 'utf-8');
    if (mainContent.includes('CORSMiddleware') && mainContent.includes('allow_origins')) {
      console.log('  ✓ CORS middleware configured in backend\n');
    } else {
      console.log('  ⚠ WARNING: CORS might not be configured. Run these commands:\n');
      console.log('     In main.py add:\n');
      console.log('     from fastapi.middleware.cors import CORSMiddleware\n');
      console.log('     app.add_middleware(\n');
      console.log('       CORSMiddleware,\n');
      console.log('       allow_origins=["http://localhost:3000"],\n');
      console.log('       allow_methods=["*"],\n');
      console.log('       allow_headers=["*"],\n');
      console.log('     )\n');
    }
  } else {
    console.log('  ℹ Backend (main.py) not found in parent directory\n');
  }
} catch (e) {
  console.log(`  ✗ Error checking backend: ${e.message}\n`);
}

// Check 5: Node modules
console.log('✓ Step 5: Checking Node Modules');
const nodeModulesPath = path.join(__dirname, 'node_modules');
if (fs.existsSync(nodeModulesPath)) {
  console.log('  ✓ node_modules folder found (dependencies installed)\n');
} else {
  console.log('  ⚠ node_modules not found. You need to run:\n');
  console.log('     npm install\n');
  console.log('  (This only needs to be done once)\n');
}

// Summary
console.log('╔════════════════════════════════════════════════╗');
if (allPassed && fs.existsSync(nodeModulesPath)) {
  console.log('║  ✓ All checks PASSED - Ready to launch!       ║');
  console.log('╚════════════════════════════════════════════════╝\n');
  
  console.log('📋 NEXT STEPS:\n');
  console.log('1. Make sure backend is running:');
  console.log('   - Open Terminal 1');
  console.log('   - cd C:\\Users\\osaam\\...\\AI_Eng_Ass');
  console.log('   - python main.py\n');
  
  console.log('2. Start frontend (in THIS terminal):');
  console.log('   - npm start\n');
  
  console.log('3. Open browser:');
  console.log('   - Navigate to http://localhost:3000\n');
  
  console.log('4. Start testing:');
  console.log('   - See TESTING_CHECKLIST.md for 10 comprehensive tests');
  console.log('   - See SETUP_GUIDE.md for detailed troubleshooting\n');
  
  process.exit(0);
} else if (allPassed) {
  console.log('║  ⚠ Minor issues found - see above              ║');
  console.log('╚════════════════════════════════════════════════╝\n');
  console.log('💡 TIP: Run "npm install" to fix dependency issues\n');
  process.exit(0);
} else {
  console.log('║  ✗ Some issues need to be fixed                ║');
  console.log('╚════════════════════════════════════════════════╝\n');
  process.exit(1);
}
