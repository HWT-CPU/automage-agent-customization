const DEFAULT_AUTOMAGE_BASE_URL = process.env.AUTOMAGE_OPENCLAW_BRIDGE_URL || 'http://127.0.0.1:8000';

export function normalizeOpenClawMessage(input) {
  const event = input || {};
  const message = event.message || event;
  const sender = message.from || event.from || {};
  return {
    channel: String(event.channel || process.env.AUTOMAGE_OPENCLAW_CHANNEL || process.env.OPENCLAW_CHANNEL || 'openclaw'),
    accountId: event.accountId || event.account_id || process.env.AUTOMAGE_OPENCLAW_ACCOUNT_ID || process.env.OPENCLAW_ACCOUNT_ID || null,
    message: {
      id: message.id || event.id || `openclaw-${Date.now()}`,
      text: String(message.text || event.text || ''),
      from: {
        id: String(sender.id || event.actorExternalId || event.actor_external_id || process.env.AUTOMAGE_OPENCLAW_ACTOR_ID || process.env.OPENCLAW_ACTOR_ID || 'staff-open-id'),
        name: sender.name || event.actorName || event.actor_name || null,
      },
      timestamp: message.timestamp || event.timestamp || Date.now(),
      attachments: Array.isArray(message.attachments) ? message.attachments : [],
    },
    payload: event.payload && typeof event.payload === 'object' ? event.payload : {},
  };
}

export async function forwardOpenClawEvent(input, options = {}) {
  const baseUrl = String(options.baseUrl || DEFAULT_AUTOMAGE_BASE_URL).replace(/\/$/, '');
  const timeoutMs = Number(options.timeoutMs || process.env.AUTOMAGE_OPENCLAW_TIMEOUT_MS || 30000);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${baseUrl}/openclaw/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(normalizeOpenClawMessage(input)),
      signal: controller.signal,
    });
    const text = await response.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = { raw: text };
    }
    if (!response.ok) {
      const message = data?.detail || data?.error || text || `AutoMage bridge returned HTTP ${response.status}`;
      throw new Error(String(message));
    }
    return data;
  } finally {
    clearTimeout(timer);
  }
}

export async function handleOpenClawMessage(input, options = {}) {
  const result = await forwardOpenClawEvent(input, options);
  return result.reply || { text: result.response?.reply_text || '', attachments: [], actions: [] };
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString('utf8').trim();
}

async function main() {
  const args = process.argv.slice(2);
  const baseUrlIndex = args.indexOf('--base-url');
  const baseUrl = baseUrlIndex >= 0 ? args[baseUrlIndex + 1] : DEFAULT_AUTOMAGE_BASE_URL;
  const textIndex = args.indexOf('--text');
  const actorIndex = args.indexOf('--actor');
  const channelIndex = args.indexOf('--channel');
  const jsonArgIndex = args.indexOf('--json');
  let input = null;
  if (jsonArgIndex >= 0 && args[jsonArgIndex + 1]) {
    input = JSON.parse(args[jsonArgIndex + 1]);
  } else if (textIndex >= 0) {
    input = {
      channel: channelIndex >= 0 ? args[channelIndex + 1] : 'openclaw',
      message: {
        text: args[textIndex + 1] || '',
        from: { id: actorIndex >= 0 ? args[actorIndex + 1] : 'staff-open-id' },
      },
    };
  } else {
    const stdin = await readStdin();
    input = stdin ? JSON.parse(stdin) : { message: { text: '查知识库 OpenAPI 契约', from: { id: 'staff-open-id' } } };
  }
  const result = await forwardOpenClawEvent(input, { baseUrl });
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    process.stderr.write(`${error.stack || error.message}\n`);
    process.exit(1);
  });
}
