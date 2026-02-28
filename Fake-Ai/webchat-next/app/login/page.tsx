'use client'

import type { FC } from 'react'
import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { LockClosedIcon, UserIcon } from '@heroicons/react/24/outline'
import AppIcon from '@/app/components/base/app-icon'
import Toast from '@/app/components/base/toast'

const LoginPage: FC = () => {
  const router = useRouter()
  const { notify } = Toast
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    if (!username.trim() || !password.trim()) {
      notify({ type: 'error', message: '请输入用户名和密码', duration: 2500 })
      return
    }

    setLoading(true)
    try {
      localStorage.setItem('fake-ai-auth', JSON.stringify({ username: username.trim(), loginAt: Date.now() }))
      notify({ type: 'success', message: '登录成功', duration: 1500 })
      router.replace('/')
    }
    finally {
      setLoading(false)
    }
  }

  return (
    <div className='min-h-screen bg-slate-100 flex items-center justify-center px-4'>
      <div className='w-full max-w-md rounded-2xl border border-gray-200 bg-white shadow-sm p-6'>
        <div className='flex items-center gap-3 mb-6'>
          <AppIcon />
          <div>
            <div className='text-base font-semibold text-gray-900'>欢迎登录</div>
            <div className='text-xs text-gray-500'>Fake-AI Assistant</div>
          </div>
        </div>

        <form className='space-y-4' onSubmit={handleLogin}>
          <div>
            <label className='block text-sm text-gray-700 mb-1'>用户名</label>
            <div className='relative'>
              <UserIcon className='w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2' />
              <input
                className='w-full h-10 rounded-lg border border-gray-200 bg-white pl-9 pr-3 text-sm outline-none focus:border-primary-400'
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder='请输入用户名'
              />
            </div>
          </div>

          <div>
            <label className='block text-sm text-gray-700 mb-1'>密码</label>
            <div className='relative'>
              <LockClosedIcon className='w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2' />
              <input
                type='password'
                className='w-full h-10 rounded-lg border border-gray-200 bg-white pl-9 pr-3 text-sm outline-none focus:border-primary-400'
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder='请输入密码'
              />
            </div>
          </div>

          <button
            type='submit'
            disabled={loading}
            className='w-full h-10 rounded-lg bg-primary-600 text-white text-sm font-medium hover:bg-primary-700 disabled:opacity-60'
          >
            {loading ? '登录中...' : '登录'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default React.memo(LoginPage)
