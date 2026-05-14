import { Bell, Search, UserCircle } from "lucide-react";

export function Header() {
  return (
    <header className="h-16 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-6">
      <div className="flex items-center bg-gray-100 dark:bg-gray-800 rounded-lg px-3 py-2 w-96">
        <Search className="w-4 h-4 text-gray-500" />
        <input
          type="text"
          placeholder="Search findings, accounts, or CVEs..."
          className="bg-transparent border-none outline-none ml-2 w-full text-sm text-gray-900 dark:text-gray-100"
        />
      </div>
      <div className="flex items-center gap-4">
        <button className="relative p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-critical rounded-full border border-white dark:border-gray-900"></span>
        </button>
        <div className="flex items-center gap-2 border-l border-gray-200 dark:border-gray-800 pl-4">
          <UserCircle className="w-8 h-8 text-gray-400" />
          <div className="text-sm">
            <p className="font-medium">Security Admin</p>
            <p className="text-gray-500 text-xs">Org Delegated Account</p>
          </div>
        </div>
      </div>
    </header>
  );
}
