'use client'

import React, { use, useEffect, useState } from 'react'
import Card from './Card'
import { ScrollArea } from './ui/scroll-area'
import axios from 'axios'
import { FaSatellite } from "react-icons/fa6";
import { useSelected } from '@/context/SelectContext'

interface SidebarProps {
    data: CoverageRegion[]
}

function Sidebar() {
    const { selected, setSelected } = useSelected();
    const [regions, setRegions] = useState<CoverageRegion[]>([]);

    useEffect(() => {
        const fetchRegions = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:8000/regions");
                setRegions(response.data);
            } catch (error) {
                console.error("Error fetching regions:", error);
            }
        };

        // Fetch immediately
        fetchRegions();

        // // Set up polling interval
        // const interval = setInterval(fetchRegions, 10000);

        // // Cleanup on unmount
        // return () => clearInterval(interval);
    }, []);

    return (
        <div className="w-[400px] bg-neutral flex flex-col p-5 rounded-lg space-y-5">
            <div className='flex items-center space-x-2'>
                <FaSatellite className='text-neutral-content' size={20}/>
                <h2 className="text-xl font-semibold text-neutral-content">Satellite Network Distribution</h2>   
            </div>
            <div>
                <select value={selected} className="select select-sm" onChange={(event) => setSelected(event.target.value)}>
                    <option disabled={true} value="Select a Region">Select a Region</option>
                    <option value='all'>All</option>
                    {regions.map((item, index) => (
                        <option key={index} value={item.region_number}>{item.name}</option>
                    ))}
                </select>
            </div>
            <ScrollArea>
                {selected === 'all' || selected === 'Select a Region' ?
                    <div className="flex flex-col space-y-5">
                        {regions.map((item, index) => (
                            <Card key={index} name={item.name} satellites={item.satellite_providers.length} clients={item.number_of_clients} peak_usage_end_time={item.peak_usage_end_time} peak_usage_start_time={item.peak_usage_start_time} coverage={item.coverage_flag}/>
                        ))}
                    </div>
                    :
                    <div className="flex flex-col space-y-5">
                        {regions.map((item, index) => (
                            item.region_number === parseInt(selected) ?
                            <Card key={index} name={item.name} satellites={item.satellite_providers.length} clients={item.number_of_clients} peak_usage_end_time={item.peak_usage_end_time} peak_usage_start_time={item.peak_usage_start_time} coverage={item.coverage_flag}/>
                            : <></>
                        ))}
                    </div>
                }
            </ScrollArea>
        </div>
    )
}

export default Sidebar