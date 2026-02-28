'use client'
import type { FC } from 'react'
import React from 'react'
import cn from 'classnames'
import { useTranslation } from 'react-i18next'
import { PencilIcon } from '@heroicons/react/24/solid'
import { Button } from '@heroui/react'
import { Sparkles, Edit2 } from 'lucide-react'
import s from './style.module.css'
import type { AppInfo } from '@/types/app'

export const AppInfoComp: FC<{ siteInfo: AppInfo }> = ({ siteInfo }) => {
  return (
    <div className="mb-8 flex flex-col items-center justify-center">
      <div className='flex flex-col items-center gap-2 py-2 text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary text-center'>
        <Sparkles className="text-primary w-8 h-8 mb-2" />
        欢迎使用 {siteInfo.title}
      </div>
      <p className='text-default-500 text-base mt-2 text-center max-w-lg'>{siteInfo.description}</p>
    </div>
  )
}

export const PromptTemplate: FC<{ html: string }> = ({ html }) => {
  return (
    <div
      className='box-border text-sm text-default-700 bg-content2 p-4 rounded-xl border border-default-100 shadow-sm'
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}

export const ChatBtn: FC<{ onClick: () => void, className?: string }> = ({
  className,
  onClick,
}) => {
  return (
    <div className="flex items-center justify-center w-full mt-6">
      <Button
        color="primary"
        size="lg"
        className={cn(className, "font-medium shadow-md shadow-primary/30 px-8 rounded-full")}
        onClick={onClick}
        startContent={<Sparkles size={18} />}
      >
        英语作文助手
      </Button>
    </div>
  )
}

export const EditBtn = ({ className, onClick }: { className?: string, onClick: () => void }) => {
  const { t } = useTranslation()
  return (
    <Button
      size="sm"
      variant="light"
      className={cn('text-primary font-medium', className)}
      onClick={onClick}
      startContent={< Edit2 size={14} />}
    >
      {t('common.operation.edit')}
    </Button >
  )
}

export const FootLogo = () => (
  <div className="font-bold text-primary tracking-tighter flex items-center gap-1">
    <Sparkles size={14} /> by Xumy
  </div>
)

