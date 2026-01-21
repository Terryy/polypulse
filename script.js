const WHALE_DATA_URL = 'data/whales.json';

const TIERS = {
    BLUE_WHALE: { threshold: 50000, emoji: '🐋', name: 'BLUE WHALE', class: 'text-blue-600 bg-blue-100 border-blue-200' },
    WHALE:      { threshold: 10000, emoji: '🐳', name: 'WHALE',      class: 'text-sky-600 bg-sky-100 border-sky-200' },
    SHARK:      { threshold: 5000,  emoji: '🦈', name: 'SHARK',      class: 'text-teal-600 bg-teal-100 border-teal-200' },
    DOLPHIN:    { threshold: 1000,  emoji: '🐬', name: 'DOLPHIN',    class: 'text-cyan-600 bg-cyan-100 border-cyan-200' }
};

function getWhaleTier(amountUSD) {
    if (amountUSD >= TIERS.BLUE_WHALE.threshold) return TIERS.BLUE_WHALE;
    if (amountUSD >= TIERS.WHALE.threshold)      return TIERS.WHALE;
    if (amountUSD >= TIERS.SHARK.threshold)      return TIERS.SHARK;
    if (amountUSD >= TIERS.DOLPHIN.threshold)    return TIERS.DOLPHIN;
    return null; 
}

// --- NEW FUNCTION: Updates the HUD Stats ---
function updateStats(trades) {
    let totalVol = 0;
    let maxVol = 0;
    let buyCount = 0; // "Buy" means OutcomeIndex 0 (YES) for simplicity

    trades.forEach(t => {
        const val = parseFloat(t.amountUSD);
        totalVol += val;
        if (val > maxVol) maxVol = val;
        
        // Basic sentiment logic: Index 0 is often "Yes/Long"
        if (t.outcomeIndex == 0) buyCount++; 
    });

    // 1. Update Volume
    document.getElementById('stat-volume').innerText = 
        totalVol.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
    
    // 2. Update Count
    document.getElementById('stat-count').innerText = trades.length;
    
    // 3. Update Largest Bet
    document.getElementById('stat-max').innerText = 
        maxVol.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });

    // 4. Update Buy Pressure
    const total = trades.length;
    const ratio = total > 0 ? Math.round((buyCount / total) * 100) : 0;
    
    const ratioEl = document.getElementById('stat-ratio');
    
    if (total === 0) {
        ratioEl.innerText = "--";
    } else if (ratio >= 50) {
        ratioEl.className = "text-xl sm:text-2xl font-black text-green-500 mt-1";
        ratioEl.innerHTML = `${ratio}% <span class="text-[10px] text-gray-400 font-bold uppercase ml-1">BULLISH</span>`;
    } else {
        ratioEl.className = "text-xl sm:text-2xl font-black text-red-500 mt-1";
        ratioEl.innerHTML = `${ratio}% <span class="text-[10px] text-gray-400 font-bold uppercase ml-1">BEARISH</span>`;
    }
}

async function fetchWhales() {
    const container = document.getElementById('whale-container');
    const status = document.getElementById('status-indicator');
    
    try {
        // Cache Buster
        const response = await fetch(`${WHALE_DATA_URL}?t=${Date.now()}`);
        if (!response.ok) throw new Error("Data file not found");
        
        const trades = await response.json();
        
        container.innerHTML = '';
        status.innerHTML = '<span class="relative flex h-3 w-3 mr-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span></span> System Online';

        const significantTrades = trades.filter(t => Math.abs(parseFloat(t.amountUSD)) >= 1000);

        // --- UPDATE STATS BAR ---
        updateStats(significantTrades);

        if (significantTrades.length === 0) {
            container.innerHTML = '<div class="text-center text-gray-400 py-12 bg-white rounded-xl border border-dashed border-gray-200">📭 No significant trades detected recently.</div>';
            return;
        }

        significantTrades.forEach(trade => {
            const amountVal = parseFloat(trade.amountUSD);
            const amountStr = amountVal.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
            const timeStr = new Date(trade.timestamp * 1000).toLocaleString(); 
            
            const userId = trade.user ? trade.user.id : "0x00";
            const shortUser = `${userId.substring(0, 4)}...${userId.substring(userId.length - 4)}`;
            const profileUrl = `https://polymarket.com/profile/${userId}`;

            const tier = getWhaleTier(Math.abs(amountVal));
            if (!tier) return; 

            // Logic for Badges: Index 0 = YES, Index 1 = NO
            let sideText = "BET YES";
            let badgeClass = "bg-green-100 text-green-700 border-green-200"; 
            
            if (trade.outcomeIndex == 1) {
                sideText = "BET NO";
                badgeClass = "bg-red-100 text-red-700 border-red-200";   
            }

            const card = document.createElement('div');
            card.className = "bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow animate-fade-in";
            
            card.innerHTML = `
                <div class="flex justify-between items-center mb-3 border-b border-gray-50 pb-2">
                    <div class="text-[10px] text-gray-400 font-mono uppercase tracking-wide flex items-center">
                        <span class="mr-2">⏰</span> ${timeStr}
                    </div>
                    <a href="${profileUrl}" target="_blank" class="text-[10px] text-blue-400 hover:text-blue-600 font-mono flex items-center transition-colors">
                        ${shortUser} <span class="ml-1">↗</span>
                    </a>
                </div>
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <div class="text-4xl filter drop-shadow-sm" title="${tier.name}">${tier.emoji}</div>
                        <div>
                            <div class="text-sm font-bold text-gray-900 leading-tight line-clamp-2 max-w-[200px] sm:max-w-md">
                                ${trade.market.question}
                            </div>
                            <div class="mt-1.5 flex items-center space-x-2">
                                <span class="${tier.class} px-2 py-0.5 rounded text-[10px] font-bold tracking-wider border opacity-90">
                                    ${tier.name}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="text-right pl-4 border-l border-gray-50 min-w-[100px]">
                        <div class="text-lg font-black text-gray-800 tracking-tight">${amountStr}</div>
                        <div class="text-[10px] font-bold uppercase tracking-widest mt-1 px-2 py-1 rounded inline-block border ${badgeClass}">
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
