import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Add bindSilverEvents
silver_events_code = '''
const bindSilverEvents = () => {
    if (els.silverAmountInput) {
        els.silverAmountInput.addEventListener('input', () => {
            state.assets.silverAmount = parseFloat(els.silverAmountInput.value) || 0;
            saveData();
            if (typeof renderAssets === 'function') renderAssets();
        });
    }

    if (els.silverUnitSelect) {
        els.silverUnitSelect.addEventListener('change', () => {
            state.assets.silverUnit = els.silverUnitSelect.value;
            saveData();
            if (typeof renderAssets === 'function') renderAssets();
            calculateInitialSilverTickSum();
        });
    }
    
    if (els.btnSaveSilverAmount) {
        els.btnSaveSilverAmount.addEventListener('click', () => {
            showToast('Đã lưu số lượng Bạc', 'success');
        });
    }

    if (els.manualSilverPriceKg) {
        els.manualSilverPriceKg.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            this.value = value ? new Intl.NumberFormat('vi-VN').format(value) : '';
        });
    }
    
    if (els.manualSilverPriceCay) {
        els.manualSilverPriceCay.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            this.value = value ? new Intl.NumberFormat('vi-VN').format(value) : '';
        });
    }
    
    if (els.manualSilverPriceChi) {
        els.manualSilverPriceChi.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            this.value = value ? new Intl.NumberFormat('vi-VN').format(value) : '';
        });
    }

    if (els.btnSaveSilverPrice) {
        els.btnSaveSilverPrice.addEventListener('click', () => {
            const kg = parseInt(els.manualSilverPriceKg.value.replace(/\D/g, '')) || 0;
            const cay = parseInt(els.manualSilverPriceCay.value.replace(/\D/g, '')) || 0;
            const chi = parseInt(els.manualSilverPriceChi.value.replace(/\D/g, '')) || 0;
            
            state.assets.manualSilverPrices = { kg, cay, chi };
            saveData();
            showToast('Đã lưu bộ giá Bạc thành công!', 'success');
            if (typeof renderAssets === 'function') renderAssets();
        });
    }

    if (els.silverPurchaseCost) {
        els.silverPurchaseCost.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            this.value = value ? new Intl.NumberFormat('vi-VN').format(value) : '';
        });
    }

    if (els.silverPurchaseUnitPrice) {
        els.silverPurchaseUnitPrice.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            this.value = value ? new Intl.NumberFormat('vi-VN').format(value) : '';
            
            const amt = parseFloat(els.silverPurchaseAmount.value) || 0;
            const unitPrice = parseInt(this.value.replace(/\D/g, '')) || 0;
            if (amt > 0 && unitPrice > 0) {
                els.silverPurchaseCost.value = new Intl.NumberFormat('vi-VN').format(amt * unitPrice);
            }
        });
    }

    if (els.silverPurchaseAmount) {
        els.silverPurchaseAmount.addEventListener('input', function() {
            const amt = parseFloat(this.value) || 0;
            const unitPrice = parseInt(els.silverPurchaseUnitPrice.value.replace(/\D/g, '')) || 0;
            if (amt > 0 && unitPrice > 0) {
                els.silverPurchaseCost.value = new Intl.NumberFormat('vi-VN').format(amt * unitPrice);
            }
        });
    }

    if (els.btnAddSilverPurchase) {
        els.btnAddSilverPurchase.addEventListener('click', addSilverPurchase);
    }
    
    // Silver Purchase Filter
    document.querySelectorAll('.silver-filter-group .filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.silver-filter-group .filter-btn').forEach(b => {
                b.classList.remove('active');
                b.style.background = 'none';
                b.style.color = 'var(--text-main)';
            });
            btn.classList.add('active');
            btn.style.background = 'var(--primary)';
            btn.style.color = '#fff';
            if (typeof renderSilverPurchases === 'function') renderSilverPurchases();
        });
    });

    if (els.btnOpenSilverCalendar) {
        els.btnOpenSilverCalendar.addEventListener('click', () => {
            els.silverPurchaseDate.showPicker();
        });
    }

    if (els.silverPurchaseDate) {
        els.silverPurchaseDate.addEventListener('change', function() {
            if (this.value) {
                const [y, m, d] = this.value.split('-');
                els.silverPurchaseDateDisplay.value = `${d}/${m}/${y}`;
            }
        });
    }

    if (els.silverPurchaseDateDisplay) {
        els.silverPurchaseDateDisplay.addEventListener('input', function(e) {
            let v = this.value.replace(/\D/g, '');
            if (v.length > 8) v = v.slice(0, 8);
            
            let formatted = v;
            if (v.length > 2) formatted = v.slice(0, 2) + '/' + v.slice(2);
            if (v.length > 4) formatted = formatted.slice(0, 5) + '/' + v.slice(4);
            
            this.value = formatted;
            
            if (v.length === 8) {
                const d = v.slice(0, 2);
                const m = v.slice(2, 4);
                const y = v.slice(4, 8);
                els.silverPurchaseDate.value = `${y}-${m}-${d}`;
            }
        });
    }

    if (els.silverSelectAll) {
        els.silverSelectAll.addEventListener('change', (e) => {
            const isChecked = e.target.checked;
            const checkboxes = els.silverPurchaseList.querySelectorAll('.silver-row-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = isChecked;
            });
            updateSilverAmountFromTicks();
        });
    }
    
    setupSilverCheckboxDelegation();
};
'''

content += '\n' + silver_events_code

# Inject into setupEventListeners
# find: 
#    els.goldPurchaseList.removeEventListener('change', handleGoldCheckboxChange);
#    els.goldPurchaseList.addEventListener('change', handleGoldCheckboxChange);
# };
content = content.replace("els.goldPurchaseList.addEventListener('change', handleGoldCheckboxChange);\n};", "els.goldPurchaseList.addEventListener('change', handleGoldCheckboxChange);\n    bindSilverEvents();\n};")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Success bindSilverEvents')
