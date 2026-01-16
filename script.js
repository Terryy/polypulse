const WHALE_DATA_URL = 'data/whales.json';

// --- CONFIGURATION ---
// Removed MINNOW. Lowest tier is now DOLPHIN ($1,000).
const TIERS = {
    BLUE_WHALE: { threshold: 50000, emoji: '🐋', name: 'BLUE WHALE', class: 'text-blue-600 bg-blue-100' },
    WHALE:      { threshold: 10000, emoji: '🐳', name: 'WHALE',      class: 'text-sky-500 bg-sky-50' },
    SHARK:      { threshold: 5000,  emoji: '🦈', name: 'SHARK',      class: 'text-teal-500 bg-teal-50' },
    DOLPHIN:    { threshold: 1000,  emoji: '🐬', name: 'DOLPHIN',    class: 'text-cyan-500 bg-cyan-50' }
};

function getWhaleTier(amountUSD) {
    if (amountUSD >= TIERS.BLUE_WHALE.threshold) return TIERS.BLUE_WHALE;
    if (amountUSD >= TIERS.WHALE.threshold)      return TIERS.WHALE;
    if (amountUSD >= TIERS.SHARK.threshold)      return TIERS.SHARK;
    if (amountUSD >= TIERS.DOLPHIN.threshold)    return TIERS.DOLPHIN;
    return null; // Return null if it's too small
}

async function fetchWhales() {
    const container = document.getElementById('whale-container');
    const status = document.getElementById('status-indicator');
    
    try {
        const response = await fetch(WHALE_DATA_URL);
        if (!response.ok) throw new Error("Data file not found");
        
        const trades = await response.json();
        
        container.innerHTML = '';
        status.innerHTML = '<span class="relative flex h-3 w-3 mr-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span></span> System Online';

        // Filter out small trades immediately
        const significantTrades = trades.filter(t => Math.abs(parseFloat(t.amountUSD)) >= 1000);

        if (significantTrades.length === 0) {
            container.innerHTML = '<div class="text-center text-gray-500 py-10">No significant trades (>$1k) detected.</div>';
            return;
        }

        significantTrades.forEach(trade => {
            const amountVal = parseFloat(trade.amountUSD);
            const amountStr = amountVal.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
            
            // Tier Logic
            const tier = getWhaleTier(Math.abs(amountVal));
            if (!tier) return; // Skip if null (extra safety)

            // Side Logic (YES vs NO)
            let sideText = "???";
            let badgeClass = "bg-gray-100 text-gray-600";

            if (trade.outcomeIndex == 0) {
                sideText = "YES";
                badgeClass = "bg-green-100 text-green-700 border border-green-200"; 
            } else if (trade.outcomeIndex == 1) {
                sideText = "NO";
                badgeClass = "bg-red-100 text-red-700 border border-red-200";   
            }

            const card = document.createElement('div');
            card.className = "bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow flex items-center justify-between animate-fade-in";
            
            card.innerHTML = `
                <div class="flex items-center space-x-4">
                    <div class="text-4xl" title="${tier.name}">${tier.emoji}</div>
                    <div>
                        <div class="text-sm font-bold text-gray-900 line-clamp-2">${trade.market.question}</div>
                        <div class="text-xs text-gray-500 mt-1 flex items-center space-x-2">
                            <span class="${tier.class} px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider border border-current opacity-80">${tier.name}</span>
                            <span>•</span>
                            <span>${new Date(trade.timestamp * 1000).toLocaleTimeString()}</span>
                        </div>
                    </div>
                </div>
                <div class="text-right min-w-[90px]">
                    <div class="text-lg font-black text-gray-800">${amountStr}</div>
                    <div class="text-xs font-black uppercase tracking-wider mt-1 px-3 py-1 rounded-md inline-block ${badgeClass}">
                        ${sideText}
                    </div>
                </div>
            `;
            container.appendChild(card);
        });

    } catch (error) {
        console.error(error);
        status.innerHTML = '<span class="h-3 w-3 rounded-full bg-red-500 mr-2"></span> Offline';
    }
}

fetchWhales();
setInterval(fetchWhales, 30000);
