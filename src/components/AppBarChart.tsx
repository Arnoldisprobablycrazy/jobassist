"use client"

import { ChartContainer, type ChartConfig } from "@/components/ui/chart"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "#2563eb",
  },
  mobile: {
    label: "Mobile",
    color: "#60a5fa",
  },
} satisfies ChartConfig

const chartData = [
  { month: "July", desktop: 30, mobile: 0 },
  { month: "August", desktop: 40, mobile: 0 },
  { month: "September", desktop: 44, mobile: 0 },
  { month: "October", desktop: 44, mobile: 0 },
  { month: "November", desktop: 58, mobile: 0 },
  { month: "December", desktop: 75, mobile: 0 },
]

const AppBarChart = () => {
  return (
    <div className="w-full">
      <h1 className="text-texts-cards font-bold text-lg mb-4">Cover Letter Match Score Trends</h1>
      <div className="h-64 w-full"> 
       <ChartContainer config={chartConfig} className="h-full w-full">
      <BarChart accessibilityLayer data={chartData}>
        <CartesianGrid vertical={false} />
            <XAxis
                dataKey="month"
                tickLine={false}
                tickMargin={10}
                axisLine={false}
                tickFormatter={(value) => value.slice(0, 3)}
                />
            <YAxis
                
                tickLine={false}
                tickMargin={10}
                axisLine={false}
                />


        <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
      </BarChart>
    </ChartContainer>
    </div>
    </div>
  )
}

export default AppBarChart
