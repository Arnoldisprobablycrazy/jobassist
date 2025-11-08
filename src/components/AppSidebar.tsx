"use client";

import { BarChart3, Bell, Calendar, Calendar1, ChevronUp, HelpCircle, Home, Inbox, Mail, Search, Settings, Target, User, User2 } from "lucide-react"
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarSeparator } from "./ui/sidebar"
import Link from "next/link"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu"
import { useState, useEffect } from "react"
import { createClient } from "@/utils/supabase/client"
import { User as SupabaseUser } from '@supabase/supabase-js'

const mainItems = [
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: Home,
  },
  {
    title: "Cover Letters",
    url: "/dashboard/cover-letters",
    icon: Mail,
  },
  {
    title: "Job Matcher",
    url: "/dashboard/job-matcher",
    icon: Target,
  },
  {
    title: "Search",
    url: "/dashboard/search",
    icon: Search,
  },
  {
    title: "Settings",
    url: "/dashboard/settings",
    icon: Settings,
  },
]

// tools and feature items

const toolsItems = [
  {
    title: "Interview Calendar",
    url: "/dashboard/calendar",
    icon: Calendar1
  },
  {
    title :"Job Search",
    url:'/dashboard/search',
    icon: Search
  },
  {
    title: "Analytics",
    url:"/dashboard/analytics",
    icon: BarChart3
  }
]

const accountItems = [
  {
    title:"Profile",
    url: "/dashboard/profile",
    icon: User,
  },
  {
    title: "Notifications",
    url:"/dashboard/notifications",
    icon: Bell,
  },
  {
    title:"Settings",
    url: "/dashboard/settings",
    icon: Settings,
  },
  {
    title: "Help & Support",
    url: "/dashboard/help",
    icon: HelpCircle,
  }
]

const AppSidebar = () => {
  const [user, setUser] = useState<SupabaseUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUser = async () => {
      const supabase = createClient()
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
      setLoading(false)
    }

    fetchUser()
  }, [])

  const getUserDisplayName = () => {
    if (!user) return "Loading..."
    
    // Try to get username first, then fall back to email
    const username = user.user_metadata?.username
    const email = user.email
    
    return username || email || "User"
  }

  const getUserEmail = () => {
    if (!user) return ""
    return user.email || ""
  }

  return (
    <Sidebar collapsible="icon" className="bg-background-sidbar">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/dashboard">
                <span className="text-xl font-bold text-primary">JobAssist</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarSeparator/>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Main Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainItems.map(item =>(
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <Link href={item.url}>
                      <item.icon/>
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        
        {/* Tools & Features Group */}
        <SidebarGroup>
          <SidebarGroupLabel>Tools & Features</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {toolsItems.map(item =>(
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <Link href={item.url}>
                      <item.icon/>
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Account & Support</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {accountItems.map(item =>(
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <Link href={item.url}>
                      <item.icon/>
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton>
                  <User2/> 
                  <span className="truncate max-w-[120px]">{getUserDisplayName()}</span>
                  <ChevronUp className="ml-auto"/>
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-64">
                <DropdownMenuItem asChild>
                  <Link href="/dashboard/profile" className="flex flex-col items-start p-3 cursor-pointer">
                    <span className="font-medium text-sm">Signed in as</span>
                    <span className="text-xs text-gray-600 truncate w-full mt-1">
                      {getUserEmail() || getUserDisplayName()}
                    </span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/dashboard/profile" className="p-2 cursor-pointer">
                    <p className="text-xs  text-yellow-800 px-2 py-1 rounded w-full text-center">
                      Premium plan
                    </p>
                  </Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar