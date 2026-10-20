import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { createServer } from 'node:net';
import { setTimeout as sleep } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';

const socket = createServer();
socket.listen(0, '127.0.0.1');
await once(socket, 'listening');
const port = socket.address().port;
await new Promise((resolve) => socket.close(resolve));

const child = spawn(process.execPath, [
  '--import', new URL('./mock_blueos.mjs', import.meta.url).href,
  fileURLToPath(new URL('../../software/visor/server.mjs', import.meta.url)),
], { env: { ...process.env, PORT: String(port) }, stdio: ['ignore', 'pipe', 'pipe'] });
let logs = '';
child.stdout.on('data', (chunk) => { logs += chunk; });
child.stderr.on('data', (chunk) => { logs += chunk; });
// Adjuntar inmediatamente para recoger también una salida de arranque temprana.
const exited = once(child, 'exit');
const base = `http://127.0.0.1:${port}`;
const eventsAbort = new AbortController();

async function statusWhenReady(source) {
  const deadline = Date.now() + 8000;
  while (Date.now() < deadline) {
    if (child.exitCode !== null || child.signalCode !== null) throw new Error(logs);
    try {
      const response = await fetch(`${base}/api/status`, { signal: AbortSignal.timeout(500) });
      const status = await response.json();
      if (status.online && status.sourceName === source) return status;
    } catch {
      // Arranque local todavía pendiente.
    }
    await sleep(50);
  }
  throw new Error(`El visor no quedó listo: ${logs}`);
}

try {
  const status = await statusWhenReady('wifi');
  assert.equal(status.heartbeat.armed, false);
  assert.equal(status.gps.satellites, 20);
  assert.ok(status.attitude.counter > 0);

  const page = await fetch(`${base}/`);
  assert.equal(page.status, 200);
  assert.match(await page.text(), /Navigator/);

  const changed = await fetch(`${base}/api/source`, {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ source: 'ethernet' }),
  });
  assert.equal(changed.status, 200);
  assert.equal((await statusWhenReady('ethernet')).targetHost, '192.168.2.2');

  const rejected = await fetch(`${base}/api/source`, {
    method: 'POST', body: JSON.stringify({ source: 'unrecognized' }),
  });
  assert.equal(rejected.status, 400);

  const events = await fetch(`${base}/events`, { signal: eventsAbort.signal });
  assert.match(events.headers.get('content-type'), /text\/event-stream/);
  const reader = events.body.getReader();
  const first = await reader.read();
  assert.match(new TextDecoder().decode(first.value), /^data: /);
  // Mantener SSE abierto para comprobar el cierre con un navegador conectado.
} finally {
  try {
    child.kill('SIGTERM');
    await Promise.race([exited, sleep(3000)]);
    if (child.exitCode === null && child.signalCode === null) {
      child.kill('SIGKILL');
      await exited;
      throw new Error('El visor de pruebas necesitó cierre forzado');
    }
    if (process.platform !== 'win32') assert.equal(child.exitCode, 0, logs);
  } finally {
    eventsAbort.abort();
  }
}
console.log('OK: visor trasladado, página/API/SSE, cambio de origen y cierre con SSE abierto');
