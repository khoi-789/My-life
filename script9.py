import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update totalAsset calculation in renderAssets
old_calc = '''    // 4. Grand Total
    const totalAsset = appBalance + bankSavings + goldValue;

    // Update UI
    els.totalAssetValue.textContent = formatCurrency(totalAsset);
    els.assetAppBalance.textContent = formatCurrency(appBalance);
    els.assetBankBalance.textContent = formatCurrency(bankSavings);
    els.assetGoldValue.textContent = formatCurrency(goldValue);'''
    
new_calc = '''    // Calculate Silver Value
    let totalSilverInTarget = 0;
    const silverAmt = state.assets.silverAmount || 0;
    const silverPrice = state.assets.manualSilverPrice || 0;
    const silverValue = silverAmt * silverPrice;

    // 4. Grand Total
    const totalAsset = appBalance + bankSavings + goldValue + silverValue;

    // Update UI
    els.totalAssetValue.textContent = formatCurrency(totalAsset);
    els.assetAppBalance.textContent = formatCurrency(appBalance);
    els.assetBankBalance.textContent = formatCurrency(bankSavings);
    els.assetGoldValue.textContent = formatCurrency(goldValue);
    
    // Add silver asset row dynamically if it exists (or just rely on the new UI)
    let silverAssetRow = document.getElementById('asset-silver-value-row');
    if (!silverAssetRow && document.querySelector('.assets-summary-list')) {
        const list = document.querySelector('.assets-summary-list');
        const row = document.createElement('div');
        row.id = 'asset-silver-value-row';
        row.className = 'summary-item';
        row.innerHTML = `<span class="label"><i class="ph ph-sketch-logo"></i> Giá trị Bạc:</span><span class="value" id="asset-silver-value">0 ₫</span>`;
        list.appendChild(row);
    }
    const silverValEl = document.getElementById('asset-silver-value');
    if (silverValEl) {
        silverValEl.textContent = formatCurrency(silverValue);
    }'''

js = js.replace(old_calc, new_calc)

# 2. Update renderSilverPurchases init values (els.silverUnitSelect.value initial population)
old_init_silver = '''        if (els.goldAmountInput) els.goldAmountInput.value = state.assets.goldAmount || '';
        if (els.goldUnitSelect) els.goldUnitSelect.value = state.assets.goldUnit || 'chi';
        if (els.bankSavingsInput && state.assets.bankSavings > 0) {
            els.bankSavingsInput.value = new Intl.NumberFormat('vi-VN').format(state.assets.bankSavings);
        }
        if (els.manualGoldInput && state.assets.manualPrice > 0) {
            els.manualGoldInput.value = new Intl.NumberFormat('vi-VN').format(state.assets.manualPrice);
        }'''
new_init_silver = '''        if (els.goldAmountInput) els.goldAmountInput.value = state.assets.goldAmount || '';
        if (els.goldUnitSelect) els.goldUnitSelect.value = state.assets.goldUnit || 'chi';
        
        if (els.silverAmountInput) els.silverAmountInput.value = state.assets.silverAmount || '';
        if (els.silverUnitSelect) els.silverUnitSelect.value = state.assets.silverUnit || 'chi';
        
        if (els.bankSavingsInput && state.assets.bankSavings > 0) {
            els.bankSavingsInput.value = new Intl.NumberFormat('vi-VN').format(state.assets.bankSavings);
        }
        if (els.manualGoldInput && state.assets.manualPrice > 0) {
            els.manualGoldInput.value = new Intl.NumberFormat('vi-VN').format(state.assets.manualPrice);
        }'''
js = js.replace(old_init_silver, new_init_silver)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('Success script 9 app.js')
