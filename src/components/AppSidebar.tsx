import { BarChart3, Bell, Calendar, Calendar1, ChevronUp, HelpCircle, Home, Inbox, Mail, Search, Settings, Target, User, User2 } from "lucide-react"
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarSeparator } from "./ui/sidebar"
import Link from "next/link"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu"

const mainItems = [
  {
    title: "Dashboard",
    url: "#",
    icon: Home,
  },
  {
    title: "Cover Letters",
    url: "/dashboard/cover-letters",
    icon: Mail,
  },
  {
    title: "Job Matcher",
    url: "#",
    icon: Target,
  },
  {
    title: "Search",
    url: "#",
    icon: Search,
  },
  {
    title: "Settings",
    url: "#",
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
  return <Sidebar collapsible="icon">
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
              <SidebarMenuItem key ={item.title}>
                <SidebarMenuButton asChild>
                  <Link href ={item.url}>
                  <item.icon/>
                  <span>{item.title}</span>
                  </Link>
                </SidebarMenuButton>

              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroupContent>
       </SidebarGroup>
       

       {/*Tools & Features Group*/}
       <SidebarGroup>
        <SidebarGroupLabel>Tools & Features</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            {toolsItems.map(item =>(
              <SidebarMenuItem key ={item.title}>
                <SidebarMenuButton asChild>
                  <Link href ={item.url}>
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
              <SidebarMenuItem key ={item.title}>
                <SidebarMenuButton asChild>
                  <Link href ={item.url}>
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
                <User2/> John Doe<ChevronUp className="ml-auto"/>

              </SidebarMenuButton>
              
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Account</DropdownMenuItem>
              <DropdownMenuItem >
                <p className="text-xs text-gray-600 truncate bg-background-accenty">Premium plan</p>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>
  </Sidebar>
}

export default AppSidebar
