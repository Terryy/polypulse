const WHALE_DATA_URL = 'data/whales.json';

// --- CONFIGURATION ---
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
    return null; 
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

        // Filter out small trades
        const significantTrades = trades.filter(t => Math.abs(parseFloat(t.amountUSD)) >= 1000);

        if (significantTrades.length === 0) {
            container.innerHTML = '<div class="text-center text-gray-500 py-10">No significant trades (>$1k) detected.</div>';
            return;
        }

        significantTrades.forEach(trade => {
            const amountVal = parseFloat(trade.amountUSD);
            const amountStr = amountVal.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
            const timeStr = new Date(trade.timestamp * 1000).toLocaleString(); // Date & Time
            
            const tier = getWhaleTier(Math.abs(amountVal));
            if (!tier) return; 

            // Logic: 0 = YES, 1 = NO
            let sideText = "UNKNOWN";
            let badgeClass = "bg-gray-100 text-gray-600";

            if (trade.outcomeIndex == 0) {
                sideText = "BET YES";
                badgeClass = "bg-green-100 text-green-700 border border-green-200"; 
            } else if (trade.outcomeIndex == 1) {
                sideText = "BET NO";
                badgeClass = "bg-red-100 text-red-700 border border-red-200";   
            }

            const card = document.createElement('div');
            card.className = "bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow animate-fade-in";
            
            // New Layout: Time on top
            card.innerHTML = `
                <div class="text-[10px] text-gray-400 font-mono mb-2 uppercase tracking-wide border-b border-gray-50 pb-1">
                    ${timeStr}
                </div>
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="text-3xl" title="${tier.name}">${tier.emoji}</div>
                        <div>
                            <div class="text-sm font-bold text-gray-900 leading-tight">${trade.market.question}</div>
                            <div class="mt-1">
                                <span class="${tier.class} px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider border border-current opacity-80">${tier.name}</span>
                            </div>
                        </div>
                    </div>
                    <div class="text-right min-w-[90px] pl-2">
                        <div class="text-lg font-black text-gray-800">${amountStr}</div>
                        <div class="text-xs font-black uppercase tracking-wider mt-1 px-3 py-1 rounded-md inline-block ${badgeClass}">
                            ${sideText}
                        </div>
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
