import Logs from "@/components/Logs";
import Sidebar from "@/components/Sidebar";
import { BiBookContent } from "react-icons/bi";
import axios from "axios";

export default async function Home() {
  return (
    <main className="w-screen h-screen flex p-5">
      <Sidebar/>
      <div className="flex flex-col grow pl-5 space-y-5">
        <div className="mt-8 flex items-center space-x-4">
          <BiBookContent size={35}/>
          <h1 className="text-2xl font-bold">Log Stream</h1>
        </div>
        <div className="flex flex-1 bg-base-200 w-full rounded-lg p-4">
          <Logs/>
        </div>
      </div>
    </main>
  );
}
