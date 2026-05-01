const WHALE_DATA_URL = 'data/whales.json';
const TIERS = {
    BLUE_WHALE: { threshold: 50000, emoji: '🐋', name: 'BLUE WHALE', class: 'text-blue-600 bg-blue-100 border-blue-200' },
    WHALE:      { threshold: 10000, emoji: '🐳', name: 'WHALE',      class: 'text-sky-600 bg-sky-100 border-sky-200' },
    SHARK:      { threshold: 5000,  emoji: '🦈', name: 'SHARK',      class: 'text-teal-600 bg-teal-100 border-teal-200' },
    DOLPHIN:    { threshold: 1000,  emoji: '🐬', name: 'DOLPHIN',    class: 'text-cyan-600 bg-cyan-100 border-cyan-200' },
    PULSE:      { threshold: 100,   emoji: '•',  name: 'PULSE',      class: 'text-slate-600 bg-slate-100 border-slate-200' }
};

function getWhaleTier(amountUSD) {
    if (amountUSD >= TIERS.BLUE_WHALE.threshold) return TIERS.BLUE_WHALE;
    if (amountUSD >= TIERS.WHALE.threshold)      return TIERS.WHALE;
    if (amountUSD >= TIERS.SHARK.threshold)      return TIERS.SHARK;
    if (amountUSD >= TIERS.DOLPHIN.threshold)    return TIERS.DOLPHIN;
    if (amountUSD >= TIERS.PULSE.threshold)      return TIERS.PULSE;
    return null;
}

function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (char) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
    }[char]));
}

function formatCurrency(value) {
    const number = Number.parseFloat(value) || 0;
    return number.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function formatCheckedTime(value) {
    if (!value) return 'never';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return 'unknown';
    return date.toLocaleString();
}

function normalizePayload(payload) {
    if (Array.isArray(payload)) {
        return { meta: null, trades: payload };
    }

    return {
        meta: payload?.meta || null,
        trades: Array.isArray(payload?.trades) ? payload.trades : []
    };
}

function updateStats(trades) {
    let totalVol = 0;
    let maxVol = 0;
    let yesCount = 0;

    trades.forEach(t => {
        const val = Math.abs(Number.parseFloat(t.amountUSD) || 0);
        totalVol += val;
        if (val > maxVol) maxVol = val;
        if (Number(t.outcomeIndex) === 0) yesCount++;
    });

    document.getElementById('stat-volume').innerText = formatCurrency(totalVol);
    document.getElementById('stat-count').innerText = trades.length;
    document.getElementById('stat-max').innerText = formatCurrency(maxVol);

    const total = trades.length;
    const ratio = total > 0 ? Math.round((yesCount / total) * 100) : 0;
    const ratioEl = document.getElementById('stat-ratio');

    if (total === 0) {
        ratioEl.className = 'text-xl sm:text-2xl font-black text-slate-800 mt-1';
        ratioEl.innerText = '--';
    } else if (ratio >= 50) {
        ratioEl.className = 'text-xl sm:text-2xl font-black text-green-500 mt-1';
        ratioEl.innerHTML = `${ratio}% <span class="text-[10px] text-gray-400 font-bold uppercase ml-1">YES</span>`;
    } else {
        ratioEl.className = 'text-xl sm:text-2xl font-black text-red-500 mt-1';
        ratioEl.innerHTML = `${ratio}% <span class="text-[10px] text-gray-400 font-bold uppercase ml-1">NO</span>`;
    }
}

function updateStatus(meta, tradeCount) {
    const status = document.getElementById('status-indicator');
    const checkedAt = formatCheckedTime(meta?.last_checked_at);
    const minTrade = meta?.min_trade_usd ? formatCurrency(meta.min_trade_usd) : '$100';

    if (meta?.status === 'error') {
        status.innerHTML = '<span class="h-3 w-3 rounded-full bg-red-500 mr-2"></span> Scanner Error';
        return;
    }

    if (tradeCount === 0) {
        status.innerHTML = '<span class="h-3 w-3 rounded-full bg-sky-500 mr-2"></span> Online, no matches';
        status.title = `Last checked ${checkedAt}. Minimum listing size: ${minTrade}.`;
        return;
    }

    status.innerHTML = '<span class="relative flex h-3 w-3 mr-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span></span> System Online';
    status.title = `Last checked ${checkedAt}. Minimum listing size: ${minTrade}.`;
}

function renderEmptyState(container, meta) {
    const checkedAt = formatCheckedTime(meta?.last_checked_at);
    const minTrade = meta?.min_trade_usd ? formatCurrency(meta.min_trade_usd) : '$100';
    const lookback = meta?.lookback_hours || 24;
    const error = meta?.error ? `<p class="mt-2 text-[11px] text-red-500 font-mono break-words">${escapeHTML(meta.error)}</p>` : '';

    container.innerHTML = `
        <div class="bg-white border border-slate-200 rounded-xl p-6 text-center shadow-sm animate-fade-in">
            <div class="text-sm font-black text-slate-800 uppercase tracking-wide">Scanner is running</div>
            <p class="text-sm text-slate-500 mt-2">Last checked ${escapeHTML(checkedAt)}. No trades above ${escapeHTML(minTrade)} were found in the last ${escapeHTML(lookback)} hours.</p>
            ${error}
        </div>
    `;
}

function renderTrade(container, trade) {
    const amountVal = Math.abs(Number.parseFloat(trade.amountUSD) || 0);
    const amountStr = formatCurrency(amountVal);
    const timeStr = new Date(Number(trade.timestamp) * 1000).toLocaleString();
    const userId = trade.user?.id || '0x00';
    const shortUser = userId.length > 8 ? `${userId.substring(0, 4)}...${userId.substring(userId.length - 4)}` : userId;
    const profileUrl = `https://polymarket.com/profile/${encodeURIComponent(userId)}`;
    const question = trade.market?.question || 'Unknown Market';
    const tier = getWhaleTier(amountVal);

    if (!tier) return;

    let sideText = 'BET YES';
    let badgeClass = 'bg-green-100 text-green-700 border-green-200';

    if (Number(trade.outcomeIndex) === 1) {
        sideText = 'BET NO';
        badgeClass = 'bg-red-100 text-red-700 border-red-200';
    }

    const card = document.createElement('div');
    card.className = 'bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow animate-fade-in';
    card.innerHTML = `
        <div class="flex justify-between items-center mb-3 border-b border-gray-50 pb-2 gap-3">
            <div class="text-[10px] text-gray-400 font-mono uppercase tracking-wide flex items-center">
                <span class="mr-2">⏰</span> ${escapeHTML(timeStr)}
            </div>
            <a href="${profileUrl}" target="_blank" rel="noopener noreferrer" class="text-[10px] text-blue-400 hover:text-blue-600 font-mono flex items-center transition-colors">
                ${escapeHTML(shortUser)} <span class="ml-1">↗</span>
            </a>
        </div>
        <div class="flex items-center justify-between gap-4">
            <div class="flex items-center space-x-4 min-w-0">
                <div class="text-4xl filter drop-shadow-sm" title="${escapeHTML(tier.name)}">${tier.emoji}</div>
                <div class="min-w-0">
                    <div class="text-sm font-bold text-gray-900 leading-tight line-clamp-2 max-w-[200px] sm:max-w-md">
                        ${escapeHTML(question)}
                    </div>
                    <div class="mt-1.5 flex items-center space-x-2">
                        <span class="${tier.class} px-2 py-0.5 rounded text-[10px] font-bold tracking-wider border opacity-90">
                            ${escapeHTML(tier.name)}
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
}

async function fetchWhales() {
    const container = document.getElementById('whale-container');
    const status = document.getElementById('status-indicator');

    try {
        const response = await fetch(`${WHALE_DATA_URL}?t=${Date.now()}`);
        if (!response.ok) throw new Error('Data file not found');

        const payload = await response.json();
        const { meta, trades } = normalizePayload(payload);
        const minTrade = Number(meta?.min_trade_usd || TIERS.PULSE.threshold);
        const significantTrades = trades
            .filter(t => Math.abs(Number.parseFloat(t.amountUSD) || 0) >= minTrade)
            .sort((a, b) => Number(b.timestamp || 0) - Number(a.timestamp || 0));

        updateStats(significantTrades);
        updateStatus(meta, significantTrades.length);

        container.innerHTML = '';
        if (significantTrades.length === 0) {
            renderEmptyState(container, meta);
            return;
        }

        significantTrades.forEach(trade => renderTrade(container, trade));
    } catch (error) {
        console.error(error);
        updateStats([]);
        status.innerHTML = '<span class="h-3 w-3 rounded-full bg-red-500 mr-2"></span> Offline';
        renderEmptyState(container, { status: 'error', error: error.message });
    }
}

fetchWhales();
setInterval(fetchWhales, 30000);
