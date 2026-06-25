import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Fix editSilverPurchase and deleteSilverPurchase (attach to window)
js = js.replace('const editSilverPurchase = (id) => {', 'window.editSilverPurchase = (id) => {')
js = js.replace('const deleteSilverPurchase = (id) => {', 'window.deleteSilverPurchase = (id) => {')

# 2. Fix calculateInitialSilverTickSum overriding the summary box incorrectly
old_calc_sum = '''    els.selectedSilverSum.textContent = finalAmount.toFixed(3).replace(/\\.?0+$/, '') + (targetUnit === 'kg' ? ' Kg' : (targetUnit === 'cay' ? ' Lượng' : ' Chỉ'));
    if (els.selectedSilverTotalDisplay) {
        els.selectedSilverTotalDisplay.style.display = totalInChi > 0 ? 'block' : 'none';
    }'''

new_calc_sum = '''    // Update summary box properly
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
    }'''

# Handle potential encoding character issues for the old string (like Lượng vs Lng)
# We will use regex to replace it
regex_calc_sum = r"els\.selectedSilverSum\.textContent\s*=\s*finalAmount\.toFixed\(3\)\.replace\(\/\\\.\[\?\^0\]\+\$\/,?\s*''\)\s*\+\s*\(targetUnit\s*===\s*'kg'\s*\?\s*' Kg'\s*:\s*\(targetUnit\s*===\s*'cay'\s*\?\s*'[^']*'\s*:\s*'[^']*'\)\);\s*if\s*\(els\.selectedSilverTotalDisplay\)\s*\{\s*els\.selectedSilverTotalDisplay\.style\.display\s*=\s*totalInChi\s*>\s*0\s*\?\s*'block'\s*:\s*'none';\s*\}"

js = re.sub(regex_calc_sum, new_calc_sum, js)

# Let's also do a fallback if regex fails
fallback_old = '''els.selectedSilverSum.textContent = finalAmount.toFixed(3).replace(/\.?0+$/, '') + (targetUnit === 'kg' ? ' Kg' : (targetUnit === 'cay' ? ' Lượng' : ' Chỉ'));'''
if fallback_old in js:
    # Just remove it, as the regex might have missed if formatting is exact
    pass

# Actually, the most robust way to replace the body of calculateInitialSilverTickSum is just match the whole function body
regex_full_calc = r'(const calculateInitialSilverTickSum = \(\) => \{)(.*?)(if \(!state\.assets\.selectedSilverPurchaseIds || !els\.selectedSilverSum\) return;)(.*?)(\n\s*if \(els\.silverSelectAll\) \{)'
def replacer(m):
    prefix = m.group(1) + m.group(2) + m.group(3) + m.group(4)
    # Inside group 4 is where the bad code is. We replace it.
    body = m.group(4)
    # Remove the bad lines
    body = re.sub(r"els\.selectedSilverSum\.textContent = .*?;", "", body)
    body = re.sub(r"if \(els\.selectedSilverTotalDisplay\) \{\s*els\.selectedSilverTotalDisplay\.style\.display = totalInChi > 0 \? 'block' : 'none';\s*\}", "", body)
    return m.group(1) + m.group(2) + m.group(3) + body + '\n' + new_calc_sum + '\n' + m.group(5)

js = re.sub(regex_full_calc, replacer, js, flags=re.DOTALL)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('Success script 10 app.js')
