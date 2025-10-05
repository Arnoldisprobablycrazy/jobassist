// src/app/Dashboard/layout.tsx
import AppSidebar from "@/components/AppSidebar";
import Navbar from "@/components/Navbar";
import { ThemeProvider } from "@/components/providers/ThemeProvider";
import { SidebarProvider } from "@/components/ui/sidebar";
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { cookies } from "next/headers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono", 
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Dashboard - JobAssist",
  description: "Manage your job applications and track your progress",
};

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {

  const cookieStore = await cookies()
  const defaultOpen = cookieStore.get("sidebar_state")?.value === "true"
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ThemeProvider attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange>

          <SidebarProvider defaultOpen={defaultOpen}> 
          <AppSidebar />
          <main className="flex-1 w-full">
            <Navbar />
            <div className="px-4 py-6">
              {children}
            </div>
          </main>
          </SidebarProvider>   
          </ThemeProvider>
        
      </body>
    </html>
  );
}