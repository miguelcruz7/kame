import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PAGE = await readFile(path.join(HERE, 'public', 'index.html'));
const PORT = Number(process.env.PORT || 8765);
const SOURCES = Object.freeze({
  wifi: '192.168.42.1',
  ethernet: '192.168.2.2',
});

let sourceName = 'wifi';
let targetHost = SOURCES[sourceName];
let lastAttitudeCounter = null;
let lastAttitudeChange = 0;
let consecutiveErrors = 0;
let previousOnline = false;
let state = {
  online: false,
  sourceName,
  targetHost,
  error: 'Conectando a BlueOS…',
  receivedAt: Date.now(),
};
const clients = new Set();

function message(messages, name) {
  const entry = messages?.[name];
  return entry ? { message: entry.message, status: entry.status } : null;
}

function numeric(value, scale = 1) {
  const number = Number(value);
  return Number.isFinite(number) ? number * scale : null;
}

function publish() {
  const data = `data: ${JSON.stringify(state)}\n\n`;
  for (const client of clients) {
    try {
      client.write(data);
    } catch {
      clients.delete(client);
    }
  }
}

function setOnline(next) {
  if (next !== previousOnline) {
    previousOnline = next;
    console.log(`[BlueOS] ${next ? 'telemetría recibida' : 'sin telemetría'} (${targetHost})`);
  }
}

async function pollBlueOS() {
  const url = `http://${targetHost}/mavlink2rest/v1/mavlink/vehicles/1/components/1/messages`;
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(1200) });
    if (!response.ok) throw new Error(`BlueOS respondió HTTP ${response.status}`);
    const messages = await response.json();
    const attitudeEntry = message(messages, 'ATTITUDE');
    if (!attitudeEntry?.message) throw new Error('No aparece ATTITUDE del autopiloto');

    const counter = Number(attitudeEntry.status?.time?.counter);
    if (Number.isFinite(counter) && counter !== lastAttitudeCounter) {
      lastAttitudeCounter = counter;
      lastAttitudeChange = Date.now();
    }
    const freshMs = lastAttitudeChange ? Date.now() - lastAttitudeChange : Infinity;
    const online = freshMs < 1500;
    const attitude = attitudeEntry.message;
    const raw = message(messages, 'RAW_IMU')?.message;
    const vibration = message(messages, 'VIBRATION')?.message;
    const ekf = message(messages, 'EKF_STATUS_REPORT')?.message;
    const gps = message(messages, 'GPS_RAW_INT')?.message;
    const heartbeat = message(messages, 'HEARTBEAT')?.message;

    consecutiveErrors = 0;
    setOnline(online);
    state = {
      online,
      sourceName,
      targetHost,
      error: online ? null : 'ATTITUDE no se actualiza',
      receivedAt: Date.now(),
      attitude: {
        roll: numeric(attitude.roll),
        pitch: numeric(attitude.pitch),
        yaw: numeric(attitude.yaw),
        rollspeed: numeric(attitude.rollspeed),
        pitchspeed: numeric(attitude.pitchspeed),
        yawspeed: numeric(attitude.yawspeed),
        frequency: numeric(attitudeEntry.status?.time?.frequency),
        counter: Number.isFinite(counter) ? counter : null,
        freshMs,
      },
      rawImu: raw ? {
        accel: [numeric(raw.xacc, 0.001), numeric(raw.yacc, 0.001), numeric(raw.zacc, 0.001)],
        gyro: [numeric(raw.xgyro, 180 / (Math.PI * 1000)), numeric(raw.ygyro, 180 / (Math.PI * 1000)), numeric(raw.zgyro, 180 / (Math.PI * 1000))],
        temperatureC: numeric(raw.temperature, 0.01),
        updatedAt: message(messages, 'RAW_IMU')?.status?.time?.last_update ?? null,
      } : null,
      vibration: vibration ? {
        xyz: [numeric(vibration.vibration_x), numeric(vibration.vibration_y), numeric(vibration.vibration_z)],
        clips: [Number(vibration.clipping_0 || 0), Number(vibration.clipping_1 || 0), Number(vibration.clipping_2 || 0)],
      } : null,
      ekf: ekf ? {
        flags: Number(ekf.flags?.bits || 0),
        compassVariance: numeric(ekf.compass_variance),
        velocityVariance: numeric(ekf.velocity_variance),
      } : null,
      gps: gps ? {
        fix: gps.fix_type?.type ?? null,
        satellites: Number(gps.satellites_visible || 0),
        latitude: numeric(gps.lat, 1e-7),
        longitude: numeric(gps.lon, 1e-7),
      } : null,
      heartbeat: heartbeat ? {
        armed: Boolean(Number(heartbeat.base_mode?.bits || 0) & 128),
        mode: Number(heartbeat.custom_mode || 0),
      } : null,
    };
    publish();
  } catch (error) {
    consecutiveErrors += 1;
    const freshMs = lastAttitudeChange ? Date.now() - lastAttitudeChange : Infinity;
    const online = freshMs < 1500;
    setOnline(online);
    state = {
      ...state,
      online,
      sourceName,
      targetHost,
      error: online ? null : (consecutiveErrors >= 2 ? 'BlueOS no responde; reintentando' : 'Esperando datos de BlueOS…'),
      receivedAt: Date.now(),
    };
    publish();
  }
}

function sendJson(response, statusCode, value) {
  response.writeHead(statusCode, {
    'content-type': 'application/json; charset=utf-8',
    'cache-control': 'no-store',
    'x-content-type-options': 'nosniff',
  });
  response.end(JSON.stringify(value));
}

const server = createServer(async (request, response) => {
  const url = new URL(request.url || '/', `http://${request.headers.host || '127.0.0.1'}`);

  if (request.method === 'GET' && url.pathname === '/') {
    response.writeHead(200, {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store',
      'x-content-type-options': 'nosniff',
      'referrer-policy': 'no-referrer',
      'content-security-policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
    });
    response.end(PAGE);
    return;
  }

  if (request.method === 'GET' && url.pathname === '/api/status') {
    sendJson(response, 200, state);
    return;
  }

  if (request.method === 'GET' && url.pathname === '/events') {
    response.writeHead(200, {
      'content-type': 'text/event-stream; charset=utf-8',
      'cache-control': 'no-cache, no-transform',
      connection: 'keep-alive',
      'x-accel-buffering': 'no',
    });
    response.write(`data: ${JSON.stringify(state)}\n\n`);
    clients.add(response);
    request.on('close', () => clients.delete(response));
    return;
  }

  if (request.method === 'POST' && url.pathname === '/api/source') {
    let body = '';
    for await (const chunk of request) {
      body += chunk;
      if (body.length > 1024) {
        sendJson(response, 413, { error: 'Solicitud demasiado grande' });
        return;
      }
    }
    let selected;
    try {
      selected = JSON.parse(body).source;
    } catch {
      sendJson(response, 400, { error: 'JSON no válido' });
      return;
    }
    if (!Object.hasOwn(SOURCES, selected)) {
      sendJson(response, 400, { error: 'Origen no permitido' });
      return;
    }
    sourceName = selected;
    targetHost = SOURCES[selected];
    lastAttitudeCounter = null;
    lastAttitudeChange = 0;
    consecutiveErrors = 0;
    state = { online: false, sourceName, targetHost, error: 'Cambiando de enlace…', receivedAt: Date.now() };
    publish();
    sendJson(response, 200, { sourceName, targetHost });
    return;
  }

  sendJson(response, 404, { error: 'No encontrado' });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`Navigator IMU Viewer: http://127.0.0.1:${PORT}`);
  console.log('Solo lectura · servidor local · no envía comandos MAVLink');
});

let polling = false;
async function tick() {
  if (polling) return;
  polling = true;
  await pollBlueOS();
  polling = false;
  const delay = state.online ? 100 : 800;
  setTimeout(tick, delay);
}
tick();

process.on('SIGINT', () => server.close(() => process.exit(0)));
process.on('SIGTERM', () => server.close(() => process.exit(0)));
