'use client'
import React, { useEffect, useState } from 'react'
import { ScrollArea } from './ui/scroll-area';
import { useSelected } from '@/context/SelectContext';
import axios from 'axios';

function Logs() {
    const logss = [
        {
            timestamp: "09/30/2022 2:53:32 AM",
            event: "sync_end",
            details: {
                    "timestamp": {
                      "$date": "2025-04-01T19:47:06.054Z"
                    },
                    "region": null,
                    "routing_key": "satellite.status",
                    "satellite_id": "LOW-16",
                    "status": "INACTIVE - AVAILABLE",
                    "classification": "LOW"
            },
        },
    ];

    const { selected } = useSelected();
    const [logs, setLogs] = useState<[]>([]);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                if (selected === 'all' || selected === "Select a Region") {
                    const response = await axios.get("http://127.0.0.1:8000/logs?limit=300", );
                    setLogs(response.data);    
                }
            } catch (error) {
                console.error("Error fetching logs:", error);
            }
        };

        // Fetch immediately
        fetchLogs();

        // // Set up polling interval
        // const interval = setInterval(fetchRegions, 10000);

        // // Cleanup on unmount
        // return () => clearInterval(interval);
    }, []);

    console.log(logs)

    const highlightJSON = (json: Object) => {
        let jsonStr = JSON.stringify(json, null, 2);
        jsonStr = jsonStr
        .replace(/"([^"]+)":/g, '<span class="text-green-400">"$1"</span>:') // Keys
        .replace(/: "(.*?)"/g, ': <span class="text-blue-400">"$1"</span>') // Strings
        .replace(/: (\d+)/g, ': <span class="text-orange-400">$1</span>') // Numbers
        .replace(/: (true|false)/g, ': <span class="text-purple-400">$1</span>') // Booleans
        .replace(/: (null)/g, ': <span class="text-gray-400">$1</span>') // Null
        .replace(/([{}[\],:])/g, '<span class="text-gray-300">$1</span>'); // Brackets, colons, commas
        return jsonStr;
    };
    
    return (
        <ScrollArea className='w-full h-[570px]'>
            <div className='flex flex-col w-full space-y-2'>
                {logs.map((item, index) => (
                    <div key={index} className={`collapse collapse-arrow ${item["routing_key"] === "satellite.outage" ? 'bg-error' : 'bg-base-100'} border border-base-300 rounded-md`}>
                        <input type="radio" name="logs"/>
                        <div className="collapse-title flex justify-between">
                            <span>Timestamp: {new Date(item["timestamp"]).toLocaleString()}</span>
                            <span>Status: {item["status"] ? item["status"] : "None"}</span>
                        </div>
                        <div className="collapse-content text-sm">
                            <pre className='bg-gray-800 p-5 rounded-md text-xs' dangerouslySetInnerHTML={{ __html: highlightJSON(item) }} />
                        </div>
                    </div>    
                ))}
            </div>    
        </ScrollArea>
    );
}

export default Logs