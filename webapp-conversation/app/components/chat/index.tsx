'use client'

import React, { useRef, useEffect, useState, useCallback } from 'react'
import { useChat } from '@ai-sdk/react'
import { Button, Avatar, Tooltip } from '@heroui/react'
import {
  ArrowUp, Bot, Loader2, Lightbulb, Mic, MicOff, Paperclip, X,
  ChevronDown, ChevronUp, Copy, RefreshCw, Pencil, StopCircle, Check,
  Share, Square
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { VisionSettings } from '@/types/app'

export interface IChatProps {
  chatList?: any[]
  currConversationId?: string
  currInputs?: Record<string, any>
  onFeedback?: (messageId: string, feedback: any) => Promise<void>
  visionConfig?: VisionSettings
  fileConfig?: any
  children?: React.ReactNode
}

/* ─── Think Block with micro-preview animation ─── */
const ThinkBlock = ({ content, isStreaming }: { content: string; isStreaming?: boolean }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const previewText = content.slice(0, 60).replace(/\n/g, ' ')

  return (
    <div className="bg-default-100 dark:bg-default-50 text-default-600 rounded-lg p-3 text-sm border-l-3 border-default-300">
      <div
        className="flex items-center gap-2 font-medium opacity-70 text-xs cursor-pointer select-none"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Lightbulb size={14} className={isStreaming ? 'animate-pulse text-warning' : ''} />
        <span>深度思考</span>
        {isStreaming && <span className="text-warning animate-pulse">思考中...</span>}
        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </div>
      {/* micro-preview: always show a faded one-liner when collapsed */}
      {!isExpanded && previewText && (
        <div className={`mt-1 text-xs opacity-50 truncate max-w-full ${isStreaming ? 'animate-pulse' : ''}`}>
          {previewText}{content.length > 60 ? '...' : ''}
        </div>
      )}
      {isExpanded && (
        <div className="whitespace-pre-wrap opacity-80 leading-relaxed font-normal mt-2">{content}</div>
      )}
    </div>
  )
}

/* ─── Typing dots animation ─── */
const TypingDots = () => (
  <div className="flex items-center gap-1 py-2">
    <span className="w-2 h-2 bg-default-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
    <span className="w-2 h-2 bg-default-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
    <span className="w-2 h-2 bg-default-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
  </div>
)

export default function Chat({
  chatList: initialChatList = [],
  currConversationId = '-1',
  currInputs = {},
  onFeedback,
  children,
}: IChatProps) {
  const [inputValue, setInputValue] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [micPermission, setMicPermission] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [wasStopped, setWasStopped] = useState(false)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<BlobPart[]>([])

  const authorizeVoice = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('当前环境不支持语音输入（可能需要HTTPS安全上下文或浏览器不支持）。')
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      setMicPermission(true)
      stream.getTracks().forEach(track => track.stop())
    } catch (err) {
      console.error('Mic permission denied', err)
      alert('无法获取麦克风权限，请在浏览器设置中允许。')
    }
  }

  const startRecording = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('当前环境不支持语音输入（可能需要HTTPS安全上下文或浏览器不支持）。')
      return
    }
    if (!micPermission) {
      alert('请先点击"预授权语音"按钮获取麦克风权限。')
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mediaRecorder.mimeType || 'audio/webm' })
        const formData = new FormData()
        formData.append('audio', audioBlob, 'audio.webm')

        try {
          const res = await fetch('/api/voice', {
            method: 'POST',
            body: formData,
          })
          const data = await res.json()
          if (data.result && data.result.text) {
            setInputValue(prev => prev + data.result.text)
          } else {
            console.error('Voice recognition failed or no text:', data)
          }
        } catch (e) {
          console.error('Voice upload error:', e)
        }

        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (err) {
      console.error('Start recording error:', err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const initialMessages = initialChatList
    .filter(msg => !msg.isOpeningStatement)
    .map(msg => ({
      id: msg.id,
      role: (msg.isAnswer ? 'assistant' : 'user') as 'assistant' | 'user',
      content: msg.content || '',
      parts: [{ type: 'text' as const, text: msg.content || '' }],
    }))

  const { messages, sendMessage, status, stop, reload } = useChat({
    initialMessages: initialMessages as any,
    body: {
      conversation_id: currConversationId === '-1' ? null : currConversationId,
      inputs: currInputs,
    },
    api: '/api/chat',
  })

  const isLoading = status === 'streaming' || status === 'submitted'
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const [attachments, setAttachments] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = inputValue.trim()
    if (!trimmed && attachments.length === 0) return
    setInputValue('')
    setWasStopped(false)

    const fileListToUpload = [...attachments]
    setAttachments([])

    let filesToSend: any[] = []
    if (fileListToUpload.length > 0) {
      filesToSend = await Promise.all(
        fileListToUpload.map(file => new Promise((resolve, reject) => {
          const reader = new FileReader()
          reader.onload = () => resolve({ type: 'image', transfer_method: 'remote_url', url: reader.result })
          reader.onerror = reject
          reader.readAsDataURL(file)
        }))
      )
    }

    try {
      await sendMessage({ role: 'user', content: trimmed || '发送图片' } as any, {
        data: { files: filesToSend } as any
      } as any)
    } catch (err) {
      console.error(err)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setAttachments(prev => [...prev, ...Array.from(e.target.files!)])
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as unknown as React.FormEvent)
    }
  }

  const getMessageText = (msg: any): string => {
    if (msg.content && typeof msg.content === 'string') return msg.content
    if (Array.isArray(msg.parts)) {
      return msg.parts
        .filter((p: any) => p.type === 'text')
        .map((p: any) => p.text)
        .join('')
    }
    return ''
  }

  const copyToClipboard = useCallback(async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch {
      console.error('Copy failed')
    }
  }, [])

  const handleRewrite = useCallback((text: string) => {
    setInputValue(text)
  }, [])

  const handleContinue = useCallback(async () => {
    try {
      await sendMessage({ role: 'user', content: '继续' } as any)
    } catch (err) {
      console.error(err)
    }
  }, [sendMessage])

  const handleRegenerate = useCallback(async () => {
    try {
      await reload()
    } catch (err) {
      console.error(err)
    }
  }, [reload])

  const renderMessageContent = (text: string, isUser: boolean, isStreamingMsg?: boolean) => {
    const thinkRegex = /<think>([\s\S]*?)(?:<\/think>|$)/g
    const parts: { type: string; content: string }[] = []
    let lastIndex = 0
    let match

    while ((match = thinkRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        const textPart = text.slice(lastIndex, match.index).trim()
        if (textPart) parts.push({ type: 'text', content: textPart })
      }
      const hasClosingTag = text.slice(match.index).includes('</think>')
      parts.push({ type: 'think', content: match[1].trim(), isStreaming: !hasClosingTag && !!isStreamingMsg } as any)
      lastIndex = thinkRegex.lastIndex
    }

    if (lastIndex < text.length) {
      const textPart = text.slice(lastIndex).trim()
      if (textPart) parts.push({ type: 'text', content: textPart })
    }

    if (parts.length === 0) {
      parts.push({ type: 'text', content: text.trim() })
    }

    return (
      <div className="space-y-3">
        {parts.map((p: any, i) => (
          p.type === 'think' ? (
            <ThinkBlock key={i} content={p.content} isStreaming={p.isStreaming} />
          ) : (
            <ReactMarkdown
              key={i}
              remarkPlugins={[remarkGfm]}
              className="prose dark:prose-invert max-w-none break-words"
            >
              {p.content}
            </ReactMarkdown>
          )
        ))}
      </div>
    )
  }

  const renderUserActions = (text: string, id: string) => (
    <div className="flex items-center gap-1 mt-1 justify-end opacity-0 group-hover:opacity-100 transition-opacity">
      <Tooltip content="复制">
        <button
          className="p-1.5 rounded-lg hover:bg-default-100 text-default-400 hover:text-default-600 transition"
          onClick={() => copyToClipboard(text, id)}
        >
          {copiedId === id ? <Check size={14} /> : <Copy size={14} />}
        </button>
      </Tooltip>
      <Tooltip content="编辑">
        <button
          className="p-1.5 rounded-lg hover:bg-default-100 text-default-400 hover:text-default-600 transition"
          onClick={() => handleRewrite(text)}
        >
          <Pencil size={14} />
        </button>
      </Tooltip>
    </div>
  )

  const renderAssistantActions = (text: string, id: string, isLast: boolean) => (
    <div className="flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
      <Tooltip content="复制">
        <button
          className="p-1.5 rounded-lg hover:bg-default-100 text-default-400 hover:text-default-600 transition"
          onClick={() => copyToClipboard(text, id)}
        >
          {copiedId === id ? <Check size={14} /> : <Copy size={14} />}
        </button>
      </Tooltip>
      <Tooltip content="重新生成">
        <button
          className="p-1.5 rounded-lg hover:bg-default-100 text-default-400 hover:text-default-600 transition"
          onClick={handleRegenerate}
        >
          <RefreshCw size={14} />
        </button>
      </Tooltip>
      {isLast && wasStopped && (
        <Tooltip content="继续生成">
          <button
            className="p-1.5 rounded-lg hover:bg-default-100 text-default-400 hover:text-default-600 transition"
            onClick={() => { setWasStopped(false); handleContinue() }}
          >
            <Share size={14} />
          </button>
        </Tooltip>
      )}
    </div>
  )

  // Check if last assistant message is currently streaming
  const lastMsg = messages[messages.length - 1]
  const isStreamingLastAssistant = isLoading && lastMsg?.role === 'assistant'

  return (
    <div className="flex flex-col h-full w-full relative overflow-hidden">
      {/* Messages - scrollable area */}
      <div
        className="flex-1 overflow-y-auto px-4 pt-4"
        style={{ WebkitOverflowScrolling: 'touch' }}
      >
        {children}
        <div className="space-y-6 max-w-full pb-8">
          {messages.map((m, idx) => {
            const text = getMessageText(m)
            const isLast = idx === messages.length - 1
            const isStreamingThis = isLast && isLoading && m.role === 'assistant'
            return (
              <div
                key={m.id}
                className={`group flex w-full ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.role !== 'user' && (
                  <Avatar
                    icon={<Bot size={20} />}
                    classNames={{
                      base: 'bg-transparent text-foreground shrink-0 z-10 mr-3 mt-1',
                    }}
                  />
                )}
                {m.role === 'user' ? (
                  <div className="max-w-[85%]">
                    <div className="bg-default-100 dark:bg-default-50 text-foreground rounded-3xl px-5 py-3 text-[15px] leading-relaxed">
                      {renderMessageContent(text, true)}
                    </div>
                    {renderUserActions(text, m.id)}
                  </div>
                ) : (
                  <div className="flex-auto w-0 pr-1 relative">
                    <div className="font-semibold text-foreground mb-1 text-[15px]">DeepSeek</div>
                    <div className="w-full min-w-full text-[15px] leading-relaxed">
                      {text ? renderMessageContent(text, false, isStreamingThis) : (
                        isStreamingThis ? <TypingDots /> : null
                      )}
                    </div>
                    {!isStreamingThis && text && renderAssistantActions(text, m.id, isLast)}
                  </div>
                )}
              </div>
            )
          })}
          {/* Waiting placeholder: show dots when user sent but no assistant msg yet */}
          {isLoading && messages[messages.length - 1]?.role === 'user' && (
            <div className="flex w-full justify-start mt-4">
              <Avatar
                icon={<Bot size={20} />}
                classNames={{
                  base: 'bg-transparent text-foreground shrink-0 z-10 mr-3 mt-1',
                }}
              />
              <div className="flex-auto w-0 pr-1 relative">
                <div className="font-semibold text-foreground mb-1 text-[15px]">DeepSeek</div>
                <TypingDots />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input - always pinned at bottom */}
      <div className="shrink-0 px-4 pb-4 pt-2 bg-white dark:bg-content1">
        <form
          onSubmit={handleSubmit}
          className={`relative flex flex-col w-full p-2 bg-default-50 dark:bg-content2 rounded-3xl shadow-lg border ${isRecording ? 'border-danger/80 bg-danger/5 shadow-danger/20' : 'border-default-200 dark:border-default-100'}`}
        >
          {attachments.length > 0 && (
            <div className="flex gap-3 px-4 pt-3 pb-1 overflow-x-auto w-full mb-1">
              {attachments.map((file, i) => (
                <div key={i} className="relative w-16 h-16 rounded-xl overflow-hidden bg-content2 border border-default-200 shrink-0 shadow-sm group">
                  <img src={URL.createObjectURL(file)} className="object-cover w-full h-full" alt="attachment" />
                  <button type="button" onClick={() => removeAttachment(i)} className="absolute top-1 right-1 bg-black/60 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
          <div className="flex items-center w-full gap-2 px-1">
            <input
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              ref={fileInputRef}
              onChange={handleFileChange}
            />
            <Button
              isIconOnly
              size="md"
              variant="light"
              radius="full"
              className="text-default-500 ml-1"
              onClick={() => fileInputRef.current?.click()}
            >
              <Paperclip size={20} />
            </Button>
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="发送消息..."
              rows={1}
              className="flex-1 resize-none bg-transparent outline-none text-base px-2 py-3 min-h-[48px] max-h-[200px] overflow-y-auto text-foreground placeholder:text-default-400"
              style={{ lineHeight: '1.5' }}
            />
            <div className="flex-shrink-0 mr-1 flex items-center gap-1 text-default-600">
              {!micPermission && (
                <Button size="sm" variant="flat" color="warning" onClick={authorizeVoice} radius="full" className="px-2 font-medium">
                  预授权语音
                </Button>
              )}
              {micPermission && (
                <Button
                  isIconOnly
                  size="md"
                  color={isRecording ? "danger" : "default"}
                  variant="light"
                  radius="full"
                  onPointerDown={(e) => { e.preventDefault(); startRecording() }}
                  onPointerUp={(e) => { e.preventDefault(); stopRecording() }}
                  onPointerLeave={stopRecording}
                  onContextMenu={(e) => e.preventDefault()}
                  className={`transition-transform duration-200 select-none ${isRecording ? 'scale-110 animate-pulse bg-danger/10' : ''}`}
                  style={{ touchAction: 'none' }}
                >
                  {isRecording ? <MicOff size={20} className="text-danger" /> : <Mic size={20} />}
                </Button>
              )}
              {/* Send / Stop button — same position */}
              {isLoading ? (
                <Button
                  isIconOnly
                  color="danger"
                  variant="solid"
                  radius="full"
                  size="md"
                  onClick={() => { stop(); setWasStopped(true) }}
                  className="flex items-center justify-center"
                >
                  <Square size={14} fill="currentColor" />
                </Button>
              ) : (
                <Button
                  isIconOnly
                  color="primary"
                  variant="solid"
                  radius="full"
                  type="submit"
                  size="md"
                  isDisabled={(!inputValue?.trim() && attachments.length === 0)}
                  className="flex items-center justify-center"
                >
                  <ArrowUp size={18} strokeWidth={2.5} />
                </Button>
              )}
            </div>
          </div>
        </form>
        <div className="text-center text-xs text-default-400 mt-2">
          内容由 AI 生成，请仔细甄别
        </div>
      </div>
    </div>
  )
}
