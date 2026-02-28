import type { FC } from 'react'
import React from 'react'
import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  Button,
} from '@heroui/react'
import { Menu, SquarePen, Bot, Home } from 'lucide-react'
import AppIcon from '@/app/components/base/app-icon'

export interface IHeaderProps {
  title: string
  isMobile?: boolean
  onShowSideBar?: () => void
  onCreateNewChat?: () => void
  onGoHome?: () => void
}

const Header: FC<IHeaderProps> = ({
  title,
  isMobile,
  onShowSideBar,
  onCreateNewChat,
  onGoHome,
}) => {
  return (
    <Navbar
      maxWidth="full"
      classNames={{
        base: "bg-content1 dark:bg-content2 shadow-sm shrink-0",
        wrapper: "px-4",
      }}
    >
      <NavbarContent justify="start">
        {isMobile && (
          <NavbarItem>
            <Button
              isIconOnly
              variant="light"
              onClick={() => onShowSideBar?.()}
              aria-label="Menu"
            >
              <Menu size={20} className="text-default-600" />
            </Button>
          </NavbarItem>
        )}
        <NavbarItem>
          <Button
            isIconOnly
            variant="light"
            onClick={() => onGoHome?.()}
            aria-label="Home"
          >
            <Home size={20} className="text-default-600" />
          </Button>
        </NavbarItem>
      </NavbarContent>

      <NavbarContent justify="center">
        <NavbarBrand className="gap-2 shrink-0">
          <div className="bg-primary/10 p-1.5 rounded-xl text-primary">
            <Bot size={22} />
          </div>
          <p className="font-bold text-inherit">{title === 'Chat APP' ? 'DeepSeek' : title}</p>
        </NavbarBrand>
      </NavbarContent>

      <NavbarContent justify="end">
        <NavbarItem>
          <Button
            isIconOnly
            variant="light"
            color="primary"
            onClick={() => onCreateNewChat?.()}
            aria-label="New Chat"
          >
            <SquarePen size={20} />
          </Button>
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  )
}

export default React.memo(Header)
