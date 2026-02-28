'use client'
import type { FC, ReactNode } from 'react'
import React from 'react'
import cn from 'classnames'
import { useTranslation } from 'react-i18next'
import { Sparkles } from 'lucide-react'
import { Button, Card, CardHeader, CardBody } from '@heroui/react'

export interface ITemplateVarPanelProps {
  className?: string
  header: ReactNode
  children?: ReactNode | null
  isFold: boolean
}

const TemplateVarPanel: FC<ITemplateVarPanelProps> = ({
  className,
  header,
  children,
  isFold,
}) => {
  return (
    <Card
      className={cn(className, 'border-none shadow-sm')}
      classNames={{
        base: isFold
          ? "bg-content1 dark:bg-content2 border border-default-200"
          : "bg-content1 dark:bg-content2 shadow-md border border-primary/20"
      }}
    >
      <CardHeader className={cn("px-6 py-4 bg-primary/5", isFold && "rounded-b-xl")}>
        <div className="w-full text-sm">
          {header}
        </div>
      </CardHeader>

      {!isFold && children && (
        <CardBody className="px-6 py-5">
          {children}
        </CardBody>
      )}
    </Card>
  )
}

export const PanelTitle: FC<{ title: string, className?: string }> = ({
  title,
  className,
}) => {
  return (
    <div className={cn(className, 'flex items-center space-x-1.5 text-primary-600 font-medium')}>
      <Sparkles size={16} />
      <span className='text-sm'>{title}</span>
    </div>
  )
}

export const VarOpBtnGroup: FC<{ className?: string, onConfirm: () => void, onCancel: () => void }> = ({
  className,
  onConfirm,
  onCancel,
}) => {
  const { t } = useTranslation()

  return (
    <div className={cn(className, 'flex mt-4 space-x-3 mobile:ml-0 tablet:ml-[128px]')}>
      <Button
        color="primary"
        variant="solid"
        onClick={onConfirm}
        className="font-medium"
      >
        {t('common.operation.save')}
      </Button>
      <Button
        variant="flat"
        onClick={onCancel}
        className="font-medium"
      >
        {t('common.operation.cancel')}
      </Button>
    </div>
  )
}

export default React.memo(TemplateVarPanel)
