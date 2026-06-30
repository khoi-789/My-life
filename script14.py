import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add updateSilverUnitLabels function and call it in renderAssets
old_render_assets_init = '''    if (!renderAssets._inputsInitialized) {
        renderAssets._inputsInitialized = true;
        if (els.goldAmountInput) els.goldAmountInput.value = state.assets.goldAmount || '';
        if (els.goldUnitSelect) els.goldUnitSelect.value = state.assets.goldUnit || 'chi';
        
        if (els.silverAmountInput) els.silverAmountInput.value = state.assets.silverAmount || '';
        if (els.silverUnitSelect) els.silverUnitSelect.value = state.assets.silverUnit || 'chi';
        
        if (els.bankSavingsInput && state.assets.bankSavings > 0) {'''
        
new_render_assets_init = '''    if (!renderAssets._inputsInitialized) {
        renderAssets._inputsInitialized = true;
        if (els.goldAmountInput) els.goldAmountInput.value = state.assets.goldAmount || '';
        if (els.goldUnitSelect) els.goldUnitSelect.value = state.assets.goldUnit || 'chi';
        
        if (els.silverAmountInput) els.silverAmountInput.value = state.assets.silverAmount || '';
        if (els.silverUnitSelect) {
            els.silverUnitSelect.value = state.assets.silverUnit || 'chi';
            const unitValue = els.silverUnitSelect.value;
            const unitName = unitValue === 'kg' ? 'Kg' : (unitValue === 'cay' ? 'Lượng' : 'Chỉ');
            if (els.silverPriceLabel) els.silverPriceLabel.innerHTML = `<i class="ph ph-tag"></i> Giá bạc (VND / ${unitName})`;
            if (els.silverSummaryUnitName) els.silverSummaryUnitName.textContent = unitName;
        }
        
        if (els.bankSavingsInput && state.assets.bankSavings > 0) {'''

js = js.replace(old_render_assets_init, new_render_assets_init)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('Success script 14 app.js')
