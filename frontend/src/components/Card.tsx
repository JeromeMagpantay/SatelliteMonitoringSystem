import React from 'react'

interface CardProps {
    name: string;
    satellites: number;
    clients: number;
    peak_usage_start_time: string;
    peak_usage_end_time: string;
    coverage: boolean;
}

function Card({ name, satellites, clients, peak_usage_start_time, peak_usage_end_time, coverage} : CardProps) {

    // Convert time strings to Date objects
    const getTimeAsDate = (timeStr: string) => {
        const [hours, minutes, seconds] = timeStr.split(":").map(Number);
        const date = new Date();
        date.setHours(hours, minutes, seconds, 0); // Set only the time, keep today's date
        return date;
    };

    const startTime = getTimeAsDate(peak_usage_start_time);
    const endTime = getTimeAsDate(peak_usage_end_time);
    const now = new Date(); // Get the current time

    // Check if the current time is within the peak usage period
    const isPeakUsage = now >= startTime && now <= endTime;
    
    return (
        <div className="card bg-base-100 shadow-sm">
            <div className="card-body space-y-3">
                {isPeakUsage ? 
                <div className="flex items-center gap-2">
                    <span className="w-3 h-3 bg-[#66CC8A] rounded-full"></span>
                    <span className="text-sm">Currently at Peak Usage</span>
                </div>: 
                <div className="flex items-center gap-2">
                    <span className="w-3 h-3 bg-base-300 rounded-full"></span>
                    <span className="text-sm">Regulary Usage</span>
                </div>
                }
                <div className="flex justify-between">
                    <h2 className="text-lg font-bold w-[70%]">{name}</h2>
                    <span className="text-lg text-[#377CFB]"><span className="text-sm text-base-content">satellites: </span>{satellites}</span>
                </div>
                <div className='flex items-center'>
                    <svg xmlns="http://www.w3.org/2000/svg" className="size-6 me-2 inline-block text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
                    <span className='text-base'>Active clients: <span className='ml-1 text-lg font-semibold text-primary'>{clients}</span></span>
                </div>
                <div className="">
                    <div className={`${coverage ? "bg-[#66CC8A]" : "bg-error"} rounded-md p-3 flex justify-center text-sm font-semibold`}>{coverage ? "Full Coverage" : "Outage Detected"}</div>
                </div>
            </div>
        </div>
    )
}

export default Card