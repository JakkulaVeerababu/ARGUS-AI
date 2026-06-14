import React, { useState } from "react";
import { Dashboard } from "./pages/Dashboard";
import { Search } from "./pages/Search";
import { Rankings } from "./pages/Rankings";
import { Analytics } from "./pages/Analytics";
import { LayoutDashboard, Search as SearchIcon, Award, BarChart3, ShieldCheck } from "lucide-react";

type TabName = "dashboard" | "search" | "rankings" | "analytics";

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabName>("dashboard");

  const renderActivePage = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />;
      case "search":
        return <Search />;
      case "rankings":
        return <Rankings />;
      case "analytics":
        return <Analytics />;
      default:
        return <Dashboard />;
    }
  };

  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: <LayoutDashboard size={18} /> },
    { id: "search", label: "Search Engine", icon: <SearchIcon size={18} /> },
    { id: "rankings", label: "Top 100 Rankings", icon: <Award size={18} /> },
    { id: "analytics", label: "Analytics", icon: <BarChart3 size={18} /> },
  ] as const;

  return (
    <div className="min-h-screen bg-gray-50/50 flex">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col justify-between">
        <div className="p-6">
          {/* Logo Title */}
          <div className="flex items-center space-x-2 text-brand-primary">
            <ShieldCheck size={26} className="stroke-[2.5]" />
            <span className="font-sans font-bold text-xl tracking-tight text-gray-900">
              ARGUS <span className="text-brand-primary">AI</span>
            </span>
          </div>
          
          {/* Navigation Links */}
          <nav className="mt-8 space-y-1">
            {menuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 text-sm font-medium rounded-lg transition-all focus:outline-none cursor-pointer ${
                  activeTab === item.id
                    ? "bg-blue-50/50 text-brand-primary border-l-2 border-brand-primary pl-3.5"
                    : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Footer info in sidebar */}
        <div className="p-6 border-t border-gray-100">
          <div className="flex items-center space-x-2 text-xs text-gray-400">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
            <span>Candidate Pool Index Ready</span>
          </div>
          <p className="text-[10px] text-gray-300 mt-1 font-mono">100K profiles indexed</p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 bg-white min-h-screen p-10 overflow-y-auto">
        <div className="max-w-5xl mx-auto">
          {renderActivePage()}
        </div>
      </main>
    </div>
  );
};

export default App;
