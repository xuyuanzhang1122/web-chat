import React from 'react'
import type { FC } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, MessageSquare, MessageSquareDot } from 'lucide-react'
import { Button, ScrollShadow, Divider } from '@heroui/react'
import type { ConversationItem } from '@/types/app'

export interface ISidebarProps {
  copyRight: string
  currentId: string
  onCurrentIdChange: (id: string) => void
  list: ConversationItem[]
}

const MAX_CONVERSATION_LENTH = 20

const Sidebar: FC<ISidebarProps> = ({
  copyRight,
  currentId,
  onCurrentIdChange,
  list,
}) => {
  const { t } = useTranslation()

  return (
    <div className="shrink-0 flex flex-col bg-content1 dark:bg-content2 pc:w-[260px] tablet:w-[220px] mobile:w-[240px] border-r border-default-200 tablet:h-[calc(100vh_-_3rem)] mobile:h-screen">

      {/* New Chat Button */}
      {list.length < MAX_CONVERSATION_LENTH && (
        <div className="p-4 pb-2">
          <Button
            radius="lg"
            color="primary"
            variant="flat"
            startContent={<Plus size={18} />}
            className="w-full justify-start font-medium"
            onClick={() => onCurrentIdChange('-1')}
          >
            开启新对话
          </Button>
        </div>
      )}

      {/* Conversation List */}
      <ScrollShadow className="flex-1 px-3 py-2 space-y-1">
        {list.map((item) => {
          const isCurrent = item.id === currentId
          return (
            <div
              key={item.id}
              onClick={() => onCurrentIdChange(item.id)}
              className={`
                group flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200
                ${isCurrent
                  ? 'bg-primary text-primary-foreground shadow-md'
                  : 'text-default-700 hover:bg-default-100'
                }
              `}
            >
              <div className={`shrink-0 ${isCurrent ? 'text-primary-foreground' : 'text-default-400 group-hover:text-primary'}`}>
                {isCurrent ? <MessageSquareDot size={18} /> : <MessageSquare size={18} />}
              </div>
              <span className="truncate text-sm font-medium">
                {item.name}
              </span>
            </div>
          )
        })}
      </ScrollShadow>

      {/* Footer Area */}
      <div className="p-4 pt-2">
        <Divider className="mb-4" />
        <div className="text-default-400 font-normal text-xs text-center">
          © {copyRight} {(new Date()).getFullYear()}
        </div>
      </div>
    </div>
  )
}

export default React.memo(Sidebar)
