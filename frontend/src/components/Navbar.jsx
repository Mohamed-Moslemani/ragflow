export default function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200 shadow-md">
      <div className="max-w-7xl mx-auto px-6 sm:px-10">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <div className="relative">
             
            </div>
            <div className="flex flex-col">
              <span className="text-purple-700 font-mono font-extrabold tracking-widest text-2xl">
                Quantech
              </span>
              <span className="text-purple-400 font-mono tracking-wider text-sm">
                Ragging System
              </span>
            </div>
          </div>

          {/* Right section: Feature badges */}
          <div className="hidden sm:flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-50 rounded-full border border-green-200">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-green-700 text-xs font-medium">Secure</span>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-blue-50 rounded-full border border-blue-200">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-blue-700 text-xs font-medium">Reliable</span>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-purple-50 rounded-full border border-purple-200">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span className="text-purple-700 text-xs font-medium">Intelligent</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
