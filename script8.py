import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update elements in els object
old_els = '''    manualSilverPriceKg: document.getElementById('manual-silver-price-kg'),
    manualSilverPriceCay: document.getElementById('manual-silver-price-cay'),
    manualSilverPriceChi: document.getElementById('manual-silver-price-chi'),'''
new_els = '''    manualSilverPrice: document.getElementById('manual-silver-price'),
    silverPriceLabel: document.getElementById('silver-price-label'),
    selectedSilverTotalDisplay: document.getElementById('selected-silver-total-display'),
    selectedSilverSum: document.getElementById('selected-silver-sum'),
    selectedSilverConverted: document.getElementById('selected-silver-converted'),
    silverSummaryUnitName: document.getElementById('silver-summary-unit-name'),
    selectedSilverPrice: document.getElementById('selected-silver-price'),
    selectedSilverTotalMoney: document.getElementById('selected-silver-total-money'),'''

js = js.replace(old_els, new_els)

# 2. Update renderAssets to populate manualSilverPrice
old_render = '''    if (els.totalSilverCost) {
        els.totalSilverCost.textContent = formatCurrency(totalSilverCost);
    }'''
new_render = '''    if (els.totalSilverCost) {
        els.totalSilverCost.textContent = formatCurrency(totalSilverCost);
    }
    if (els.manualSilverPrice && state.assets.manualSilverPrice > 0) {
        els.manualSilverPrice.value = new Intl.NumberFormat('vi-VN').format(state.assets.manualSilverPrice);
    }'''
js = js.replace(old_render, new_render)

# 3. Update the save price button logic
old_save_price = '''    if (els.btnSaveSilverPrice) {
        els.btnSaveSilverPrice.addEventListener('click', () => {
            const kg = parseInt(els.manualSilverPriceKg.value.replace(/\\D/g, '')) || 0;
            const cay = parseInt(els.manualSilverPriceCay.value.replace(/\\D/g, '')) || 0;
            const chi = parseInt(els.manualSilverPriceChi.value.replace(/\\D/g, '')) || 0;
            
            state.assets.manualSilverPrices = { kg, cay, chi };
            saveData();
            showToast('Đã lưu bộ giá Bạc thành công!', 'success');
            if (typeof renderAssets === 'function') renderAssets();
        });
    }'''
new_save_price = '''    if (els.btnSaveSilverPrice) {
        els.btnSaveSilverPrice.addEventListener('click', () => {
            const price = parseInt(els.manualSilverPrice.value.replace(/\\D/g, '')) || 0;
            state.assets.manualSilverPrice = price;
            saveData();
            showToast('Đã lưu giá Bạc thành công!', 'success');
            if (typeof renderAssets === 'function') renderAssets();
            
            // Re-format the input right away
            if (price > 0) {
                els.manualSilverPrice.value = new Intl.NumberFormat('vi-VN').format(price);
            }
        });
    }
    if (els.manualSilverPrice) {
        els.manualSilverPrice.addEventListener('input', function (e) {
            let value = e.target.value.replace(/[^0-9]/g, '');
            if (value !== '') {
                e.target.value = new Intl.NumberFormat('vi-VN').format(parseInt(value));
            }
        });
    }'''
js = js.replace(old_save_price, new_save_price)

# 4. Update the unit change logic for Silver
old_unit_change = '''    if (els.silverUnitSelect) {
        els.silverUnitSelect.addEventListener('change', () => {
            updateSilverAmountFromTicks();
        });
    }'''
new_unit_change = '''    if (els.silverUnitSelect) {
        els.silverUnitSelect.addEventListener('change', () => {
            const unitValue = els.silverUnitSelect.value;
            const unitName = unitValue === 'kg' ? 'Kg' : (unitValue === 'cay' ? 'Lượng' : 'Chỉ');
            if (els.silverPriceLabel) {
                els.silverPriceLabel.innerHTML = `<i class="ph ph-tag"></i> Giá bạc (VND / ${unitName})`;
            }
            if (els.silverSummaryUnitName) {
                els.silverSummaryUnitName.textContent = unitName;
            }
            updateSilverAmountFromTicks();
        });
    }'''
js = js.replace(old_unit_change, new_unit_change)

# 5. Update updateSilverAmountFromTicks to show the green summary box
old_update_silver = '''    if (els.silverAmountInput) {
        els.silverAmountInput.value = finalAmount > 0 ? finalAmount.toFixed(3).replace(/\\.?0+$/, '') : 0;
    }
    
    state.assets.silverAmount = finalAmount;
    state.assets.silverUnit = targetUnit;
    saveData();'''
new_update_silver = '''    if (els.silverAmountInput) {
        els.silverAmountInput.value = finalAmount > 0 ? finalAmount.toFixed(3).replace(/\\.?0+$/, '') : 0;
    }
    
    state.assets.silverAmount = finalAmount;
    state.assets.silverUnit = targetUnit;
    
    // Update summary box
    if (els.selectedSilverTotalDisplay) {
        if (totalInChi > 0) {
            els.selectedSilverTotalDisplay.style.display = 'block';
            
            const chiStr = totalInChi.toFixed(3).replace(/\\.?0+$/, '');
            if (els.selectedSilverSum) els.selectedSilverSum.textContent = `${chiStr} Chỉ`;
            
            let unitStr = (targetUnit === 'kg' ? 'Kg' : (targetUnit === 'cay' ? 'Lượng' : 'Chỉ'));
            let convertedStr = finalAmount.toFixed(3).replace(/\\.?0+$/, '') + ' ' + unitStr;
            if (els.selectedSilverConverted) els.selectedSilverConverted.textContent = convertedStr;
            
            const currentPrice = state.assets.manualSilverPrice || 0;
            if (els.selectedSilverPrice) els.selectedSilverPrice.textContent = formatCurrency(currentPrice);
            
            const totalMoney = finalAmount * currentPrice;
            if (els.selectedSilverTotalMoney) els.selectedSilverTotalMoney.textContent = formatCurrency(totalMoney);
        } else {
            els.selectedSilverTotalDisplay.style.display = 'none';
        }
    }
    
    saveData();'''
js = js.replace(old_update_silver, new_update_silver)

# 6. Update renderSilverPurchases row profit calculation
old_row_profit = '''        // Calculate difference for this specific row based on its unit
        let profitDisplay = '-';
        let profitColor = 'var(--text-muted)';
        const currentPrice = state.assets.manualSilverPrices ? (state.assets.manualSilverPrices[p.unit] || 0) : 0;
        
        if (currentPrice > 0 && p.cost) {
            const currentValue = p.amount * currentPrice;
            const profit = currentValue - p.cost;
            profitDisplay = (profit >= 0 ? '+' : '') + formatCurrency(profit);
            profitColor = profit >= 0 ? 'var(--success)' : 'var(--danger)';
        }'''
        
new_row_profit = '''        // Calculate difference for this specific row based on standard reference price
        let profitDisplay = '-';
        let profitColor = 'var(--text-muted)';
        const currentPrice = state.assets.manualSilverPrice || 0;
        
        if (currentPrice > 0 && p.cost) {
            // Need to convert this row's amount into the currently selected TARGET unit to multiply with price
            const targetUnit = state.assets.silverUnit || 'chi';
            let amountInChi = (p.unit === 'kg') ? p.amount * 266.6667 : (p.unit === 'cay' ? p.amount * 10 : p.amount);
            
            let amountInTarget = amountInChi;
            if (targetUnit === 'cay') amountInTarget = amountInChi / 10;
            else if (targetUnit === 'kg') amountInTarget = amountInChi / 266.6667;
            
            const currentValue = amountInTarget * currentPrice;
            const profit = currentValue - p.cost;
            profitDisplay = (profit >= 0 ? '+' : '') + formatCurrency(profit);
            profitColor = profit >= 0 ? 'var(--success)' : 'var(--danger)';
        }'''
js = js.replace(old_row_profit, new_row_profit)

# 7. Update silverProfitLoss in renderSilverPurchases
old_total_profit = '''        if (currentPrice > 0) {
            // ... wait we didn't calculate total profit here? 
            // Oh, we just didn't calculate it in renderSilverPurchases?
            // Actually let's just make sure the initial rendering sets up the labels correctly
        }'''
        
# 8. Let's fix the initial label on page load
old_init = '''const init = async () => {
    await loadData();
    setupEventListeners();'''
new_init = '''const init = async () => {
    await loadData();
    setupEventListeners();
    
    // Set initial label for silver
    if (els.silverUnitSelect && els.silverPriceLabel) {
        const unitValue = els.silverUnitSelect.value;
        const unitName = unitValue === 'kg' ? 'Kg' : (unitValue === 'cay' ? 'Lượng' : 'Chỉ');
        els.silverPriceLabel.innerHTML = `<i class="ph ph-tag"></i> Giá bạc (VND / ${unitName})`;
        if (els.silverSummaryUnitName) els.silverSummaryUnitName.textContent = unitName;
    }
'''
js = js.replace(old_init, new_init)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('Success script 8 app.js')
