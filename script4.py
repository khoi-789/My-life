import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update addSilverPurchase
addSilver_old = '''const addSilverPurchase = () => {
    const dateStr = document.getElementById('silver-purchase-date').value;
    const amount = parseFloat(els.silverPurchaseAmount.value);
    const unit = els.silverPurchaseUnit.value;
    const type = els.silverPurchaseType.value.trim();
    const cost = parseFormattedNumber(els.silverPurchaseCost.value);
    
    if (!dateStr || isNaN(amount) || amount <= 0 || isNaN(cost) || cost <= 0) {
        showToast('Vui lòng nhập Ngày mua, Số lượng và Tiền vốn hợp lệ', 'warning');
        return;
    }
    
    let unitPrice = 0;
    if (els.silverPurchaseUnitPrice.value) {
        unitPrice = parseFormattedNumber(els.silverPurchaseUnitPrice.value);
    }
    
    const editId = els.silverPurchaseEditId.value;'''

addSilver_new = '''const addSilverPurchase = () => {
    let dateStr = document.getElementById('silver-purchase-date').value;
    const displayVal = document.getElementById('silver-purchase-date-display').value;
    if (displayVal && displayVal.length === 10) {
        const [d, m, y] = displayVal.split('/');
        dateStr = `${y}-${m}-${d}`;
    }

    const amount = parseFloat(els.silverPurchaseAmount.value) || 0;
    const unit = els.silverPurchaseUnit.value;
    const type = els.silverPurchaseType.value.trim();
    const cost = parseInt(els.silverPurchaseCost.value.replace(/\D/g, '')) || 0;
    
    if (!dateStr || dateStr.split('-').length !== 3) {
        if (typeof showToast === 'function') showToast('Vui lòng nhập ngày hợp lệ (Ngày/Tháng/Năm).', 'warning');
        else alert('Vui lòng nhập ngày hợp lệ (Ngày/Tháng/Năm).');
        return;
    }
    if (amount <= 0 || cost <= 0) {
        if (typeof showToast === 'function') showToast('Vui lòng nhập Số lượng và Tiền vốn hợp lệ.', 'warning');
        else alert('Vui lòng nhập Số lượng và Tiền vốn hợp lệ.');
        return;
    }
    
    const unitPriceStr = els.silverPurchaseUnitPrice.value.replace(/\D/g, '');
    let unitPrice = parseInt(unitPriceStr) || 0;
    
    const editId = els.silverPurchaseEditId.value;'''

content = content.replace(addSilver_old, addSilver_new)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Success addSilverPurchase fix')
