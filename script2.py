import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update renderAssets
renderAssets_old = '''const renderAssets = () => {
    const goldPriceToUse = state.assets.isManualGold ? state.assets.manualPrice : state.assets.lastGoldPrice;
    const goldValue = state.assets.goldAmount * goldPriceToUse;
    const totalAssets = state.appBalance + state.assets.bankSavings + goldValue;
    
    if (els.totalAssetValue) els.totalAssetValue.textContent = formatCurrency(totalAssets);
    if (els.assetAppBalance) els.assetAppBalance.textContent = formatCurrency(state.appBalance);
    if (els.assetBankBalance) els.assetBankBalance.textContent = formatCurrency(state.assets.bankSavings);
    if (els.assetGoldValue) els.assetGoldValue.textContent = formatCurrency(goldValue);
    
    renderGoldPurchases();
};'''

renderAssets_new = '''const renderAssets = () => {
    const goldPriceToUse = state.assets.isManualGold ? state.assets.manualPrice : state.assets.lastGoldPrice;
    const goldValue = state.assets.goldAmount * goldPriceToUse;
    
    let silverValue = 0;
    const silverPrices = state.assets.manualSilverPrices || {kg: 0, cay: 0, chi: 0};
    if (state.assets.silverPurchases && state.assets.selectedSilverPurchaseIds) {
        state.assets.silverPurchases.forEach(p => {
            if (state.assets.selectedSilverPurchaseIds.includes(String(p.id)) || state.assets.selectedSilverPurchaseIds.includes(Number(p.id))) {
                let pPrice = silverPrices[p.unit] || 0;
                silverValue += p.amount * pPrice;
            }
        });
    }

    const totalAssets = state.appBalance + state.assets.bankSavings + goldValue + silverValue;
    
    if (els.totalAssetValue) els.totalAssetValue.textContent = formatCurrency(totalAssets);
    if (els.assetAppBalance) els.assetAppBalance.textContent = formatCurrency(state.appBalance);
    if (els.assetBankBalance) els.assetBankBalance.textContent = formatCurrency(state.assets.bankSavings);
    if (els.assetGoldValue) els.assetGoldValue.textContent = formatCurrency(goldValue);
    
    const assetSilverValue = document.getElementById('asset-silver-value');
    if (assetSilverValue) assetSilverValue.textContent = formatCurrency(silverValue);
    
    renderGoldPurchases();
    if (typeof renderSilverPurchases === 'function') renderSilverPurchases();
};'''

content = content.replace(renderAssets_old, renderAssets_new)

# 2. Add Silver functions
silver_code = '''
// --- SILVER LOGIC ---
window.switchAssetTab = (tabName) => {
    if (tabName === 'gold') {
        els.assetsGoldView.style.display = 'block';
        els.assetsSilverView.style.display = 'none';
        els.btnTabGold.style.background = '';
        els.btnTabGold.style.color = '';
        els.btnTabGold.style.border = '';
        els.btnTabGold.className = 'btn btn-primary';

        els.btnTabSilver.className = 'btn';
        els.btnTabSilver.style.background = 'rgba(255,255,255,0.4)';
        els.btnTabSilver.style.color = 'var(--text-main)';
        els.btnTabSilver.style.border = '1px solid var(--card-border)';
    } else {
        els.assetsGoldView.style.display = 'none';
        els.assetsSilverView.style.display = 'block';
        
        els.btnTabSilver.style.background = '';
        els.btnTabSilver.style.color = '';
        els.btnTabSilver.style.border = '';
        els.btnTabSilver.className = 'btn btn-primary';

        els.btnTabGold.className = 'btn';
        els.btnTabGold.style.background = 'rgba(255,255,255,0.4)';
        els.btnTabGold.style.color = 'var(--text-main)';
        els.btnTabGold.style.border = '1px solid var(--card-border)';
    }
};

window.renderSilverPurchases = () => {
    if (!els.silverPurchaseList) return;
    
    els.silverPurchaseList.innerHTML = '';
    let totalCost = 0;
    
    // Calculate display values based on selected IDs
    let selectedKg = 0;
    let selectedCay = 0;
    let selectedChi = 0;
    
    if (state.assets.silverPurchases && state.assets.selectedSilverPurchaseIds) {
        state.assets.silverPurchases.forEach(p => {
            if (state.assets.selectedSilverPurchaseIds.includes(String(p.id)) || state.assets.selectedSilverPurchaseIds.includes(Number(p.id))) {
                if (p.unit === 'kg') selectedKg += p.amount;
                if (p.unit === 'cay') selectedCay += p.amount;
                if (p.unit === 'chi') selectedChi += p.amount;
                totalCost += (p.cost || 0);
            }
        });
    }

    const activeFilterBtn = document.querySelector('.silver-filter-group .filter-btn.active');
    const currentFilter = activeFilterBtn ? activeFilterBtn.dataset.filter : 'all';

    let filteredPurchases = state.assets.silverPurchases || [];
    if (currentFilter !== 'all') {
        filteredPurchases = filteredPurchases.filter(p => p.category && p.category.toLowerCase() === currentFilter.toLowerCase());
    }

    if (filteredPurchases.length === 0) {
        els.silverPurchaseList.innerHTML = `<tr><td colspan="11" style="text-align: center; padding: 30px; color: var(--text-muted);"><i class="ph ph-folder-open" style="font-size: 32px; margin-bottom: 10px;"></i><p>Không có dữ liệu cho mục này</p></td></tr>`;
        if (els.totalSilverCost) els.totalSilverCost.textContent = '0 ₫';
        if (els.silverProfitLoss) els.silverProfitLoss.textContent = '0 ₫';
        return;
    }

    const sorted = [...filteredPurchases].sort((a, b) => new Date(b.date) - new Date(a.date));
    
    sorted.forEach(p => {
        const row = document.createElement('tr');
        row.className = 'hoverable-row';
        const formattedDate = new Date(p.date).toLocaleDateString('vi-VN');
        const unitName = p.unit === 'kg' ? 'Kg' : (p.unit === 'cay' ? 'Lượng' : 'Chỉ');
        
        let unitPriceDisplay = '';
        if (p.unitPrice && !isNaN(p.unitPrice)) {
            unitPriceDisplay = formatCurrency(p.unitPrice);
        } else if (p.cost && p.amount) {
            unitPriceDisplay = '~ ' + formatCurrency(p.cost / p.amount);
        }

        const isSelected = state.assets.selectedSilverPurchaseIds?.some(sid => String(sid) === String(p.id));
        
        // Calculate difference for this specific row based on its unit
        let profitDisplay = '-';
        let profitColor = 'var(--text-muted)';
        const currentPrice = state.assets.manualSilverPrices ? (state.assets.manualSilverPrices[p.unit] || 0) : 0;
        
        if (currentPrice > 0 && p.cost) {
            const currentValue = p.amount * currentPrice;
            const profit = currentValue - p.cost;
            profitDisplay = (profit >= 0 ? '+' : '') + formatCurrency(profit);
            profitColor = profit >= 0 ? 'var(--success)' : 'var(--danger)';
        }
        
        row.innerHTML = `
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border); text-align: center;">
                <input type="checkbox" class="silver-row-checkbox" data-id="${p.id}" data-amount="${p.amount}" data-unit="${p.unit}" ${isSelected ? 'checked' : ''} style="width:18px; height:18px; cursor:pointer;">
            </td>
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border); font-size: 13px;">${formattedDate}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border); font-weight: 600;">${p.amount} ${unitName}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border); text-align: right; color: var(--text-muted); font-size: 13px;">${unitPriceDisplay}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border); font-size: 13px;">${p.type || ''}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border);"><span class="badge badge-primary">${p.category || 'Tích trữ'}</span></td>
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border); font-weight: 600; text-align: right; color: var(--text-main);">${formatCurrency(p.cost)}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border); font-size: 13px;">${p.shop || ''}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border); font-size: 13px; color: var(--text-muted);">${p.address || ''}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border); font-size: 13px; color: var(--text-muted);">${p.note || ''}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--card-border); text-align: center;">
                <div style="display:flex; gap:4px; justify-content:center;">
                    <button onclick="editSilverPurchase(${p.id})" class="btn btn-secondary small" title="Sửa" style="padding:4px 8px; color:var(--primary); background:var(--primary-light);">
                        <i class="ph ph-pencil-simple"></i>
                    </button>
                    <button onclick="deleteSilverPurchase(${p.id})" class="btn btn-secondary small" title="Xóa" style="padding:4px 8px; color:var(--danger); background:var(--danger-bg);">
                        <i class="ph ph-trash"></i>
                    </button>
                </div>
            </td>
        `;
        els.silverPurchaseList.appendChild(row);
    });

    if (els.totalSilverCost) els.totalSilverCost.textContent = formatCurrency(totalCost);

    if (els.silverProfitLoss) {
        let currentMarketValue = 0;
        const prices = state.assets.manualSilverPrices || {kg:0, cay:0, chi:0};
        currentMarketValue += selectedKg * prices.kg;
        currentMarketValue += selectedCay * prices.cay;
        currentMarketValue += selectedChi * prices.chi;
        
        const profit = currentMarketValue - totalCost;
        els.silverProfitLoss.textContent = (profit >= 0 ? '+' : '') + formatCurrency(profit);
        els.silverProfitLoss.style.color = profit >= 0 ? 'var(--success)' : 'var(--danger)';
    }
    
    calculateInitialSilverTickSum();
};

const setupSilverCheckboxDelegation = () => {
    if (!els.silverPurchaseList) return;
    els.silverPurchaseList.removeEventListener('change', handleSilverCheckboxChange);
    els.silverPurchaseList.addEventListener('change', handleSilverCheckboxChange);
};

const handleSilverCheckboxChange = (e) => {
    if (e.target.classList.contains('silver-row-checkbox')) {
        updateSilverAmountFromTicks();
    }
};

const calculateInitialSilverTickSum = () => {
    if (!state.assets.selectedSilverPurchaseIds || !els.selectedSilverSum) return;
    
    let totalInChi = 0;
    (state.assets.silverPurchases || []).forEach(p => {
        if (state.assets.selectedSilverPurchaseIds.includes(String(p.id)) || state.assets.selectedSilverPurchaseIds.includes(Number(p.id))) {
            if (p.unit === 'kg') totalInChi += p.amount * 266.6667;
            else if (p.unit === 'cay') totalInChi += p.amount * 10;
            else totalInChi += p.amount;
        }
    });

    const targetUnit = els.silverUnitSelect?.value || 'chi';
    let finalAmount = totalInChi;
    if (targetUnit === 'cay') finalAmount = totalInChi / 10;
    else if (targetUnit === 'kg') finalAmount = totalInChi / 266.6667;

    els.selectedSilverSum.textContent = finalAmount.toFixed(3).replace(/\.?0+$/, '') + (targetUnit === 'kg' ? ' Kg' : (targetUnit === 'cay' ? ' Lượng' : ' Chỉ'));
    if (els.selectedSilverTotalDisplay) {
        els.selectedSilverTotalDisplay.style.display = totalInChi > 0 ? 'block' : 'none';
    }
    
    if (els.silverSelectAll) {
        const checkboxes = els.silverPurchaseList.querySelectorAll('.silver-row-checkbox');
        const checkedCount = els.silverPurchaseList.querySelectorAll('.silver-row-checkbox:checked').length;
        els.silverSelectAll.checked = (checkboxes.length > 0 && checkedCount === checkboxes.length);
    }
};

const updateSilverAmountFromTicks = () => {
    const checkboxes = els.silverPurchaseList.querySelectorAll('.silver-row-checkbox:checked');
    const allCheckboxes = els.silverPurchaseList.querySelectorAll('.silver-row-checkbox');
    
    let totalInChi = 0;
    const selectedIds = [];

    checkboxes.forEach(cb => {
        const amount = parseFloat(cb.dataset.amount);
        const unit = cb.dataset.unit;
        selectedIds.push(cb.dataset.id);
        
        if (unit === 'kg') totalInChi += amount * 266.6667;
        else if (unit === 'cay') totalInChi += amount * 10;
        else totalInChi += amount;
    });

    state.assets.selectedSilverPurchaseIds = selectedIds;
    
    if (els.silverSelectAll) {
        els.silverSelectAll.checked = (checkboxes.length > 0 && checkboxes.length === allCheckboxes.length);
    }

    const targetUnit = els.silverUnitSelect?.value || 'chi';
    let finalAmount = totalInChi;
    if (targetUnit === 'cay') finalAmount = totalInChi / 10;
    else if (targetUnit === 'kg') finalAmount = totalInChi / 266.6667;

    if (els.selectedSilverSum) {
        els.selectedSilverSum.textContent = finalAmount.toFixed(3).replace(/\.?0+$/, '') + (targetUnit === 'kg' ? ' Kg' : (targetUnit === 'cay' ? ' Lượng' : ' Chỉ'));
        if (els.selectedSilverTotalDisplay) {
            els.selectedSilverTotalDisplay.style.display = totalInChi > 0 ? 'block' : 'none';
        }
    }

    if (els.silverAmountInput) {
        els.silverAmountInput.value = finalAmount > 0 ? finalAmount.toFixed(3).replace(/\.?0+$/, '') : 0;
    }
    
    state.assets.silverAmount = finalAmount;
    state.assets.silverUnit = targetUnit;
    saveData(); 
    
    if (typeof renderAssets === 'function') {
        renderAssets();
    }
};

const addSilverPurchase = () => {
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
    
    const editId = els.silverPurchaseEditId.value;
    if (!state.assets.silverPurchases) state.assets.silverPurchases = [];

    const purchaseData = {
        amount,
        unit,
        unitPrice,
        cost,
        type,
        category: els.silverPurchaseCategory.value,
        shop: els.silverPurchaseShop.value.trim(),
        address: els.silverPurchaseAddress.value.trim(),
        note: els.silverPurchaseNote.value.trim(),
        date: dateStr
    };
    
    if (editId) {
        const idx = state.assets.silverPurchases.findIndex(p => String(p.id) === String(editId));
        if (idx > -1) {
            state.assets.silverPurchases[idx] = { ...state.assets.silverPurchases[idx], ...purchaseData };
            showToast('Đã cập nhật giao dịch bạc!', 'success');
        }
    } else {
        const newPurchase = {
            id: Date.now(),
            ...purchaseData
        };
        state.assets.silverPurchases.push(newPurchase);
        
        if (!state.assets.selectedSilverPurchaseIds) state.assets.selectedSilverPurchaseIds = [];
        state.assets.selectedSilverPurchaseIds.push(String(newPurchase.id));
        
        showToast('Đã thêm giao dịch bạc mới!', 'success');
    }
    
    saveData();
    clearSilverPurchaseForm();
    updateSilverAmountFromTicks(); 
};

const editSilverPurchase = (id) => {
    const p = (state.assets.silverPurchases || []).find(item => String(item.id) === String(id));
    if (!p) return;
    
    els.silverPurchaseEditId.value = p.id;
    els.silverPurchaseAmount.value = p.amount;
    els.silverPurchaseUnit.value = p.unit;
    els.silverPurchaseUnitPrice.value = p.unitPrice ? formatNumber(p.unitPrice) : '';
    els.silverPurchaseType.value = p.type || '';
    els.silverPurchaseCategory.value = p.category || 'bạc tích trữ';
    els.silverPurchaseCost.value = p.cost ? formatNumber(p.cost) : '';
    els.silverPurchaseShop.value = p.shop || '';
    els.silverPurchaseAddress.value = p.address || '';
    els.silverPurchaseNote.value = p.note || '';
    
    const dateObj = new Date(p.date);
    document.getElementById('silver-purchase-date').value = p.date;
    const day = String(dateObj.getDate()).padStart(2, '0');
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const year = dateObj.getFullYear();
    document.getElementById('silver-purchase-date-display').value = f"{day}/{month}/{year}";
    
    els.silverPurchaseBtnText.textContent = 'Cập nhật';
    document.getElementById('silver-purchase-form-container').scrollIntoView({ behavior: 'smooth', block: 'center' });
};

const deleteSilverPurchase = (id) => {
    if (confirm('Bạn có chắc chắn muốn xóa giao dịch bạc này?')) {
        if (state.assets.silverPurchases) {
            state.assets.silverPurchases = state.assets.silverPurchases.filter(p => String(p.id) !== String(id));
        }
        if (state.assets.selectedSilverPurchaseIds) {
            state.assets.selectedSilverPurchaseIds = state.assets.selectedSilverPurchaseIds.filter(sid => String(sid) !== String(id));
        }
        saveData();
        updateSilverAmountFromTicks(); 
        showToast('Đã xóa giao dịch!', 'success');
    }
};

const clearSilverPurchaseForm = () => {
    els.silverPurchaseEditId.value = '';
    els.silverPurchaseAmount.value = '';
    els.silverPurchaseUnitPrice.value = '';
    els.silverPurchaseType.value = '';
    els.silverPurchaseCost.value = '';
    els.silverPurchaseShop.value = '';
    els.silverPurchaseAddress.value = '';
    els.silverPurchaseNote.value = '';
    document.getElementById('silver-purchase-date').value = '';
    document.getElementById('silver-purchase-date-display').value = '';
    els.silverPurchaseBtnText.textContent = 'Thêm/Lưu';
};

window.addSilverPurchase = addSilverPurchase;
window.editSilverPurchase = editSilverPurchase;
window.deleteSilverPurchase = deleteSilverPurchase;
'''

silver_code = silver_code.replace('f"{day}/{month}/{year}"', '`${day}/${month}/${year}`')

content += '\n' + silver_code

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated app.js with silver logic successfully.')
