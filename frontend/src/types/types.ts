interface CoverageRegion {
    _id: string;
    name: string;
    region_number: number;
    number_of_clients: number;
    peak_usage_start_time: string;
    peak_usage_end_time: string;
    coverage_flag: boolean;
    satellite_providers: string[]; 
}