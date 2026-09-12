import React, { useState } from 'react';

interface ShipClass {
  id: string;
  name: string;
  class: string;
  color: string;
  textColor?: string;
}

const StarfleetInterface: React.FC = () => {
  const [selectedShip, setSelectedShip] = useState<string | null>(null);
  const [selectedFaction, setSelectedFaction] = useState<string | null>(null);
  const [isActivated, setIsActivated] = useState(false);

  const shipClasses: ShipClass[] = [
    { id: '22th', name: '22-TH', class: 'NX-CLASS', color: '#808080', textColor: '#000000' },
    { id: '23rd', name: '23-RD', class: 'CONSTITUTION', color: '#FFFF00', textColor: '#000000' },
    { id: '23st', name: '23-ST', class: 'EXCELSIOR', color: '#0080FF', textColor: '#FFFFFF' },
    { id: '24th', name: '24-TH', class: 'GALAXY-CLASS', color: '#FF8C00', textColor: '#000000' },
    { id: '25th', name: '25-TH', class: 'TITAN-CLASS', color: '#4A90E2', textColor: '#FFFFFF' },
    { id: '29th', name: '29-TH', class: 'TCARS', color: '#40E0D0', textColor: '#000000' }
  ];

  const factions = [
    { id: 'ufp', name: 'UFP', color: '#0080FF' },
    { id: 'kln', name: 'KLN', color: '#FF0000' },
    { id: 'rom', name: 'ROM', color: '#40E0D0' },
    { id: 'car', name: 'CAR', color: '#A0522D' }
  ];

  const handleShipSelect = (shipId: string) => {
    setSelectedShip(selectedShip === shipId ? null : shipId);
  };

  const handleFactionSelect = (factionId: string) => {
    setSelectedFaction(selectedFaction === factionId ? null : factionId);
  };

  const handleActivate = () => {
    if (selectedShip) {
      setIsActivated(true);
      setTimeout(() => setIsActivated(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-black p-8 font-mono">
      <div className="relative w-full max-w-6xl mx-auto">
        {/* Main Frame */}
        <div className="relative bg-black border-4 border-gray-400 rounded-lg p-6">
          
          {/* Corner Indicators */}
          <div className="absolute -top-2 -left-2 w-8 h-8 bg-blue-600 rounded-full border-2 border-gray-400"></div>
          <div className="absolute -top-2 -right-2 w-8 h-8 bg-red-600 rounded-full border-2 border-gray-400"></div>
          
          {/* Side Labels */}
          <div className="absolute -left-12 top-1/2 transform -translate-y-1/2 -rotate-90 text-gray-400 text-lg font-bold tracking-widest">
            NX-01
          </div>
          <div className="absolute -right-12 top-1/2 transform -translate-y-1/2 rotate-90 text-gray-400 text-lg font-bold tracking-widest">
            INTERFACE
          </div>

          <div className="flex h-96">
            {/* Left Panel - Faction Buttons */}
            <div className="flex flex-col space-y-2 mr-6">
              {factions.map((faction) => (
                <button
                  key={faction.id}
                  onClick={() => handleFactionSelect(faction.id)}
                  className={`w-16 h-16 text-white font-bold text-sm border-2 border-gray-400 transition-all duration-200 hover:brightness-110 ${
                    selectedFaction === faction.id ? 'ring-2 ring-white' : ''
                  }`}
                  style={{ backgroundColor: faction.color }}
                >
                  {faction.name}
                </button>
              ))}
            </div>

            {/* Central Area */}
            <div className="flex-1 border-2 border-gray-400 bg-black p-6 relative">
              {/* Ship Class Blocks */}
              <div className="grid grid-cols-2 gap-6 h-full">
                <div className="space-y-4">
                  {shipClasses.slice(0, 3).map((ship) => (
                    <button
                      key={ship.id}
                      onClick={() => handleShipSelect(ship.id)}
                      className={`w-full h-16 border-2 border-gray-400 transition-all duration-200 hover:brightness-110 relative ${
                        selectedShip === ship.id ? 'ring-2 ring-white' : ''
                      }`}
                      style={{ 
                        backgroundColor: ship.color,
                        color: ship.textColor || '#FFFFFF'
                      }}
                    >
                      <div className="text-left p-2">
                        <div className="font-bold text-lg">{ship.name}</div>
                        <div className="text-sm">{ship.class}</div>
                      </div>
                      <div className="absolute top-2 right-2 w-3 h-3 bg-white rounded-full opacity-70"></div>
                    </button>
                  ))}
                </div>
                
                <div className="space-y-4">
                  {shipClasses.slice(3).map((ship) => (
                    <button
                      key={ship.id}
                      onClick={() => handleShipSelect(ship.id)}
                      className={`w-full h-16 border-2 border-gray-400 transition-all duration-200 hover:brightness-110 relative ${
                        selectedShip === ship.id ? 'ring-2 ring-white' : ''
                      }`}
                      style={{ 
                        backgroundColor: ship.color,
                        color: ship.textColor || '#FFFFFF'
                      }}
                    >
                      <div className="text-left p-2">
                        <div className="font-bold text-lg">{ship.name}</div>
                        <div className="text-sm">{ship.class}</div>
                      </div>
                      <div className="absolute top-2 right-2 w-3 h-3 bg-white rounded-full opacity-70"></div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Central Activate Button */}
              <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2">
                <button
                  onClick={handleActivate}
                  disabled={!selectedShip}
                  className={`px-8 py-3 bg-blue-600 text-white font-bold text-lg border-2 border-gray-400 transition-all duration-200 relative ${
                    selectedShip 
                      ? 'hover:bg-blue-500 cursor-pointer' 
                      : 'opacity-50 cursor-not-allowed'
                  } ${
                    isActivated ? 'animate-pulse bg-green-500' : ''
                  }`}
                >
                  <div>ACTIVATE</div>
                  <div className="text-xs">INTERFACE</div>
                  <div className="absolute top-1 right-1 w-2 h-2 bg-white rounded-full opacity-70"></div>
                </button>
              </div>
            </div>

            {/* Right Panel - STD Button */}
            <div className="ml-6">
              <button
                className="w-16 h-16 bg-blue-600 text-white font-bold text-sm border-2 border-gray-400 transition-all duration-200 hover:brightness-110"
              >
                STD
              </button>
            </div>
          </div>

          {/* Status Display */}
          {selectedShip && (
            <div className="mt-4 p-3 bg-gray-800 border border-gray-400 text-green-400 font-mono text-sm">
              <div>SELECTED: {shipClasses.find(s => s.id === selectedShip)?.name} {shipClasses.find(s => s.id === selectedShip)?.class}</div>
              {selectedFaction && (
                <div>FACTION: {factions.find(f => f.id === selectedFaction)?.name}</div>
              )}
              {isActivated && (
                <div className="text-yellow-400 animate-pulse">{'>>> INTERFACE ACTIVATED <<<'}</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StarfleetInterface;
