'use client';

import { Home, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function Header() {
  return (
    <header className="w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 shadow-sm">
      <div className="container mx-auto px-4 md:px-6 flex h-16 items-center justify-between">
        {/* Logo */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary text-primary-foreground shadow-sm">
            <Home className="w-4 h-4" />
          </div>
          <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">RealTech</span>
        </div>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
          <Link href="#" className="transition-colors hover:text-primary text-foreground/60">
            Home
          </Link>
          <Link href="#" className="transition-colors hover:text-primary text-foreground/60">
            About
          </Link>
          <Link href="#" className="transition-colors hover:text-primary text-foreground/60">
            API
          </Link>
        </nav>

        {/* CTA Button */}
        <Button size="sm" className="gap-2 bg-primary hover:bg-primary/90 shadow-sm">
          <TrendingUp className="w-4 h-4" />
          Get Started
        </Button>
      </div>
    </header>
  );
}