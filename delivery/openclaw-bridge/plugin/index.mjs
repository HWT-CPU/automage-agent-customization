import { handleOpenClawMessage, forwardOpenClawEvent, normalizeOpenClawMessage } from '../automage_openclaw_forwarder.mjs';

export const name = 'automage-openclaw-bridge';
export const displayName = 'AutoMage OpenClaw Bridge';
export const description = 'Forward OpenClaw channel messages to AutoMage HTTP bridge.';

export async function onMessage(event, context = {}) {
  const baseUrl = context.baseUrl || process.env.AUTOMAGE_OPENCLAW_BRIDGE_URL || 'http://127.0.0.1:8000';
  return await handleOpenClawMessage(event, { baseUrl });
}

export async function handleMessage(event, context = {}) {
  return await onMessage(event, context);
}

export async function run(input, context = {}) {
  return await onMessage(input, context);
}

export async function invoke(input, context = {}) {
  return await onMessage(input, context);
}

export function register(api = {}) {
  if (typeof api.onMessage === 'function') {
    api.onMessage(async (event, context = {}) => await onMessage(event, context));
  }
  if (typeof api.registerHandler === 'function') {
    api.registerHandler('message', async (event, context = {}) => await onMessage(event, context));
  }
  if (typeof api.registerTool === 'function') {
    api.registerTool({
      name: 'automage_openclaw_event',
      label: 'AutoMage OpenClaw Event',
      description: 'Forward a user message to AutoMage /openclaw/events and return the AutoMage skill reply.',
      parameters: {
        type: 'object',
        additionalProperties: false,
        properties: {
          text: {
            type: 'string',
            description: 'User message to forward to AutoMage.',
          },
          actorExternalId: {
            type: 'string',
            description: 'External actor id. Defaults to staff-open-id.',
          },
          channel: {
            type: 'string',
            description: 'Source channel. Defaults to openclaw.',
          },
          payload: {
            type: 'object',
            description: 'Structured channel metadata to forward to AutoMage.',
            additionalProperties: true,
          },
        },
        required: ['text'],
      },
      execute: async (_toolCallId, rawParams = {}) => {
        const response = await onMessage({
          channel: rawParams.channel || 'openclaw',
          message: {
            id: `openclaw-tool-${Date.now()}`,
            text: rawParams.text,
            from: {
              id: rawParams.actorExternalId || 'staff-open-id',
              name: 'OpenClaw Agent',
            },
            attachments: [],
          },
          payload: rawParams.payload && typeof rawParams.payload === 'object' ? rawParams.payload : {},
        }, api);
        return {
          content: [
            {
              type: 'text',
              text: response.text || JSON.stringify(response),
            },
          ],
        };
      },
    });
  }
  return {
    name,
    displayName,
    description,
    onMessage,
    handleMessage,
    run,
    invoke,
  };
}

export async function activate(api = {}) {
  return register(api);
}

export default {
  name,
  displayName,
  description,
  register,
  activate,
  onMessage,
  handleMessage,
  run,
  invoke,
  forwardOpenClawEvent,
  normalizeOpenClawMessage,
};
