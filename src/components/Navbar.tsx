"use client";
import { LogOut, Moon, Receipt, Settings, Sun, User } from 'lucide-react'
import Link from 'next/link'
import React, { useState } from 'react'
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useTheme } from 'next-themes'
import { Button } from './ui/button'
import { SidebarTrigger, useSidebar } from './ui/sidebar'
import { signOut } from '../../actions/auth'
import Toast from './toast'

const Navbar = () => {
  const { theme, setTheme } = useTheme();
  const { toggleSidebar } = useSidebar()
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [showLogoutToast, setShowLogoutToast] = useState(false)

  const handleLogout = async () => {
    setIsLoggingOut(true)
    setShowLogoutToast(true) // Show toast immediately

    try {
      await signOut()
      // The redirect happens in the server action
    } catch (error) {
      console.error('Logout failed:', error)
      setShowLogoutToast(false) // Hide toast on error
      setIsLoggingOut(false)
      // You could show an error toast here
    }
  }

  return (
    <>
      {/* Logout Toast */}
      <Toast
        message="Logging out..."
        type="info"
        isVisible={showLogoutToast}
        onClose={() => setShowLogoutToast(false)}
        duration={3000}
      />

      <nav className='p-4 flex items-center justify-between'>
        {/*LEFT*/}
        <SidebarTrigger />

        {/*RIGHT*/}
        <div className="flex items-center gap-4">
          <Link href="/">Dashboard</Link>

          {/*THEME MENU*/}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon">
                <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
                <Moon className="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
                <span className="sr-only">Toggle theme</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setTheme("light")}>
                Light
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("dark")}>
                Dark
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("system")}>
                System
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* USER MENU */}
          <DropdownMenu>
            <DropdownMenuTrigger>
              <Avatar>
                <AvatarImage src="https://github.com/shadcn.png" />
                <AvatarFallback>CN</AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent sideOffset={10}>
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <Link href="/dashboard/profile" className="flex items-center">
                  <User className='h-[1.2rem] w-[1.2rem] mr-2' />
                  Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Receipt className='h-[1.2rem] w-[1.2rem] mr-2' />
                Billing
              </DropdownMenuItem>
              
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="text-red-600 focus:text-red-600 focus:bg-red-50"
              >
                <LogOut className='h-[1.2rem] w-[1.2rem] mr-2' />
                {isLoggingOut ? 'Logging out...' : 'Logout'}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </nav>
    </>
  )
}

export default Navbar