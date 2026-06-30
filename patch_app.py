import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update calculateSummary
old_summary_loop = '''                if (d < firstOfCurrentMonth) incomePrev += t.amount;
            }
        }
    });

    const savingsPrevious = incomePrev - expensePrev;'''

new_summary_loop = '''                if (d < firstOfCurrentMonth) incomePrev += t.amount;
            }
        }
        
        // Custom logic for withdrawing savings: subtract from past savings
        if (t.categoryId === 'withdraw_savings') {
            expensePrev += t.amount;
        }
    });

    const savingsPrevious = incomePrev - expensePrev;'''

js = js.replace(old_summary_loop, new_summary_loop)

# 2. Update calculateTotalAssets (appBalance)
old_assets_loop = '''            } else if (t.type === 'debt') {
                if (t.categoryId === 'debt_borrow' || t.categoryId === 'debt_recover') incomePrev += t.amount;
                else expensePrev += t.amount;
            }
        }
    });

    const appBalance = incomePrev - expensePrev;'''

new_assets_loop = '''            } else if (t.type === 'debt') {
                if (t.categoryId === 'debt_borrow' || t.categoryId === 'debt_recover') incomePrev += t.amount;
                else expensePrev += t.amount;
            }
        }
        
        // Custom logic for withdrawing savings: subtract from past savings
        if (t.categoryId === 'withdraw_savings') {
            expensePrev += t.amount;
        }
    });

    const appBalance = incomePrev - expensePrev;'''

js = js.replace(old_assets_loop, new_assets_loop)

# 3. Add global functions for the Modal at the bottom of the file
modal_functions = '''

// ==========================================
// WITHDRAW SAVINGS FEATURE
// ==========================================
let currentMaxSavings = 0;

window.openWithdrawSavingsModal = () => {
    // Calculate current max savings available
    let inc = 0, exp = 0;
    const now = new Date();
    const firstOfCurrentMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    
    state.transactions.forEach(t => {
        const d = new Date(t.date);
        if (d < firstOfCurrentMonth) {
            if (t.type === 'income') inc += t.amount;
            else if (t.type === 'expense') exp += t.amount;
            else if (t.type === 'debt') {
                if (t.categoryId === 'debt_borrow' || t.categoryId === 'debt_recover') inc += t.amount;
                else exp += t.amount;
            }
        }
        if (t.categoryId === 'withdraw_savings') exp += t.amount;
    });
    
    currentMaxSavings = inc - exp;
    if (currentMaxSavings < 0) currentMaxSavings = 0;
    
    // Set default date to today
    const tzOffset = (new Date()).getTimezoneOffset() * 60000;
    const localISOTime = (new Date(Date.now() - tzOffset)).toISOString().slice(0, 10);
    document.getElementById('withdraw-savings-date').value = localISOTime;
    
    document.getElementById('withdraw-savings-amount').value = '';
    
    const modal = document.getElementById('withdraw-savings-modal');
    if (modal) {
        modal.style.display = 'flex';
        modal.style.opacity = '0';
        setTimeout(() => modal.style.opacity = '1', 10);
    }
};

window.closeWithdrawSavingsModal = () => {
    const modal = document.getElementById('withdraw-savings-modal');
    if (modal) {
        modal.style.opacity = '0';
        setTimeout(() => modal.style.display = 'none', 300);
    }
};

window.confirmWithdrawSavings = () => {
    const amountInput = document.getElementById('withdraw-savings-amount');
    const dateInput = document.getElementById('withdraw-savings-date');
    const noteInput = document.getElementById('withdraw-savings-note');
    
    const amountStr = amountInput.value.replace(/\D/g, '');
    if (!amountStr) {
        alert('Vui lòng nhập số tiền hợp lệ!');
        return;
    }
    const amount = parseInt(amountStr);
    if (amount <= 0) {
        alert('Số tiền phải lớn hơn 0!');
        return;
    }
    
    if (amount > currentMaxSavings && currentMaxSavings > 0) {
        if (!confirm(`Số tiền rút (${new Intl.NumberFormat('vi-VN').format(amount)} đ) vượt quá số dư Tích lũy hiện tại (${new Intl.NumberFormat('vi-VN').format(currentMaxSavings)} đ). Bạn có chắc chắn muốn tiếp tục?`)) {
            return;
        }
    }
    
    const dateVal = dateInput.value;
    if (!dateVal) {
        alert('Vui lòng chọn ngày!');
        return;
    }
    
    const note = noteInput.value.trim() || 'Rút từ Tích lũy cũ';
    
    const newTx = {
        id: Date.now().toString(),
        type: 'income',
        amount: amount,
        categoryId: 'withdraw_savings',
        categoryName: 'Rút Tích Lũy',
        date: dateVal,
        note: note
    };
    
    state.transactions.push(newTx);
    saveData();
    updateUI();
    
    if (typeof renderAssets === 'function') renderAssets(); // Update Total Assets
    
    window.closeWithdrawSavingsModal();
    
    // Add success toast if exist
    const toast = document.getElementById('toast');
    if (toast) {
        toast.textContent = 'Đã rút tiền thành công!';
        toast.className = 'toast show success';
        setTimeout(() => { toast.className = toast.className.replace('show', ''); }, 3000);
    }
};

// Add formatting logic to the amount input
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const wAmountInput = document.getElementById('withdraw-savings-amount');
        if (wAmountInput) {
            wAmountInput.addEventListener('input', function(e) {
                let val = this.value.replace(/\D/g, '');
                if (val !== '') {
                    this.value = new Intl.NumberFormat('vi-VN').format(parseInt(val));
                } else {
                    this.value = '';
                }
            });
        }
        
        const wBtnAll = document.getElementById('btn-withdraw-savings-all');
        if (wBtnAll) {
            wBtnAll.addEventListener('click', () => {
                if (wAmountInput) wAmountInput.value = new Intl.NumberFormat('vi-VN').format(currentMaxSavings);
            });
        }
    }, 1000); // give time for HTML to be parsed if not already
});

'''

js += modal_functions

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('Success script patch_app app.js')
