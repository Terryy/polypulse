const WHALE_DATA_URL = 'data/whales.json';
const PAGE_SIZE = 50;
const TIERS = {
    BLUE_WHALE: { threshold: 50000, emoji: '🐋', name: 'BLUE WHALE', class: 'text-blue-600 bg-blue-100 border-blue-200' },
    WHALE:      { threshold: 10000, emoji: '🐳', name: 'WHALE',      class: 'text-sky-600 bg-sky-100 border-sky-200' },
    SHARK:      { threshold: 5000,  emoji: '🦈', name: 'SHARK',      class: 'text-teal-600 bg-teal-100 border-teal-200' },
    DOLPHIN:    { threshold: 1000,  emoji: '🐬', name: 'DOLPHIN',    class: 'text-cyan-600 bg-cyan-100 border-cyan-200' },
    PULSE:      { threshold: 100,   emoji: '🐟', name: 'PULSE',      class: 'text-slate-600 bg-slate-100 border-slate-200' }
};

let feedMeta = null;
let allTrades = [];
let filteredTrades = [];
let visibleCount = PAGE_SIZE;

function getWhaleTier(amountUSD) {
    if (amountUSD >= TIERS.BLUE_WHALE.threshold) return { key: 'BLUE_WHALE', ...TIERS.BLUE_WHALE };
    if (amountUSD >= TIERS.WHALE.threshold)      return { key: 'WHALE', ...TIERS.WHALE };
    if (amountUSD >= TIERS.SHARK.threshold)      return { key: 'SHARK', ...TIERS.SHARK };
    if (amountUSD >= TIERS.DOLPHIN.threshold)    return { key: 'DOLPHIN', ...TIERS.DOLPHIN };
    if (amountUSD >= TIERS.PULSE.threshold)      return { key: 'PULSE', ...TIERS.PULSE };
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

function getSelectedTierKeys() {
    return Array.from(document.querySelectorAll('.tier-filter:checked')).map(input => input.dataset.tier);
}

function getSelectedPeriodDays() {
    const value = document.getElementById('period-filter')?.value || '1';
    return value === 'all' ? null : Number(value);
}

function applyFilters(resetVisible = true) {
    const minTrade = Number(feedMeta?.min_trade_usd || TIERS.PULSE.threshold);
    const selectedTierKeys = new Set(getSelectedTierKeys());
    const periodDays = getSelectedPeriodDays();
    const cutoffSeconds = periodDays ? Math.floor(Date.now() / 1000) - (periodDays * 24 * 60 * 60) : null;

    filteredTrades = allTrades
        .map(trade => {
            const amountUSD = Math.abs(Number.parseFloat(trade.amountUSD) || 0);
            return { ...trade, amountUSDValue: amountUSD, tier: getWhaleTier(amountUSD) };
        })
        .filter(trade => trade.amountUSDValue >= minTrade)
        .filter(trade => trade.tier && selectedTierKeys.has(trade.tier.key))
        .filter(trade => !cutoffSeconds || Number(trade.timestamp || 0) >= cutoffSeconds)
        .sort((a, b) => Number(b.timestamp || 0) - Number(a.timestamp || 0));

    if (resetVisible) visibleCount = PAGE_SIZE;
    updateStats(filteredTrades);
    updateStatus(feedMeta, filteredTrades.length);
    renderFeed();
}

function updateStats(trades) {
    let totalVol = 0;
    let maxVol = 0;
    let buyCount = 0;

    trades.forEach(t => {
        const val = t.amountUSDValue ?? Math.abs(Number.parseFloat(t.amountUSD) || 0);
        totalVol += val;
        if (val > maxVol) maxVol = val;
        if (String(t.type || '').toUpperCase() === 'BUY') buyCount++;
    });

    document.getElementById('stat-volume').innerText = formatCurrency(totalVol);
    document.getElementById('stat-count').innerText = trades.length;
    document.getElementById('stat-max').innerText = formatCurrency(maxVol);

    const total = trades.length;
    const ratio = total > 0 ? Math.round((buyCount / total) * 100) : 0;
    const ratioEl = document.getElementById('stat-ratio');

    if (total === 0) {
        ratioEl.className = 'text-xl sm:text-2xl font-black text-slate-800 mt-1';
        ratioEl.innerText = '--';
    } else if (ratio >= 50) {
        ratioEl.className = 'text-xl sm:text-2xl font-black text-green-500 mt-1';
        ratioEl.innerHTML = `${ratio}% <span class="text-[10px] text-gray-400 font-bold uppercase ml-1">BUY</span>`;
    } else {
        ratioEl.className = 'text-xl sm:text-2xl font-black text-red-500 mt-1';
        ratioEl.innerHTML = `${ratio}% <span class="text-[10px] text-gray-400 font-bold uppercase ml-1">BUY</span>`;
    }
}

function setStatusHTML(html, title = '') {
    ['status-indicator', 'status-indicator-desktop'].forEach(id => {
        const status = document.getElementById(id);
        if (!status) return;
        status.innerHTML = html;
        if (title) {
            status.title = title;
        } else {
            status.removeAttribute('title');
        }
    });
}

function updateStatus(meta, tradeCount) {
    const checkedAt = formatCheckedTime(meta?.last_checked_at);
    const minTrade = meta?.min_trade_usd ? formatCurrency(meta.min_trade_usd) : '$100';
    const title = `Last checked ${checkedAt}. Minimum listing size: ${minTrade}.`;

    if (meta?.status === 'error') {
        setStatusHTML('<span class="h-3 w-3 rounded-full bg-red-500 mr-2"></span> Scanner Error');
        return;
    }

    if (tradeCount === 0) {
        setStatusHTML('<span class="h-3 w-3 rounded-full bg-sky-500 mr-2"></span> Online, no matches', title);
        return;
    }

    setStatusHTML('<span class="relative flex h-3 w-3 mr-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span></span> System Online', title);
}

function renderEmptyState(container, meta) {
    const checkedAt = formatCheckedTime(meta?.last_checked_at);
    const periodLabel = document.getElementById('period-filter')?.selectedOptions?.[0]?.textContent || 'selected period';
    const error = meta?.error ? `<p class="mt-2 text-[11px] text-red-500 font-mono break-words">${escapeHTML(meta.error)}</p>` : '';

    container.innerHTML = `
        <div class="bg-white border border-slate-200 rounded-xl p-6 text-center shadow-sm animate-fade-in">
            <div class="text-sm font-black text-slate-800 uppercase tracking-wide">No matching trades</div>
            <p class="text-sm text-slate-500 mt-2">Last checked ${escapeHTML(checkedAt)}. Try widening the period or enabling more tiers.</p>
            <p class="text-[11px] text-slate-400 mt-2 uppercase tracking-wide">Current period: ${escapeHTML(periodLabel)}</p>
            ${error}
        </div>
    `;
}

function renderTrade(container, trade) {
    const amountVal = trade.amountUSDValue ?? Math.abs(Number.parseFloat(trade.amountUSD) || 0);
    const amountStr = formatCurrency(amountVal);
    const timeStr = new Date(Number(trade.timestamp) * 1000).toLocaleString();
    const userId = trade.user?.id || '0x00';
    const shortUser = userId.length > 8 ? `${userId.substring(0, 4)}...${userId.substring(userId.length - 4)}` : userId;
    const profileUrl = `https://polymarket.com/profile/${encodeURIComponent(userId)}`;
    const question = trade.market?.question || 'Unknown Market';
    const tier = trade.tier || getWhaleTier(amountVal);

    if (!tier) return;

    const tradeSide = String(trade.type || 'TRADE').toUpperCase();
    const outcome = trade.outcome || (Number(trade.outcomeIndex) === 0 ? 'Outcome 1' : 'Outcome 2');
    const sideText = `${tradeSide} ${outcome}`;
    const badgeClass = tradeSide === 'SELL'
        ? 'bg-red-100 text-red-700 border-red-200'
        : 'bg-green-100 text-green-700 border-green-200';

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
            <div class="text-right pl-4 border-l border-gray-50 min-w-[100px] max-w-[150px]">
                <div class="text-lg font-black text-gray-800 tracking-tight">${amountStr}</div>
                <div class="text-[10px] font-bold uppercase tracking-widest mt-1 px-2 py-1 rounded inline-block border ${badgeClass}">
                    ${escapeHTML(sideText)}
                </div>
            </div>
        </div>
    `;
    container.appendChild(card);
}

function renderFeed() {
    const container = document.getElementById('whale-container');
    const loadMore = document.getElementById('load-more');
    const summary = document.getElementById('result-summary');
    const visibleTrades = filteredTrades.slice(0, visibleCount);

    container.innerHTML = '';

    if (filteredTrades.length === 0) {
        renderEmptyState(container, feedMeta);
    } else {
        visibleTrades.forEach(trade => renderTrade(container, trade));
    }

    if (summary) {
        const showing = Math.min(visibleCount, filteredTrades.length);
        summary.innerText = filteredTrades.length ? `Showing ${showing} of ${filteredTrades.length}` : 'Showing 0';
    }

    if (loadMore) {
        loadMore.classList.toggle('hidden', visibleCount >= filteredTrades.length);
    }
}

async function fetchWhales() {
    try {
        const response = await fetch(`${WHALE_DATA_URL}?t=${Date.now()}`);
        if (!response.ok) throw new Error('Data file not found');

        const payload = await response.json();
        const normalized = normalizePayload(payload);
        feedMeta = normalized.meta;
        allTrades = normalized.trades;
        applyFilters(false);
    } catch (error) {
        console.error(error);
        updateStats([]);
        setStatusHTML('<span class="h-3 w-3 rounded-full bg-red-500 mr-2"></span> Offline');
        filteredTrades = [];
        renderEmptyState(document.getElementById('whale-container'), { status: 'error', error: error.message });
    }
}

function bindIntroToggle() {
    const button = document.getElementById('intro-toggle');
    const panel = document.getElementById('intro-more');
    if (!button || !panel) return;

    button.addEventListener('click', () => {
        const isOpen = !panel.classList.contains('hidden');
        panel.classList.toggle('hidden', isOpen);
        button.innerText = isOpen ? 'Show more' : 'Show less';
        button.setAttribute('aria-expanded', String(!isOpen));
    });
}

function bindControls() {
    bindIntroToggle();
    document.getElementById('period-filter')?.addEventListener('change', () => applyFilters(true));
    document.querySelectorAll('.tier-filter').forEach(input => {
        input.addEventListener('change', () => applyFilters(true));
    });
    document.getElementById('load-more')?.addEventListener('click', () => {
        visibleCount += PAGE_SIZE;
        renderFeed();
    });
}

bindControls();
fetchWhales();
setInterval(fetchWhales, 30000);
