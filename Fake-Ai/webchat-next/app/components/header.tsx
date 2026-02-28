import type { FC } from 'react'
import React from 'react'
import {
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  PencilSquareIcon,
} from '@heroicons/react/24/solid'
import AppIcon from '@/app/components/base/app-icon'
export interface IHeaderProps {
  title: string
  isMobile?: boolean
  onShowSideBar?: () => void
  onCreateNewChat?: () => void
  onLogout?: () => void
}
const Header: FC<IHeaderProps> = ({
  title,
  isMobile,
  onShowSideBar,
  onCreateNewChat,
  onLogout,
}) => {
  return (
    <div className="shrink-0 flex items-center justify-between h-14 px-3 mobile:px-2.5 bg-white border-b border-gray-200">
      {isMobile
        ? (
          <div
            className='flex items-center justify-center h-8 w-8 rounded-md cursor-pointer hover:bg-gray-100'
            onClick={() => onShowSideBar?.()}
          >
            <Bars3Icon className="h-4 w-4 text-gray-500" />
          </div>
        )
        : <div></div>}
      <div className='flex items-center space-x-2.5'>
        <AppIcon size="small" className='shadow-sm' />
        <div className="text-sm text-gray-800 font-semibold truncate max-w-[48vw] pc:max-w-none">{title}</div>
      </div>
      <div className='flex items-center gap-1'>
        {isMobile && (
          <div className='flex items-center justify-center h-8 w-8 rounded-md cursor-pointer hover:bg-gray-100' onClick={() => onCreateNewChat?.()} >
            <PencilSquareIcon className="h-4 w-4 text-gray-500" />
          </div>
        )}
        <div className='flex items-center justify-center h-8 w-8 rounded-md cursor-pointer hover:bg-gray-100' onClick={() => onLogout?.()}>
          <ArrowRightOnRectangleIcon className="h-4 w-4 text-gray-500" />
        </div>
      </div>
    </div>
  )
}

export default React.memo(Header)
