import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs'; // Use nodejs runtime for Buffer support

export async function POST(req: NextRequest) {
    try {
        const formData = await req.formData();
        const audioFile = formData.get('audio') as File;
        if (!audioFile) {
            return NextResponse.json({ error: 'No audio file provided' }, { status: 400 });
        }

        const arrayBuffer = await audioFile.arrayBuffer();
        const base64Audio = Buffer.from(arrayBuffer).toString('base64');

        // Volcengine credentials from ENV or hardcoded as provided by user
        const appid = process.env.VOLCENGINE_APP_ID || '8397914318';
        const token = process.env.VOLCENGINE_TOKEN || 'kdoZ2QWRn64eWpUcSeA4nyNYe39nR2or';

        // We try to use the resource ID format from docs. Alternatively, cluster ID: Speech_Recognition_Seed_AUC2000000604516201474
        // Using standard volc.bigasr.auc_turbo as recommended by documentation for Extreme Speed version.
        const resourceId = process.env.VOLCENGINE_RESOURCE_ID || 'volc.bigasr.auc_turbo';

        const requestId = crypto.randomUUID();

        const payload = {
            user: {
                uid: appid
            },
            audio: {
                data: base64Audio
            },
            request: {
                model_name: 'bigmodel'
            }
        };

        const response = await fetch('https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash', {
            method: 'POST',
            headers: {
                'X-Api-App-Key': appid,
                'X-Api-Access-Key': token,
                'X-Api-Resource-Id': resourceId,
                'X-Api-Request-Id': requestId,
                'X-Api-Sequence': '-1',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errText = await response.text();
            console.error('Volcengine API Error:', errText);
            return NextResponse.json({ error: 'Speech recognition failed', details: errText }, { status: response.status });
        }

        const result = await response.json();
        return NextResponse.json(result);

    } catch (err: any) {
        console.error('[/api/voice] POST Error:', err);
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
