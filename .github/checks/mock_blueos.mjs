// Preload exclusivo de pruebas. Sustituye fetch antes de cargar el visor.
// Ninguna consulta del visor sale hacia BlueOS durante esta comprobación.
let counter = 0;

globalThis.fetch = async (input) => {
  const url = new URL(String(input));
  if (!['192.168.42.1', '192.168.2.2'].includes(url.hostname)
      || url.pathname !== '/mavlink2rest/v1/mavlink/vehicles/1/components/1/messages') {
    throw new Error('Consulta inesperada en el visor simulado');
  }
  counter += 1;
  const status = { time: { counter, frequency: 10, last_update: new Date().toISOString() } };
  const entry = (message) => ({ message, status });
  return new Response(JSON.stringify({
    ATTITUDE: entry({ roll: 0.01, pitch: -0.02, yaw: 1, rollspeed: 0, pitchspeed: 0, yawspeed: 0 }),
    GPS_RAW_INT: entry({ fix_type: { type: 'GPS_FIX_TYPE_DGPS' }, satellites_visible: 20, lat: 430000000, lon: -80000000 }),
    HEARTBEAT: entry({ base_mode: { bits: 65 }, custom_mode: 0 }),
    RAW_IMU: entry({ xacc: 0, yacc: 0, zacc: 1000, xgyro: 0, ygyro: 0, zgyro: 0, temperature: 2500 }),
  }), { headers: { 'content-type': 'application/json' } });
};
