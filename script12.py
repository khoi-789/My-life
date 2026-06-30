import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add renderSilverPurchases to renderAssets
old_render_assets_end = '''    els.assetBankBalance.textContent = formatCurrency(bankSavings);
    els.assetGoldValue.textContent = formatCurrency(goldValue);'''

new_render_assets_end = '''    els.assetBankBalance.textContent = formatCurrency(bankSavings);
    els.assetGoldValue.textContent = formatCurrency(goldValue);
    
    if (typeof renderSilverPurchases === 'function') renderSilverPurchases();'''

js = js.replace(old_render_assets_end, new_render_assets_end)

# 2. Update deleteSilverPurchase to call renderAssets() instead of updateSilverAmountFromTicks()
old_delete = '''        saveData();
        updateSilverAmountFromTicks(); 
        showToast('Đã xóa giao dịch!', 'success');'''
new_delete = '''        saveData();
        if (typeof renderAssets === 'function') renderAssets();
        showToast('Đã xóa giao dịch!', 'success');'''
js = js.replace(old_delete, new_delete)
# Handle encoding variations just in case
old_delete2 = '''        saveData();
        updateSilverAmountFromTicks(); 
        showToast('Da xa giao d?ch!', 'success');'''
js = js.replace(old_delete2, new_delete)

# 3. Update addSilverPurchase to call renderAssets() instead of updateSilverAmountFromTicks()
old_add = '''    saveData();
    updateSilverAmountFromTicks();
    clearSilverPurchaseForm();'''
new_add = '''    saveData();
    if (typeof renderAssets === 'function') renderAssets();
    clearSilverPurchaseForm();'''
js = js.replace(old_add, new_add)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('Success script 12 app.js')
