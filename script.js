/* --- SHARED UTILITY FUNCTIONS --- */

function toggleText() {
    const moreText = document.getElementById("more-text");
    const btn = document.getElementById("toggle-btn");
    if (moreText.classList.contains("hidden")) {
        moreText.classList.remove("hidden");
        btn.innerText = "Show less";
    } else {
        moreText.classList.add("hidden");
        btn.innerText = "Show more";
    }
}

function formatSmartDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function showEmptyState() {
    document.getElementById('dashboard-grid').innerHTML = `
        <div class="col-span-full text-center py-12 bg-slate-900/30 border border-slate-800/50 rounded-xl border-dashed">
            <p class="text-slate-400 font-bold">Ocean is Quiet</p>
            <p class="text-xs text-slate-600 mt-1">No trades found above the current threshold.</p>
        </div>`;
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

async function loadData(url) {
    try {
        const response = await fetch(`${url}?t=${new Date().getTime()}`);
        if (!response.ok) throw new Error("Data missing");
        const data = await response.json();
        
        if (data.length === 0) showEmptyState();
        else renderCards(data);
        
        document.getElementById('last-updated').innerText = `Updated: ${new Date().toLocaleTimeString()}`;
    } catch (error) {
        console.error(error);
        showEmptyState();
    }
}

// --- CORE RENDERING LOGIC ---
function renderCards(whales) {
    const container = document.getElementById('dashboard-grid');
    container.innerHTML = ''; 
    whales.sort((a, b) => b.time - a.time);

    whales.forEach(whale => {
        const isYes = whale.outcome === 0;
        const isBuy = whale.side === 'BUY';
        const isBullish = (isBuy && isYes) || (!isBuy && !isYes);
        const color = isBullish ? 'emerald' : 'rose';

        // --- HIERARCHY & HIGHLIGHT LOGIC ---
        let levelColor = 'slate'; 
        let textHighlightClass = ''; 
        let iconSizeClass = 'text-2xl'; // Default icon size
        
        // Normalize Level Name (Map old names to new display if needed)
        let displayLevel = whale.level || 'MINNOW';
        if (displayLevel === 'LEVIATHAN' || displayLevel === 'MEGALODON') displayLevel = 'BLUE WHALE';

        // 1. DOLPHIN
        if (displayLevel === 'DOLPHIN') {
            levelColor = 'blue'; 
        }
        // 2. SHARK
        else if (displayLevel === 'SHARK') {
            levelColor = 'cyan';
        }
        // 3. WHALE (Standard)
        else if (displayLevel === 'WHALE') {
            levelColor = 'rose'; 
            textHighlightClass = 'effect-whale text-rose-500'; // Standard Flash
        }
        // 4. BLUE WHALE (Boss Tier)
        else if (displayLevel === 'BLUE WHALE') {
            levelColor = 'violet'; 
            textHighlightClass = 'effect-megalodon text-violet-400'; // Fast Intense Flash
            iconSizeClass = 'text-4xl'; // <--- MAKE ICON BIGGER
        }

        const timeString = formatSmartDate(whale.time);

        container.innerHTML += `
            <div class="group relative overflow-hidden rounded-xl bg-slate-900/80 backdrop-blur border border-slate-800 p-5 hover:border-${levelColor}-500/50 transition-all duration-300 shadow-xl flex flex-col justify-between">
                <div>
                    <div class="flex justify-between items-start mb-4 gap-2">
                        <div class="flex items-center gap-3 overflow-hidden">
                            <div class="w-12 h-12 shrink-0 rounded-lg bg-slate-800 flex items-center justify-center border border-slate-700 ${iconSizeClass}">
                                ${whale.icon}
                            </div>
                            <div class="min-w-0">
                                <div class="flex items-center gap-2 mb-1">
                                    <span class="text-[10px] tracking-wider uppercase px-2 py-0.5 rounded bg-${levelColor}-500/10 border border-${levelColor}-500/20 ${textHighlightClass ? textHighlightClass : `text-${levelColor}-400 font-bold`}">
                                        ${displayLevel}
                                    </span>
                                    <span class="text-xs text-slate-500 font-mono">${timeString}</span>
                                </div>
                                <h3 class="font-bold text-slate-100 text-sm leading-tight truncate" title="${whale.question}">
                                    ${whale.question}
                                </h3>
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3 mb-4">
                        <div class="bg-slate-950/50 p-3 rounded-lg border border-slate-800">
                            <p class="text-[10px] uppercase text-slate-500 mb-1 font-bold">Size (USD)</p>
                            <p class="text-lg font-mono font-bold text-white">$${whale.size_usd.toLocaleString()}</p>
                        </div>
                        <div class="bg-slate-950/50 p-3 rounded-lg border border-slate-800 relative overflow-hidden">
                            <div class="absolute top-0 right-0 w-8 h-8 bg-${color}-500/20 blur-xl rounded-full -mr-4 -mt-4"></div>
                            <p class="text-[10px] uppercase text-slate-500 mb-1 font-bold">Position</p>
                            <div class="flex items-center gap-1">
                                <span class="text-sm font-bold text-${color}-400">
                                    ${isBullish ? 'BULLISH' : 'BEARISH'}
                                </span>
                                <span class="text-xs text-slate-600">(${(whale.price * 100).toFixed(0)}¢)</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex items-center gap-2 pt-3 border-t border-slate-800/50">
                    <i data-lucide="wallet" class="w-3 h-3 text-slate-500"></i>
                    <span class="text-xs font-mono text-slate-400 truncate w-full" title="${whale.maker_address}">
                        ${whale.maker_address}
                    </span>
                    <a href="https://polymarket.com/profile/${whale.maker_address}" target="_blank" class="text-[10px] text-indigo-400 hover:text-indigo-300 hover:underline shrink-0">
                        Trace
                    </a>
                </div>
            </div>
        `;
    });
    
    if (typeof lucide !== 'undefined') lucide.createIcons();
}
