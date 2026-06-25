import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Filter out corrupt data before sorting
old_sort = '''const sorted = [...filteredPurchases].sort((a, b) => new Date(b.date) - new Date(a.date));'''
new_sort = '''const validPurchases = filteredPurchases.filter(p => p && typeof p === 'object');
        const sorted = validPurchases.sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0));'''

content = content.replace(old_sort, new_sort)

# Fix 2: Call renderSilverPurchases before updateSilverAmountFromTicks in addSilverPurchase
old_add = '''    saveData();
    clearSilverPurchaseForm();
    updateSilverAmountFromTicks(); 
};'''

new_add = '''    saveData();
    clearSilverPurchaseForm();
    if (typeof renderAssets === 'function') renderAssets();
    updateSilverAmountFromTicks(); 
};'''

content = content.replace(old_add, new_add)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Success script 6')
