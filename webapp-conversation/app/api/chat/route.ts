import { NextRequest } from 'next/server';
import { client, getInfo } from '@/app/api/utils/common';

export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
    const payload = await req.json();
    const { messages, conversation_id, inputs } = payload;
    const files = payload.data?.files || payload.files || [];

    // Extract text from latest user message
    const latestMessage = messages?.at(-1);
    const query: string =
        typeof latestMessage?.content === 'string'
            ? latestMessage.content
            : (latestMessage?.parts?.find((p: any) => p.type === 'text')?.text ?? '');

    const { user } = getInfo(req);

    const encoder = new TextEncoder();

    const stream = new ReadableStream({
        async start(controller) {
            const writeSSE = (data: object) => {
                const line = `data: ${JSON.stringify(data)}\n\n`;
                controller.enqueue(encoder.encode(line));
            };

            try {
                const res = await client.createChatMessage(
                    inputs || {},
                    query,
                    user,
                    'streaming',
                    conversation_id,
                    files || []
                );

                const textId = `text-${Date.now()}`;

                // Send start markers in SSE format
                writeSSE({ type: 'start' });
                writeSSE({ type: 'start-step' });
                writeSSE({ type: 'text-start', id: textId });

                const axiosStream = res.data as any;
                const decoder = new TextDecoder('utf-8');
                let buffer = '';

                for await (const chunk of axiosStream) {
                    buffer += decoder.decode(chunk, { stream: true });
                    const lines = buffer.split('\n');

                    for (let i = 0; i < lines.length - 1; i++) {
                        const line = lines[i].trim();
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                if ((data.event === 'message' || data.event === 'agent_message') && data.answer) {
                                    writeSSE({ type: 'text-delta', id: textId, delta: data.answer });
                                }
                            } catch {
                                // ignore partial line parse errors
                            }
                        }
                    }
                    buffer = lines[lines.length - 1];
                }

                // Send end markers
                writeSSE({ type: 'text-end', id: textId });
                writeSSE({ type: 'finish-step' });
                writeSSE({ type: 'finish', finishReason: 'stop' });
                controller.close();

            } catch (err: any) {
                console.error('[/api/chat] SSE stream error:', err?.message ?? err);
                writeSSE({ type: 'error', errorText: String(err?.message ?? 'Unknown error') });
                controller.close();
            }
        }
    });

    return new Response(stream, {
        headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache, no-transform',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        },
    });
}
