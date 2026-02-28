import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
    try {
        const { query } = await req.json();
        const deepSeekKey = process.env.DEEPSEEK_API_KEY || 'sk-410f0787464c45c28d6283c20b097bc1';

        const response = await fetch('https://api.deepseek.com/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${deepSeekKey}`
            },
            body: JSON.stringify({
                model: 'deepseek-chat',
                messages: [
                    { role: 'system', content: '你是一个对话标题生成器。请根据用户的输入，生成一个简短的总结标题（最好在10个字以内，使用中文）。直接返回标题内容，不要带引号、标点或前缀说明。' },
                    { role: 'user', content: query || '你好' }
                ],
                temperature: 0.3
            })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch from DeepSeek API');
        }

        const data = await response.json();
        const title = data.choices[0].message.content.trim().replace(/^["']|["']$/g, '');

        return NextResponse.json({ title });
    } catch (error: any) {
        console.error('DeepSeek Title Error:', error);
        return NextResponse.json({ title: '新对话' }, { status: 500 });
    }
}
