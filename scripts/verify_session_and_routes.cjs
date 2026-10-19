/**
 * CSIC Session Reliability, LocalStorage Resiliency & Route Verification Suite
 */
const fs = require('fs');
const path = require('path');
const assert = require('assert');

console.log('='.repeat(70));
console.log('CSIC SESSION RELIABILITY & REFRESH/ROUTING AUDIT');
console.log('='.repeat(70));

let passCount = 0;
let failCount = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`[PASS] ${name}`);
    passCount++;
  } catch (err) {
    console.error(`[FAIL] ${name}: ${err.message}`);
    failCount++;
  }
}

// Mock localStorage simulation for node
class MockLocalStorage {
  constructor() {
    this.store = {};
  }
  getItem(key) {
    return this.store[key] || null;
  }
  setItem(key, val) {
    this.store[key] = String(val);
  }
  removeItem(key) {
    delete this.store[key];
  }
  clear() {
    this.store = {};
  }
}

const mockStorage = new MockLocalStorage();
global.localStorage = mockStorage;

const TOKEN_KEY = 'csic_auth_token';
const USER_KEY = 'csic_user_profile';

// Pure logic under test replicating frontend/src/services/api.ts
const removeStoredToken = () => {
  mockStorage.removeItem(TOKEN_KEY);
  mockStorage.removeItem(USER_KEY);
};

const getStoredUser = () => {
  try {
    const token = mockStorage.getItem(TOKEN_KEY);
    const data = mockStorage.getItem(USER_KEY);
    if (!token || !data) {
      return null;
    }
    const parsed = JSON.parse(data);
    if (!parsed || typeof parsed !== 'object' || !parsed.id || !parsed.role) {
      removeStoredToken();
      return null;
    }
    return parsed;
  } catch (err) {
    removeStoredToken();
    return null;
  }
};

// 1. LocalStorage Malformed / Corrupted Data Resiliency
test('1. Malformed JSON in localStorage does not crash and safely purges', () => {
  mockStorage.setItem(TOKEN_KEY, 'some-token');
  mockStorage.setItem(USER_KEY, '{invalid json');
  const user = getStoredUser();
  assert.strictEqual(user, null, 'Expected null on malformed JSON');
  assert.strictEqual(mockStorage.getItem(USER_KEY), null, 'Expected corrupted USER_KEY to be purged');
  assert.strictEqual(mockStorage.getItem(TOKEN_KEY), null, 'Expected TOKEN_KEY to be purged');
});

test('2. "undefined" string in localStorage does not crash and safely purges', () => {
  mockStorage.setItem(TOKEN_KEY, 'some-token');
  mockStorage.setItem(USER_KEY, 'undefined');
  const user = getStoredUser();
  assert.strictEqual(user, null);
  assert.strictEqual(mockStorage.getItem(USER_KEY), null);
});

test('3. Incomplete user profile object without role or id is safely rejected and purged', () => {
  mockStorage.setItem(TOKEN_KEY, 'some-token');
  mockStorage.setItem(USER_KEY, JSON.stringify({ randomField: 123 }));
  const user = getStoredUser();
  assert.strictEqual(user, null);
  assert.strictEqual(mockStorage.getItem(USER_KEY), null);
});

test('4. Token without user profile returns null and preserves cleanliness', () => {
  mockStorage.clear();
  mockStorage.setItem(TOKEN_KEY, 'orphan-token');
  const user = getStoredUser();
  assert.strictEqual(user, null);
});

test('5. Valid user profile and token are correctly restored', () => {
  mockStorage.clear();
  mockStorage.setItem(TOKEN_KEY, 'valid-token-123');
  const validProfile = { id: 'stu-001', full_name: 'Rashi', email: 'rashi@csic.edu', role: 'student' };
  mockStorage.setItem(USER_KEY, JSON.stringify(validProfile));
  const user = getStoredUser();
  assert.ok(user, 'User profile should be restored');
  assert.strictEqual(user.id, 'stu-001');
  assert.strictEqual(user.role, 'student');
  assert.strictEqual(user.full_name, 'Rashi');
});

test('6. Logout explicitly clears all session keys', () => {
  removeStoredToken();
  assert.strictEqual(mockStorage.getItem(TOKEN_KEY), null);
  assert.strictEqual(mockStorage.getItem(USER_KEY), null);
});

// 2. Vercel Configuration & SPA Routing Verification
test('7. vercel.json exists and is valid JSON', () => {
  const vPath = path.resolve(__dirname, '../vercel.json');
  assert.ok(fs.existsSync(vPath), 'vercel.json must exist at repository root');
  const content = JSON.parse(fs.readFileSync(vPath, 'utf8'));
  assert.ok(content.services, 'vercel.json must have services');
  assert.ok(content.services.frontend, 'frontend service must be defined');
  assert.strictEqual(content.services.frontend.framework, 'vite', 'frontend service must have framework vite');
  assert.ok(content.services.backend, 'backend service must be defined');
  assert.ok(content.rewrites, 'rewrites array must be defined');
});

test('8. vercel.json preserves API and health routing to backend', () => {
  const content = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../vercel.json'), 'utf8'));
  const apiRewrite = content.rewrites.find(r => r.source === '/api/(.*)');
  const healthRewrite = content.rewrites.find(r => r.source === '/health/(.*)');
  assert.ok(apiRewrite, 'API rewrite must exist');
  assert.strictEqual(apiRewrite.destination.service, 'backend');
  assert.ok(healthRewrite, 'Health rewrite must exist');
  assert.strictEqual(healthRewrite.destination.service, 'backend');
});

test('9. vercel.json routes all client-side SPA routes to Vite frontend service', () => {
  const content = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../vercel.json'), 'utf8'));
  const catchAll = content.rewrites.find(r => r.source === '/(.*)');
  assert.ok(catchAll, 'Catch-all rewrite must exist');
  assert.strictEqual(catchAll.destination.service, 'frontend');
});

// 3. Frontend Production Build Artifacts Verification
test('11. Frontend dist contains index.html and code-split chunks', () => {
  const distDir = path.resolve(__dirname, '../frontend/dist');
  assert.ok(fs.existsSync(distDir), 'frontend/dist must exist');
  const indexHtml = path.join(distDir, 'index.html');
  assert.ok(fs.existsSync(indexHtml), 'index.html must exist in dist');
  
  const assetsDir = path.join(distDir, 'assets');
  assert.ok(fs.existsSync(assetsDir), 'assets dir must exist in dist');
  const files = fs.readdirSync(assetsDir);
  
  // Verify lazy loaded chunks exist
  const hasLogin = files.some(f => f.startsWith('Login-'));
  const hasDashboard = files.some(f => f.startsWith('StudentDashboardPage-'));
  const hasChat = files.some(f => f.startsWith('ChatPage-'));
  const hasFaculty = files.some(f => f.startsWith('FacultyDashboard-'));
  const hasAdmin = files.some(f => f.startsWith('AdminDashboard-'));
  const hasVendorReact = files.some(f => f.startsWith('vendor-react-'));
  
  assert.ok(hasLogin, 'Login chunk must exist');
  assert.ok(hasDashboard, 'StudentDashboardPage chunk must exist');
  assert.ok(hasChat, 'ChatPage chunk must exist');
  assert.ok(hasFaculty, 'FacultyDashboard chunk must exist');
  assert.ok(hasAdmin, 'AdminDashboard chunk must exist');
  assert.ok(hasVendorReact, 'vendor-react chunk must exist');
});

console.log('='.repeat(70));
console.log(`Results: ${passCount} Passed, ${failCount} Failed`);
console.log('='.repeat(70));

if (failCount > 0) {
  process.exit(1);
}
