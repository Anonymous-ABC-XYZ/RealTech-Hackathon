'use client';

import * as React from "react"
import { createPortal } from "react-dom"

import { cn } from "@/lib/utils"

export interface TooltipProps {
  children: React.ReactNode
  content: React.ReactNode
  className?: string
}

export function Tooltip({ children, content, className }: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false)
  const [position, setPosition] = React.useState({ top: 0, left: 0 })
  const triggerRef = React.useRef<HTMLDivElement>(null)
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  const updatePosition = () => {
    if (triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect()
      setPosition({
        top: rect.bottom + 8,
        left: rect.left + rect.width / 2
      })
    }
  }

  const handleMouseEnter = () => {
    updatePosition()
    setIsVisible(true)
  }

  return (
    <div className="relative inline-block">
      <div
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      {mounted && isVisible && createPortal(
        <div
          className={cn(
            "fixed z-[9999] w-64 p-3 text-xs text-white bg-slate-900 border border-slate-700 rounded-lg shadow-xl",
            "-translate-x-1/2",
            "animate-in fade-in-0 zoom-in-95",
            className
          )}
          style={{ top: `${position.top}px`, left: `${position.left}px` }}
        >
          <div className="relative">
            <div className="absolute -top-[13px] left-1/2 -translate-x-1/2 w-3 h-3 rotate-45 bg-slate-900 border-l border-t border-slate-700" />
            {content}
          </div>
        </div>,
        document.body
      )}
    </div>
  )
}
