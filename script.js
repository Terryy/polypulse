const WHALE_DATA_URL = 'data/whales.json';

// --- CONFIGURATION: TIER DEFINITIONS ---
const TIERS = {
    BLUE_WHALE: { threshold: 50000, emoji: '🐋', name: 'BLUE WHALE', class: 'text-blue-600 bg-blue-100' },
    WHALE:      { threshold: 10000, emoji: '🐳', name: 'WHALE',      class: 'text-sky-500 bg-sky-50' },
    SHARK:      { threshold: 5000,  emoji: '🦈', name: 'SHARK',      class: 'text-teal-500 bg-teal-50' },
    DOLPHIN:    { threshold: 1000,  emoji: '🐬', name: 'DOLPHIN',    class: 'text-cyan-500 bg-cyan-50' },
    MINNOW:     { threshold: 0,     emoji: '🐟', name: 'MINNOW',     class: 'text-gray-400 bg-gray-50' }
};

function getWhaleTier(amountUSD) {
    if (amountUSD >= TIERS.BLUE_WHALE.threshold) return TIERS.BLUE_WHALE;
    if (amountUSD >= TIERS.WHALE.threshold)      return TIERS.WHALE;
    if (amountUSD >= TIERS.SHARK.threshold)      return TIERS.SHARK;
    if (amountUSD >= TIERS.DOLPHIN.threshold)    return TIERS.DOLPHIN;
    return TIERS.MINNOW;
}

async function fetchWhales() {
    const container = document.getElementById('whale-container');
    const status = document.getElementById('status-indicator');
    
    try {
        const response = await fetch(WHALE_DATA_URL);
        if (!response.ok) throw new Error("Data file not found");
        
        const trades = await response.json();
        
        // Clear "Scanning..." message
        container.innerHTML = '';
        status.innerHTML = '<span class="relative flex h-3 w-3 mr-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span></span> System Online';

        if (trades.length === 0) {
            container.innerHTML = '<div class="text-center text-gray-500 py-10">No whales detected in the last cycle. Ocean is quiet. 🌊</div>';
            return;
        }

        trades.forEach(trade => {
            const amount = parseFloat(trade.amountUSD).toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
            const tier = getWhaleTier(parseFloat(trade.amountUSD));
            
            // Determine Sentiment (Bullish/Bearish)
            const isBuy = trade.amount > 0; // Simplified logic, assumes positive amount is buy
            // You can refine "side" logic if your API provides it explicitly
            
            const card = document.createElement('div');
            card.className = "bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow flex items-center justify-between animate-fade-in";
            
            card.innerHTML = `
                <div class="flex items-center space-x-4">
                    <div class="text-4xl" title="${tier.name}">${tier.emoji}</div>
                    <div>
                        <div class="text-sm font-bold text-gray-900">${trade.market.question}</div>
                        <div class="text-xs text-gray-500 mt-1">
                            <span class="${tier.class} px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider border border-current opacity-80">${tier.name}</span>
                            <span class="mx-1">•</span>
                            ${new Date(trade.timestamp * 1000).toLocaleTimeString()}
                        </div>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-lg font-black text-gray-800">${amount}</div>
                    <div class="text-xs font-medium ${isBuy ? 'text-green-500' : 'text-red-500'} uppercase tracking-wide">
                        ${isBuy ? 'Accumulating' : 'Dumping'}
                    </div>
                </div>
            `;
            container.appendChild(card);
        });

    } catch (error) {
        console.error(error);
        status.innerHTML = '<span class="h-3 w-3 rounded-full bg-red-500 mr-2"></span> Offline';
        container.innerHTML = `<div class="text-center text-red-400 py-10">
            Unable to read whale data. <br>
            <span class="text-sm text-gray-400">Make sure backend/main.py has run successfully.</span>
        </div>`;
    }
}

// Auto-refresh every 30 seconds
fetchWhales();
setInterval(fetchWhales, 30000);
