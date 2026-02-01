'use client';

import * as React from "react"

import { cn } from "@/lib/utils"

export interface TooltipProps {
  children: React.ReactNode
  content: React.ReactNode
  className?: string
}

export function Tooltip({ children, content, className }: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false)

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      {isVisible && (
        <div
          className={cn(
            "absolute z-50 w-64 p-3 text-xs text-white bg-slate-900 border border-slate-700 rounded-lg shadow-xl",
            "bottom-full left-1/2 -translate-x-1/2 mb-2",
            "animate-in fade-in-0 zoom-in-95",
            className
          )}
        >
          <div className="relative">
            {content}
            <div className="absolute -bottom-[13px] left-1/2 -translate-x-1/2 w-3 h-3 rotate-45 bg-slate-900 border-r border-b border-slate-700" />
          </div>
        </div>
      )}
    </div>
  )
}
