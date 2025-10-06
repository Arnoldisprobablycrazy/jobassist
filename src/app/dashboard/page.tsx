import AppBarChart from '@/components/AppBarChart'
import DashboardCards from '@/components/DashboardCards'
import React from 'react'


const Dashboardpage = () => {
  return (
    <div className='grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-4 gap-4'>
      <div className="bg-primary-foreground -4 rounded-lg col-span-full"><DashboardCards/> </div>
      
      <div className="bg-primary-foreground p-4 rounded-lg lg:col-span-2 2xl:col-span-2"><AppBarChart/></div>

    </div>
  )
}

export default Dashboardpage
