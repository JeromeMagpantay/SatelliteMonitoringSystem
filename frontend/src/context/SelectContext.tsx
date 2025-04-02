'use client'
import React, { createContext, useState, useContext, ReactNode } from "react";

// Define the context
interface SelectedContextType {
    selected: string;
    setSelected: React.Dispatch<React.SetStateAction<string>>;
}

// Default value for context
const SelectedContext = createContext<SelectedContextType | undefined>(undefined);

// Provider component
export const SelectedProvider = ({ children }: { children: ReactNode }) => {
    const [selected, setSelected] = useState<string>("Select a Region");

    return (
        <SelectedContext.Provider value={{ selected, setSelected }}>
            {children}
        </SelectedContext.Provider>
    );
};

// Custom hook to use the context
export const useSelected = () => {
    const context = useContext(SelectedContext);
    if (!context) {
        throw new Error("useSelected must be used within a SelectedProvider");
    }
    return context;
};
