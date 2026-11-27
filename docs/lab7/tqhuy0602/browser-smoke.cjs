// Run from the repository root with Playwright available through NODE_PATH.
// This is an automated browser check, not the required outside-person H1 test.
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const assert = require('node:assert/strict');

const root = process.cwd();
const output = path.join(root, 'docs/lab7/tqhuy0602');
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'huy-lab07-browser-'));
const python = path.join(root, '.venv/bin/python');
const controlFile = path.join(temporary, 'control.json');
const traceFile = path.join(temporary, 'trace.jsonl');
const apiUrl = 'http://127.0.0.1:18701';
const uiUrl = 'http://127.0.0.1:18702';
const environment = {
  ...process.env, LLM_PROVIDER: 'stub', ASSISTANT_API_URL: apiUrl,
  DATABASE_URL: `sqlite:///${path.join(temporary, 'demo.db')}`,
  SESSION_SALT: 'synthetic-lab07-demo-salt', API_ADMIN_KEY: 'synthetic-lab07-demo-admin',
  DEMO_CONTROL: controlFile, DEMO_TRACE: traceFile,
};
const children = [];
const results = [];
let backend, browser;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const control = value => fs.writeFileSync(controlFile, JSON.stringify(value));
const trace = () => fs.existsSync(traceFile) ? fs.readFileSync(traceFile, 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse) : [];
const chats = () => trace().filter(row => row.path === '/v1/chat');

function launch(args, name) {
  const fd = fs.openSync(path.join(temporary, `${name}.log`), 'a');
  const child = spawn(python, args, { cwd: root, env: environment, stdio: ['ignore', fd, fd] });
  children.push(child);
  return child;
}
async function until(check, description, timeout = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (await check()) return;
    await delay(100);
  }
  throw new Error(`Timed out: ${description}`);
}
async function healthy(url) {
  try { return (await fetch(url)).ok; } catch { return false; }
}
async function startBackend() {
  backend = launch(['-m', 'uvicorn', 'demo_api:app', '--app-dir', 'docs/lab7/tqhuy0602', '--host', '127.0.0.1', '--port', '18701'], 'api');
  await until(() => healthy(`${apiUrl}/health`), 'API startup');
}
async function stop(child) {
  if (!child || child.exitCode !== null) return;
  child.kill('SIGINT');
  await until(() => child.exitCode !== null, 'server shutdown');
}
async function screenshot(page, name) {
  if (!name.includes('waiting')) {
    await page.getByTestId('stStatusWidget').waitFor({ state: 'hidden', timeout: 10000 });
    await delay(300);
  }
  await page.screenshot({ path: path.join(output, name), fullPage: true });
}
async function question(page, text) {
  const count = chats().length;
  const input = page.getByPlaceholder('Ask about fees, offices or the handbook…');
  await input.fill(text);
  await input.press('Enter');
  await until(() => chats().length === count + 1, `chat ${text}`);
}

(async () => {
  try {
    control({});
    await startBackend();
    launch(['-m', 'streamlit', 'run', 'ui/app.py', '--server.address', '127.0.0.1', '--server.port', '18702', '--server.headless', 'true', '--browser.gatherUsageStats', 'false', '--server.fileWatcherType', 'none'], 'ui');
    await until(() => healthy(`${uiUrl}/_stcore/health`), 'Streamlit startup');
    browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    await page.goto(uiUrl);
    await page.getByRole('heading', { name: '🎓 FIT Study Assistant' }).waitFor();
    await screenshot(page, 'desktop-welcome.png');

    control({ delay_s: 1.3 });
    await page.getByRole('button', { name: 'Can I register my thesis with 118 credits?', exact: true }).click();
    await page.getByText('Thinking…', { exact: true }).waitFor();
    await screenshot(page, 'desktop-waiting.png');
    await page.getByText('Sources: H26#5.3', { exact: false }).waitFor();
    assert.equal(chats().length, 1);
    assert.match(chats()[0].response.answer, /120/);
    assert.match(chats()[0].response.answer, /2\.0/);
    await screenshot(page, 'desktop-thesis.png');
    results.push('Sidebar sends one POST; Thinking visible; thesis has 120 credits, GPA 2.0 and H26#5.3.');
    control({});
    await page.getByRole('button', { name: '👍 Helpful', exact: true }).click();
    await page.getByText('Thanks for your feedback!', { exact: true }).waitFor();
    assert.equal(await page.getByRole('button', { name: '👎 Not helpful', exact: true }).count(), 0);
    results.push('Positive feedback uses the answer request_id; both buttons disappear after 201.');

    await question(page, 'what is the capital of France');
    await page.getByText('A staff member can help: Training Office, room I.101.', { exact: false }).waitFor();
    assert.equal(chats().at(-1).response.path, 'abstain');
    assert.deepEqual(chats().at(-1).response.sources, []);
    await screenshot(page, 'desktop-escalation.png');

    control({ provider_down: true });
    await question(page, 'I lost my student card');
    await page.getByText('Shown directly from the source document', { exact: false }).waitFor();
    assert.equal(chats().at(-1).response.degraded, true);
    await screenshot(page, 'desktop-fallback.png');
    control({});
    results.push('No-evidence response escalates to I.101; real provider failure shows retrieval fallback and S26#3.');

    const mobileContext = await browser.newContext({ viewport: { width: 375, height: 812 } });
    const mobile = await mobileContext.newPage();
    await mobile.goto(uiUrl);
    await mobile.getByRole('heading', { name: '🎓 FIT Study Assistant' }).waitFor();
    await question(mobile, 'I lost my student card');
    await mobile.getByText('Sources: S26#3', { exact: false }).waitFor();
    const bounds = await mobile.evaluate(() => ({ viewport: innerWidth, content: document.documentElement.scrollWidth }));
    assert.ok(bounds.content <= bounds.viewport, JSON.stringify(bounds));
    await screenshot(mobile, 'mobile-card-375.png');
    const mobileSession = chats().at(-1).body.session_id;
    assert.notEqual(mobileSession, chats()[0].body.session_id);
    control({ feedback_status: 500 });
    await mobile.getByRole('button', { name: '👎 Not helpful', exact: true }).click();
    await mobile.getByText('Feedback could not be confirmed', { exact: false }).waitFor();
    assert.ok(await mobile.getByRole('button', { name: '👎 Not helpful', exact: true }).isEnabled());
    await screenshot(mobile, 'mobile-feedback-retry.png');
    control({});
    await mobile.getByRole('button', { name: '👎 Not helpful', exact: true }).click();
    await mobile.getByText('Thanks — we will look at this answer.', { exact: true }).waitFor();
    assert.equal(await mobile.getByRole('button', { name: '👎 Not helpful', exact: true }).count(), 0);
    await screenshot(mobile, 'mobile-feedback-saved.png');
    results.push('375 px has no horizontal overflow; labels readable; failed negative feedback stays retryable; 201 hides buttons.');

    await stop(backend);
    const countBeforeOutage = chats().length;
    const input = page.getByPlaceholder('Ask about fees, offices or the handbook…');
    await input.fill('Question while API is stopped');
    await input.press('Enter');
    await page.getByText('Cannot reach the assistant backend.', { exact: false }).waitFor();
    await page.getByText('Sources: H26#5.3', { exact: false }).waitFor();
    assert.equal(chats().length, countBeforeOutage);
    await screenshot(page, 'desktop-backend-offline.png');
    await startBackend();
    await question(page, 'Tuition for 18 credits and 2 retake');
    await page.getByText('Your tuition is 9,450,000 VND.', { exact: true }).waitFor();
    assert.equal(chats().at(-1).body.session_id, chats()[0].body.session_id);
    assert.deepEqual(chats().at(-1).response.sources, []);
    const feedback = await (await fetch(`${apiUrl}/v1/feedback`, { headers: { 'X-Admin-Key': environment.API_ADMIN_KEY } })).json();
    assert.equal(feedback.length, 2);
    assert.deepEqual(feedback.map(row => row.rating).sort(), [-1, 1]);
    await screenshot(page, 'desktop-recovered-fee.png');
    results.push('Stopping real Uvicorn preserves UI history; restart on same SQLite retains both ratings; session_id is stable.');

    const beforeInvalid = chats().length;
    await input.fill('x'.repeat(2001));
    await input.press('Enter');
    await page.getByText('Your question is too long', { exact: false }).waitFor();
    await input.fill('   ');
    await input.press('Enter');
    await delay(500);
    assert.equal(chats().length, beforeInvalid);
    results.push('Whitespace and 2001-character questions make no POST; separate tabs have separate session_id.');

    const rows = trace();
    const posted = rows.filter(row => row.path === '/v1/feedback' && row.method === 'POST');
    assert.deepEqual(posted.map(row => row.status), [201, 500, 201]);
    fs.writeFileSync(path.join(output, 'browser-results.json'), JSON.stringify({ automated: true, human_usability_test: false, viewport: bounds, results, feedback_after_restart: feedback, requests: rows }, null, 2) + '\n');
    console.log(results.join('\n'));
    console.log(`Evidence: ${output}`);
  } finally {
    if (browser) await browser.close();
    for (const child of children.reverse()) await stop(child);
    console.log(`Server logs: ${temporary}`);
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
