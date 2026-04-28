// --- Firebase Configuration ---
const firebaseConfig = {
  apiKey: "AIzaSyAGwlGB_nowZWAjyz1fGRy30ZzwV5-igGY",
  authDomain: "mylife-a01e7.firebaseapp.com",
  projectId: "mylife-a01e7",
  storageBucket: "mylife-a01e7.firebasestorage.app",
  messagingSenderId: "570920781846",
  appId: "1:570920781846:web:7ca009b8fc659ec8e3cd37",
  measurementId: "G-1HKG64KXS2"
};

// Initialize Firebase (Avoid re-init if already initialized)
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const db = firebase.firestore();

// Household ID (Cố định để đồng bộ tự động giữa các thiết bị)
const householdId = 'family_khoi789'; 
const docRef = db.collection("households").doc(householdId);

// --- Constants & Config ---
const STORAGE_KEY = 'family_finance_data';

const DEFAULT_CATEGORIES = {
    income: [
        { id: 'inc_salary', name: 'Tiền lương', icon: '💰' },
        { id: 'inc_bonus', name: 'Tiền thưởng', icon: '🎁' },
        { id: 'inc_invest', name: 'Đầu tư', icon: '📈' },
        { id: 'inc_other', name: 'Thu nhập khác', icon: '💵' }
    ],
    expense: [
        { id: 'exp_food', name: 'Ăn uống', icon: '🍔' },
        { id: 'exp_transport', name: 'Di chuyển', icon: '🚍' },
        { id: 'exp_shopping', name: 'Mua sắm', icon: '🛍️' },
        { id: 'exp_bill', name: 'Điện nước', icon: '💡' },
        { id: 'exp_edu', name: 'Giáo dục', icon: '📚' },
        { id: 'exp_entertain', name: 'Giải trí', icon: '🎮' },
        { id: 'exp_family', name: 'Gia đình', icon: '🏠' },
        { id: 'exp_other', name: 'Chi tiêu khác', icon: '💸' }
    ],
    debt: [
        { id: 'debt_loan', name: 'Cho vay', icon: '📤' },
        { id: 'debt_borrow', name: 'Đi vay', icon: '📥' },
        { id: 'debt_recover', name: 'Thu nợ', icon: '💰' },
        { id: 'debt_repay', name: 'Trả nợ', icon: '💸' }
    ]
};

const isTransactionPositive = (t) => {
    if (t.type === 'income') return true;
    if (t.type === 'debt') {
        return (t.categoryId === 'debt_borrow' || t.categoryId === 'debt_recover');
    }
    return false;
};

// --- State Management ---
let state = {
    transactions: [],
    budgets: {},
    categories: null
};

// Initial data if empty
const dummyData = [
    { id: 't1', type: 'income', amount: 25000000, categoryId: 'inc_salary', date: '2026-04-01', note: 'Lương tháng 3' },
    { id: 't2', type: 'expense', amount: 1500000, categoryId: 'exp_food', date: '2026-04-02', note: 'Đi siêu thị' },
    { id: 't3', type: 'expense', amount: 500000, categoryId: 'exp_bill', date: '2026-04-05', note: 'Tiền điện' },
    { id: 't4', type: 'income', amount: 3000000, categoryId: 'inc_bonus', date: '2026-04-10', note: 'Thưởng dự án' },
    { id: 't5', type: 'expense', amount: 2000000, categoryId: 'exp_shopping', date: '2026-04-15', note: 'Mua quần áo' }
];

// --- Utilities ---
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
};

const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('vi-VN', options);
};

const generateId = () => '_' + Math.random().toString(36).substr(2, 9);

const getCategoryById = (type, id) => {
    return state.categories[type].find(c => c.id === id) || { id: 'other', name: 'Khác', icon: '❓' };
};

// --- Storage API ---
const loadData = async () => {
    // 1. Try to load from LocalStorage first (for speed)
    const localData = localStorage.getItem(STORAGE_KEY);
    if (localData) {
        state = JSON.parse(localData);
        if (!state.budgets) state.budgets = {};
        if (!state.categories) state.categories = JSON.parse(JSON.stringify(DEFAULT_CATEGORIES));
        if (!state.categories.debt) state.categories.debt = [...DEFAULT_CATEGORIES.debt]; 
        // Force update icons for debt if they are the old ones
        state.categories.debt.forEach(c => {
            const def = DEFAULT_CATEGORIES.debt.find(d => d.id === c.id);
            if (def) c.icon = def.icon;
        });
        updateUI();
    }

    // 2. Load from Firebase Cloud
    try {
        const docSnap = await docRef.get();
        if (docSnap.exists) {
            const cloudData = docSnap.data();
            // Merge or replace (here we replace with cloud since it's the source of truth)
            state = cloudData;
            if (!state.categories) state.categories = JSON.parse(JSON.stringify(DEFAULT_CATEGORIES));
            if (!state.categories.debt) state.categories.debt = [...DEFAULT_CATEGORIES.debt];
            saveDataLocal();
            updateUI();
        } else {
            // First time cloud setup
            if (!localData) {
                state.transactions = dummyData;
                state.budgets = {};
                state.categories = JSON.parse(JSON.stringify(DEFAULT_CATEGORIES));
            }
            await saveData(); // Initial push to cloud
        }
    } catch (e) {
        console.error("Cloud Error:", e);
    }

    // 3. Set up Real-time Sync
    docRef.onSnapshot((doc) => {
        if (doc.exists) {
            const data = doc.data();
            // Check if there are changes to avoid infinite UI loops
            if (JSON.stringify(data) !== JSON.stringify(state)) {
                state = data;
                if (!state.categories) state.categories = JSON.parse(JSON.stringify(DEFAULT_CATEGORIES));
                if (!state.categories.debt) state.categories.debt = [...DEFAULT_CATEGORIES.debt];
                saveDataLocal();
                updateUI();
            }
        }
    });
};

const saveDataLocal = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
};

const saveData = async () => {
    saveDataLocal();
    try {
        await docRef.set(state);
    } catch (e) {
        console.error("Error saving to cloud:", e);
    }
};

// --- DOM Elements ---
const els = {
    tabs: document.querySelectorAll('.nav-item'),
    tabContents: document.querySelectorAll('.tab-content'),
    totalBalance: document.getElementById('total-balance'),
    totalIncome: document.getElementById('total-income'),
    totalExpense: document.getElementById('total-expense'),
    recentTransactions: document.getElementById('recent-transactions'),
    transactionsBody: document.getElementById('transactions-body'),
    
    // Modal
    modal: document.getElementById('transaction-modal'),
    form: document.getElementById('transaction-form'),
    btnOpenSidebar: document.getElementById('btn-add-transaction-sidebar'),
    btnOpenPage: document.getElementById('btn-add-transaction-page'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    btnCancelModal: document.getElementById('btn-cancel'),
    
    // Form Inputs
    typeRadios: document.getElementsByName('type'),
    categorySelect: document.getElementById('trans-category'),
    amountInput: document.getElementById('trans-amount'),
    dateInput: document.getElementById('trans-date'),
    noteInput: document.getElementById('trans-note'),
    
    // Settings
    btnClearData: document.getElementById('btn-clear-data'),
    btnExportData: document.getElementById('btn-export-data'),
    btnImportData: document.getElementById('btn-import-data'),
    fileImport: document.getElementById('file-import'),
    
    // Summary Labels & Cards
    totalIncome: document.getElementById('total-income'),
    totalExpense: document.getElementById('total-expense'),
    totalBalanceCurrent: document.getElementById('total-balance-current'),
    savingsPrevious: document.getElementById('savings-previous'),
    labelIncomeMonth: document.getElementById('label-income-month'),
    labelExpenseMonth: document.getElementById('label-expense-month'),
    labelBalanceMonth: document.getElementById('label-balance-month'),
    
    // Sidebar Mobile
    sidebar: document.getElementById('sidebar'),
    btnToggleSidebar: document.getElementById('btn-toggle-sidebar'),
    btnCloseSidebar: document.getElementById('btn-close-sidebar'),
    
    // Report Filters
    reportYear: document.getElementById('report-year'),
    reportMonth: document.getElementById('report-month'),
    reportCategory: document.getElementById('report-category'),
    reportSavingsTotal: document.getElementById('report-savings-total'),
    
    // Budgets
    budgetProgressContainer: document.getElementById('budget-progress-container'),
    budgetSettingsContainer: document.getElementById('budget-settings-container'),
    
    // User Profile
    userAvatar: document.getElementById('user-avatar'),
    avatarUrlInput: document.getElementById('avatar-url-input'),
    btnSaveAvatar: document.getElementById('btn-save-avatar'),
    
    // Filters
    filterType: document.getElementById('filter-type'),
    filterYear: document.getElementById('filter-year'),
    filterMonth: document.getElementById('filter-month'),
    filterDay: document.getElementById('filter-day'),
    filterCategory: document.getElementById('filter-category'),
    
    // Category Modal
    btnOpenCatModal: document.getElementById('btn-open-category-modal'),
    catModal: document.getElementById('category-modal'),
    catForm: document.getElementById('category-form'),
    btnCloseCatModal: document.getElementById('btn-close-category-modal'),
    btnCancelCatModal: document.getElementById('btn-cancel-category'),
    catIconInput: document.getElementById('cat-icon'),
    catNameInput: document.getElementById('cat-name'),
    catBudgetInput: document.getElementById('cat-budget'),
    budgetInputGroup: document.getElementById('budget-input-group'),
    editCatIdInput: document.getElementById('edit-cat-id'),
    catModalTitle: document.getElementById('cat-modal-title')
};

// Chart Instances
let charts = {
    miniExpense: null,
    cashflow: null,
    trend: null,
    expenseCategory: null
};

// --- Custom Chart Plugins ---
const centerTextPlugin = {
    id: 'centerText',
    afterDraw: (chart) => {
        if (chart.config.type === 'doughnut' && chart.options.plugins.centerText) {
            const { ctx, chartArea: { top, bottom, left, right, width, height } } = chart;
            ctx.save();
            const fontSize = window.innerWidth < 768 ? '14px' : '20px';
            ctx.font = `bold ${fontSize} Outfit`;
            ctx.fillStyle = '#0f172a';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(chart.options.plugins.centerText, left + width / 2, top + height / 2);
            ctx.restore();
        }
    }
};
Chart.register(centerTextPlugin);

// --- Initialization ---
const init = async () => {
    await loadData();
    setupEventListeners();
    updateUI();
    
    // Set current date on header
    const now = new Date();
    document.getElementById('current-date').textContent = `Tháng ${now.getMonth() + 1}, ${now.getFullYear()}`;
    
    // Set default date in form
    els.dateInput.valueAsDate = new Date();
    
    // Init categories dropdown
    populateCategories('expense');
    if(typeof populateFilterCategories === 'function') populateFilterCategories();
    if(typeof populateDateFilters === 'function') populateDateFilters();
    
    // Init settings
    renderSettings();
    renderUserAvatar();
};

const renderUserAvatar = () => {
    if (els.userAvatar) {
        els.userAvatar.src = state.userAvatar || 'https://i.pravatar.cc/150?img=11';
    }
    if (els.avatarUrlInput) {
        els.avatarUrlInput.value = state.userAvatar || '';
    }
};

// --- Event Listeners ---
const setupEventListeners = () => {
    // Tab Navigation
    els.tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = tab.getAttribute('data-tab');
            switchTab(targetId);
        });
    });

    // Modal Triggers
    const openModal = () => els.modal.classList.add('active');
    const closeModal = () => {
        els.modal.classList.remove('active');
        els.form.reset();
        els.dateInput.valueAsDate = new Date();
        document.getElementById('trans-id').value = '';
        document.getElementById('modal-title').textContent = 'Thêm giao dịch';
    };

    els.btnOpenSidebar.addEventListener('click', openModal);
    els.btnOpenPage.addEventListener('click', openModal);
    els.btnCloseModal.addEventListener('click', closeModal);
    els.btnCancelModal.addEventListener('click', closeModal);
    
    if (els.reportYear) els.reportYear.addEventListener('change', renderCharts);
    if (els.reportMonth) els.reportMonth.addEventListener('change', renderCharts);
    if (els.reportCategory) els.reportCategory.addEventListener('change', renderCharts);

    // Sidebar Toggle
    if (els.btnToggleSidebar) {
        els.btnToggleSidebar.addEventListener('click', () => {
            els.sidebar.classList.add('active');
        });
    }

    if (els.btnSaveAvatar) {
        els.btnSaveAvatar.addEventListener('click', () => {
            const url = els.avatarUrlInput.value.trim();
            if (url) {
                state.userAvatar = url;
                saveData();
                renderUserAvatar();
                alert('Đã cập nhật ảnh đại diện!');
            }
        });
    }
    if (els.btnCloseSidebar) {
        els.btnCloseSidebar.addEventListener('click', () => {
            els.sidebar.classList.remove('active');
        });
    }

    // Close sidebar on click outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && els.sidebar.classList.contains('active')) {
            if (!els.sidebar.contains(e.target) && !els.btnToggleSidebar.contains(e.target)) {
                els.sidebar.classList.remove('active');
            }
        }
    });

    // Close modal on click outside
    els.modal.addEventListener('click', (e) => {
        if(e.target === els.modal) closeModal();
    });

    // Handle Form Type Change (Income/Expense)
    els.typeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            populateCategories(e.target.value);
        });
    });

    // Format amount input as user types
    if(els.amountInput) {
        els.amountInput.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            if (value === '') {
                this.value = '';
                return;
            }
            this.value = new Intl.NumberFormat('vi-VN').format(value);
        });
    }

    if(els.catBudgetInput) {
        els.catBudgetInput.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            if (value === '') {
                this.value = '';
                return;
            }
            this.value = new Intl.NumberFormat('vi-VN').format(value);
        });
    }

    // Handle Form Submit
    els.form.addEventListener('submit', (e) => {
        e.preventDefault();
        saveTransaction();
        closeModal();
    });
    
    // Filter Transactions
    if(els.filterType) {
        els.filterType.addEventListener('change', () => {
            if(typeof populateFilterCategories === 'function') populateFilterCategories();
            renderFullTransactionsTable();
        });
    }
    if(els.filterYear) {
        els.filterYear.addEventListener('change', renderFullTransactionsTable);
    }
    if(els.filterMonth) {
        els.filterMonth.addEventListener('change', renderFullTransactionsTable);
    }
    if(els.filterDay) {
        els.filterDay.addEventListener('change', renderFullTransactionsTable);
    }
    if(els.filterCategory) {
        els.filterCategory.addEventListener('change', renderFullTransactionsTable);
    }

    // Settings
    if(els.btnClearData) {
        els.btnClearData.addEventListener('click', () => {
            if(confirm('Bạn có chắc chắn muốn xóa toàn bộ dữ liệu? Hành động này không thể hoàn tác.')) {
                state.transactions = [];
                state.budgets = {};
                saveData();
                updateUI();
                renderSettings();
                alert('Đã xóa dữ liệu!');
            }
        });
    }

    if(els.btnExportData) {
        els.btnExportData.addEventListener('click', () => {
            const dataStr = JSON.stringify(state, null, 2);
            const blob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            const date = new Date().toISOString().split('T')[0];
            link.href = url;
            link.download = `family_finance_backup_${date}.json`;
            link.click();
            URL.revokeObjectURL(url);
        });
    }

    if(els.btnImportData) {
        els.btnImportData.addEventListener('click', () => {
            els.fileImport.click();
        });
    }

    if(els.fileImport) {
        els.fileImport.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const importedState = JSON.parse(event.target.result);
                    
                    // Basic validation
                    if (importedState.transactions && Array.isArray(importedState.transactions)) {
                        if (confirm('Bạn có muốn nạp dữ liệu từ file này? Dữ liệu hiện tại trên máy sẽ bị thay thế.')) {
                            state = importedState;
                            saveData();
                            location.reload(); // Reload to ensure everything is refreshed
                        }
                    } else {
                        alert('File không đúng định dạng dữ liệu của ứng dụng.');
                    }
                } catch (err) {
                    alert('Lỗi khi đọc file. Vui lòng kiểm tra lại file của bạn.');
                }
            };
            reader.readAsText(file);
        });
    }

    // Sync Code Display
    const syncCodeInput = document.getElementById('sync-code-input');
    if (syncCodeInput) syncCodeInput.value = householdId;

    // Category Modal Triggers
    const openCatModal = () => {
        els.catForm.reset();
        els.editCatIdInput.value = '';
        if(els.catBudgetInput) els.catBudgetInput.value = '';
        els.catModalTitle.textContent = 'Thêm hạng mục mới';
        if(els.budgetInputGroup) els.budgetInputGroup.style.display = 'block';
        const radio = document.querySelector('input[name="cat_type"][value="expense"]');
        if (radio) radio.checked = true;
        els.catModal.classList.add('active');
    };
    const closeCatModal = () => {
        els.catModal.classList.remove('active');
        els.catForm.reset();
        els.editCatIdInput.value = '';
    };

    if(els.btnOpenCatModal) els.btnOpenCatModal.addEventListener('click', openCatModal);
    if(els.btnCloseCatModal) els.btnCloseCatModal.addEventListener('click', closeCatModal);
    if(els.btnCancelCatModal) els.btnCancelCatModal.addEventListener('click', closeCatModal);

    if(els.catModal) els.catModal.addEventListener('click', (e) => {
        if(e.target === els.catModal) closeCatModal();
    });

    // Emoji Picker Select logic
    document.querySelectorAll('.emoji-option').forEach(el => {
        el.addEventListener('click', (e) => {
            els.catIconInput.value = e.target.textContent;
        });
    });

    // Handle Category Type Change to hide budget input
    const typeRadiosCat = document.getElementsByName('cat_type');
    typeRadiosCat.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if(els.budgetInputGroup) els.budgetInputGroup.style.display = e.target.value === 'expense' ? 'block' : 'none';
        });
    });

    if(els.catForm) els.catForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const type = document.querySelector('input[name="cat_type"]:checked').value;
        const catId = els.editCatIdInput.value;
        
        let targetId = catId;
        if (catId) {
            // Edit
            const index = state.categories[type].findIndex(c => c.id === catId);
            if (index !== -1) {
                state.categories[type][index].name = els.catNameInput.value;
                state.categories[type][index].icon = els.catIconInput.value;
            }
        } else {
            // Add
            targetId = 'c_' + generateId();
            const newCat = {
                id: targetId,
                name: els.catNameInput.value,
                icon: els.catIconInput.value
            };
            state.categories[type].push(newCat);
        }

        // Handle Budget Save
        if (type === 'expense' && els.catBudgetInput && els.catBudgetInput.value !== '') {
            const val = parseFloat(els.catBudgetInput.value.replace(/\./g, ''));
            if (!isNaN(val) && val >= 0) {
                state.budgets[targetId] = val;
            } else {
                state.budgets[targetId] = 0;
            }
        } else {
             if (type === 'expense') state.budgets[targetId] = 0;
        }

        saveData();
        closeCatModal();
        populateCategories(document.querySelector('input[name="type"]:checked').value);
        renderSettings();
        updateUI();
        alert(catId ? 'Đã cập nhật hạng mục!' : 'Đã thêm hạng mục mới thành công!');
    });
};

// --- Exposure to Global (for onclick events) ---
window.editTransaction = (id) => {
    const t = state.transactions.find(t => t.id === id);
    if(!t) return;
    
    document.getElementById('trans-id').value = t.id;
    els.amountInput.value = new Intl.NumberFormat('vi-VN').format(t.amount);
    
    const typeRadio = document.querySelector(`input[name="type"][value="${t.type}"]`);
    if(typeRadio) {
        typeRadio.checked = true;
        populateCategories(t.type);
    }
    
    els.categorySelect.value = t.categoryId;
    els.dateInput.value = t.date;
    els.noteInput.value = t.note;
    
    document.getElementById('modal-title').textContent = 'Chỉnh sửa giao dịch';
    els.modal.classList.add('active');
};

window.deleteTransaction = (id) => {
    if(confirm('Bạn có chắc chắn muốn xóa giao dịch này?')) {
        state.transactions = state.transactions.filter(t => t.id !== id);
        saveData();
        updateUI();
    }
};

window.editCategory = (id, type) => {
    const cat = state.categories[type].find(c => c.id === id);
    if (!cat) return;
    
    const radio = document.querySelector(`input[name="cat_type"][value="${type}"]`);
    if(radio) radio.checked = true;
    
    els.editCatIdInput.value = cat.id;
    els.catIconInput.value = cat.icon;
    els.catNameInput.value = cat.name;

    if (type === 'expense' && state.budgets && state.budgets[id]) {
        els.catBudgetInput.value = new Intl.NumberFormat('vi-VN').format(state.budgets[id]);
    } else {
        els.catBudgetInput.value = '';
    }
    
    if (els.budgetInputGroup) {
        els.budgetInputGroup.style.display = type === 'expense' ? 'block' : 'none';
    }

    els.catModalTitle.textContent = 'Chỉnh sửa hạng mục';
    els.catModal.classList.add('active');
};

window.deleteCategory = (id, type) => {
    if(confirm(`Bạn có chắc muốn xóa hạng mục này? Các giao dịch cũ sẽ được chuyển vào mục "Khác".`)) {
        // Move transactions to 'other'
        state.transactions.forEach(t => {
            if(t.categoryId === id) t.categoryId = 'other';
        });
        
        // Remove from state
        state.categories[type] = state.categories[type].filter(c => c.id !== id);
        if(state.budgets[id]) delete state.budgets[id];
        
        saveData();
        updateUI();
        renderSettings();
    }
};

// --- Navigation ---
const switchTab = (tabId) => {
    // Update active logic
    els.tabs.forEach(t => t.classList.remove('active'));
    const activeTab = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
    if(activeTab) activeTab.classList.add('active');

    els.tabContents.forEach(c => c.classList.remove('active'));
    const activeContent = document.getElementById(`tab-${tabId}`);
    if(activeContent) activeContent.classList.add('active');

    // Page Subject Title Update
    const pageTitle = document.getElementById('page-title');
    if(pageTitle) {
        const titles = {
            'dashboard': 'Tổng quan',
            'transactions': 'Lịch sử giao dịch',
            'reports': 'Báo cáo thông minh',
            'settings': 'Cài đặt hệ thống'
        };
        pageTitle.textContent = titles[tabId];
    }

    // Set universal theme class
    document.body.className = `antigravity-theme`;

    // Auto-close sidebar on mobile
    if (window.innerWidth <= 768 && els.sidebar) {
        els.sidebar.classList.remove('active');
    }

    // Rerender charts if needed
    if(tabId === 'reports' || tabId === 'dashboard') {
        renderCharts();
    }
    
    updateUI();
};

// --- Form Logic ---
const populateDateFilters = () => {
    if(els.filterYear || els.reportYear) {
        const years = [];
        for(let y = 2020; y <= 2035; y++) years.push(y);
        
        [els.filterYear, els.reportYear].forEach(select => {
            if(!select) return;
            const originalVal = select.id === 'filter-year' ? 'Năm: Tất cả' : 'Tất cả các năm';
            select.innerHTML = `<option value="all">${originalVal}</option>`;
            years.forEach(y => {
                const opt = document.createElement('option');
                opt.value = y;
                opt.textContent = `Năm ${y}`;
                if (y === new Date().getFullYear()) opt.selected = true;
                select.appendChild(opt);
            });
        });
    }
    if(els.filterDay) {
        for(let d = 1; d <= 31; d++) {
            const opt = document.createElement('option');
            opt.value = d;
            opt.textContent = `Ngày ${d}`;
            els.filterDay.appendChild(opt);
        }
    }
};

const populateFilterCategories = () => {
    // 1. Transaction Tab Filters
    if(els.filterCategory) {
        const filterTypeValue = els.filterType.value;
        els.filterCategory.innerHTML = '<option value="all">Danh mục: Tất cả</option>';
        
        const addOptions = (type, target) => {
            state.categories[type].forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = `${cat.icon} ${cat.name}`;
                target.appendChild(option);
            });
        };

        if (filterTypeValue === 'all') {
            addOptions('expense', els.filterCategory);
            addOptions('income', els.filterCategory);
        } else {
            addOptions(filterTypeValue, els.filterCategory);
        }
    }

    // 2. Report Tab Filters
    if(els.reportCategory) {
        els.reportCategory.innerHTML = '<option value="all">Tất cả danh mục</option>';
        state.categories.expense.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = `Chi: ${cat.icon} ${cat.name}`;
            els.reportCategory.appendChild(opt);
        });
        state.categories.income.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = `Thu: ${cat.icon} ${cat.name}`;
            els.reportCategory.appendChild(opt);
        });
        state.categories.debt.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = `Nợ: ${cat.icon} ${cat.name}`;
            els.reportCategory.appendChild(opt);
        });
    }
};

const populateCategories = (type) => {
    els.categorySelect.innerHTML = '';
    state.categories[type].forEach(cat => {
        const option = document.createElement('option');
        option.value = cat.id;
        option.textContent = cat.name;
        els.categorySelect.appendChild(option);
    });
};

const saveTransaction = () => {
    const type = document.querySelector('input[name="type"]:checked').value;
    const transIdStr = document.getElementById('trans-id').value;
    
    const transData = {
        type: type,
        amount: parseFloat(els.amountInput.value.replace(/\./g, '')),
        categoryId: els.categorySelect.value,
        date: els.dateInput.value,
        note: els.noteInput.value
    };

    if (transIdStr) {
        // Update existing
        transData.id = transIdStr;
        const index = state.transactions.findIndex(t => t.id === transIdStr);
        if(index !== -1) {
            state.transactions[index] = transData;
        }
    } else {
        // Add new
        transData.id = generateId();
        state.transactions.push(transData);
    }
    
    // Sort descending by date
    state.transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    saveData();
    updateUI();
};

// --- Rendering View ---
const updateUI = () => {
    calculateSummary();
    renderRecentTransactions();
    renderFullTransactionsTable();
    renderCharts();
    renderBudgetProgress();
};

const renderSettings = () => {
    if(!els.budgetSettingsContainer) return;
    els.budgetSettingsContainer.innerHTML = '';
    state.categories.expense.forEach(cat => {
        const val = state.budgets ? state.budgets[cat.id] : 0;
        const html = `
            <div class="form-group" style="margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <label style="display:flex; align-items:center; gap:8px;">
                    <span class="emoji-icon mini">${cat.icon}</span> ${cat.name}
                    <div style="margin-left:auto; display:flex; gap:4px; align-items:center;">
                        <button class="edit-btn" onclick="editCategory('${cat.id}', 'expense')" style="padding:4px 8px; font-size:16px; display:flex; align-items:center; gap:4px; font-weight:normal;" title="Chỉnh sửa"><i class="ph ph-pencil-simple"></i> Cập nhật</button>
                        <button class="icon-btn" onclick="deleteCategory('${cat.id}', 'expense')" style="color:var(--danger-color); padding:4px 8px; font-size:16px; border-radius:4px;" title="Xóa"><i class="ph ph-trash"></i></button>
                    </div>
                </label>
                <div style="color:var(--text-muted); font-size:14px; display:flex; align-items:center; gap:8px; margin-top:8px;">
                    <i class="ph ph-coins"></i>Hạn mức hàng tháng:
                    <strong style="color:var(--text);">${val ? new Intl.NumberFormat('vi-VN').format(val) + ' đ' : 'Không giới hạn'}</strong>
                </div>
            </div>
        `;
        els.budgetSettingsContainer.insertAdjacentHTML('beforeend', html);
    });
};

const renderBudgetProgress = () => {
    if(!els.budgetProgressContainer) return;
    els.budgetProgressContainer.innerHTML = '';
    
    const expTotals = {};
    let otherSpent = 0;

    const now = new Date();
    const curMonth = now.getMonth();
    const curYear = now.getFullYear();

    state.transactions.filter(t => {
        const d = new Date(t.date);
        return t.type === 'expense' && d.getMonth() === curMonth && d.getFullYear() === curYear;
    }).forEach(t => {
        const cat = getCategoryById('expense', t.categoryId);
        if (cat.id === 'other') {
            otherSpent += t.amount;
        } else {
            expTotals[cat.id] = (expTotals[cat.id] || 0) + t.amount;
        }
    });

    let hasBudgets = false;
    
    // Group all categories to display
    const categoriesToDisplay = [...state.categories.expense];
    if (otherSpent > 0) {
        categoriesToDisplay.push({ id: 'other', name: 'Khác', icon: '❓' });
    }

    categoriesToDisplay.forEach(cat => {
        const budget = state.budgets ? (state.budgets[cat.id] || 0) : 0;
        const spent = cat.id === 'other' ? otherSpent : (expTotals[cat.id] || 0);
        
        // Show if it has a budget assigned OR if there's spending
        if (budget > 0 || spent > 0) {
            hasBudgets = true;
            let percent = 0;
            let colorClass = 'safe';
            
            if (budget > 0) {
                percent = Math.min((spent / budget) * 100, 100);
                if (percent >= 100) colorClass = 'danger';
                else if (percent >= 80) colorClass = 'warning';
            }
            
            const budgetText = budget > 0 ? formatCurrency(budget) : 'Không giới hạn';
            
            const html = `
                <div class="budget-item">
                    <div class="budget-header">
                        <div class="budget-cat"><span class="emoji-icon mini">${cat.icon}</span> ${cat.name}</div>
                        <div class="budget-amounts">
                            <span class="${(budget > 0 && percent >= 100) ? 'danger-text' : ''}">${formatCurrency(spent)}</span> / ${budgetText}
                        </div>
                    </div>
                    <div class="progress-bg">
                        <div class="progress-fill ${colorClass}" style="width: ${percent}%"></div>
                    </div>
                </div>
            `;
            els.budgetProgressContainer.insertAdjacentHTML('beforeend', html);
        }
    });

    if (!hasBudgets) {
        els.budgetProgressContainer.innerHTML = '<div class="empty-state" style="text-align:center; padding:20px; color:var(--text-muted);">Chưa có giao dịch hoặc hạn mức nào được thiết lập.</div>';
    }
};

const calculateSummary = () => {
    let incomeMonthly = 0;
    let expenseMonthly = 0;
    let incomePrev = 0;
    let expensePrev = 0;

    const now = new Date();
    const curMonth = now.getMonth();
    const curYear = now.getFullYear();
    const firstOfCurrentMonth = new Date(curYear, curMonth, 1);

    state.transactions.forEach(t => {
        const d = new Date(t.date);
        const isThisMonth = d.getMonth() === curMonth && d.getFullYear() === curYear;

        if (t.type === 'income') {
            if (isThisMonth) incomeMonthly += t.amount;
            if (d < firstOfCurrentMonth) incomePrev += t.amount;
        } else if (t.type === 'expense') {
            if (isThisMonth) expenseMonthly += t.amount;
            if (d < firstOfCurrentMonth) expensePrev += t.amount;
        } else if (t.type === 'debt') {
            // Cho vay (loan) & Trả nợ (repay) -> Tiền ra (giống Chi tiêu)
            // Đi vay (borrow) & Thu nợ (recover) -> Tiền vào (giống Thu nhập)
            if (t.categoryId === 'debt_loan' || t.categoryId === 'debt_repay') {
                if (isThisMonth) expenseMonthly += t.amount;
                if (d < firstOfCurrentMonth) expensePrev += t.amount;
            } else {
                if (isThisMonth) incomeMonthly += t.amount;
                if (d < firstOfCurrentMonth) incomePrev += t.amount;
            }
        }
    });

    const savingsPrevious = incomePrev - expensePrev;
    const balanceCurrent = incomeMonthly - expenseMonthly;

    // Update labels with current month name
    const monthNames = ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6", "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"];
    const monthStr = monthNames[curMonth];
    
    if (els.labelIncomeMonth) els.labelIncomeMonth.textContent = `Thu nhập ${monthStr}`;
    if (els.labelExpenseMonth) els.labelExpenseMonth.textContent = `Chi tiêu ${monthStr}`;
    if (els.labelBalanceMonth) els.labelBalanceMonth.textContent = `Số dư ${monthStr}`;

    if (els.totalIncome) els.totalIncome.textContent = formatCurrency(incomeMonthly);
    if (els.totalExpense) els.totalExpense.textContent = formatCurrency(expenseMonthly);
    if (els.savingsPrevious) els.savingsPrevious.textContent = formatCurrency(savingsPrevious);
    if (els.totalBalanceCurrent) els.totalBalanceCurrent.textContent = formatCurrency(balanceCurrent);
    
    // Display household ID for confirmation in Sidebar
    const displayId = document.getElementById('display-household-id');
    if (displayId) displayId.textContent = householdId;
};

// Mini list in Dashboard
const renderRecentTransactions = () => {
    els.recentTransactions.innerHTML = '';
    
    if (state.transactions.length === 0) {
        els.recentTransactions.innerHTML = '<div class="empty-state" style="text-align:center; padding:20px; color:var(--text-muted);">Không có giao dịch nào</div>';
        return;
    }

    const recent = state.transactions.slice(0, 5); // Take top 5

    recent.forEach(t => {
        const cat = getCategoryById(t.type, t.categoryId);
        const html = `
            <div class="transaction-item">
                <div class="trans-left">
                    <div class="trans-icon ${t.type}">
                        <span class="emoji-icon">${cat.icon}</span>
                    </div>
                    <div class="trans-details">
                        <h4>${t.note}</h4>
                        <span class="trans-cat">${cat.name}</span>
                    </div>
                </div>
                <div class="trans-right">
                    <div class="trans-amount ${isTransactionPositive(t) ? 'positive-text' : 'negative-text'}">
                        ${isTransactionPositive(t) ? '+' : '-'}${formatCurrency(t.amount)}
                    </div>
                    <div class="trans-date">${formatDate(t.date)}</div>
                </div>
            </div>
        `;
        els.recentTransactions.insertAdjacentHTML('beforeend', html);
    });
};

// Full table in Transactions Tab
const renderFullTransactionsTable = () => {
    els.transactionsBody.innerHTML = '';
    
    const filterTy = els.filterType ? els.filterType.value : 'all';
    const filterYr = els.filterYear ? els.filterYear.value : 'all';
    const filterMo = els.filterMonth ? els.filterMonth.value : 'all';
    const filterDa = els.filterDay ? els.filterDay.value : 'all';
    const filterCat = els.filterCategory ? els.filterCategory.value : 'all';

    let filteredList = state.transactions;
    
    if (filterTy !== 'all') {
        filteredList = filteredList.filter(t => t.type === filterTy);
    }
    
    if (filterCat !== 'all') {
        filteredList = filteredList.filter(t => t.categoryId === filterCat);
    }

    filteredList = filteredList.filter(t => {
        const tDate = new Date(t.date);
        const matchYear = filterYr === 'all' || Math.floor(filterYr) === tDate.getFullYear();
        const matchMonth = filterMo === 'all' || Math.floor(filterMo) === (tDate.getMonth() + 1);
        const matchDay = filterDa === 'all' || Math.floor(filterDa) === tDate.getDate();

        return matchYear && matchMonth && matchDay;
    });

    if (filteredList.length === 0) {
        els.transactionsBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted); padding:30px;">Không có dữ liệu</td></tr>`;
        return;
    }

    filteredList.forEach(t => {
        const cat = getCategoryById(t.type, t.categoryId);
        const amountClass = isTransactionPositive(t) ? 'positive-text' : 'negative-text';
        const operator = isTransactionPositive(t) ? '+' : '-';
        
        const html = `
            <tr>
                <td><strong>${t.note}</strong></td>
                <td><span style="display:flex; align-items:center; gap:8px;"><span class="emoji-icon mini">${cat.icon}</span> ${cat.name}</span></td>
                <td style="color:var(--text-muted);">${formatDate(t.date)}</td>
                <td class="text-right ${amountClass}" style="font-weight: 600; font-family: var(--font-heading)">
                    ${operator}${formatCurrency(t.amount)}
                </td>
                <td class="text-right">
                    <button class="edit-btn" onclick="editTransaction('${t.id}')" style="margin-right: 8px;">
                        <i class="ph ph-pencil-simple"></i>
                    </button>
                    <button class="delete-btn" onclick="deleteTransaction('${t.id}')">
                        <i class="ph ph-trash"></i>
                    </button>
                </td>
            </tr>
        `;
        els.transactionsBody.insertAdjacentHTML('beforeend', html);
    });
};

// --- Chart.js Integration ---
const renderCharts = () => {
    Chart.defaults.color = '#0f172a';
    Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.05)';
    Chart.defaults.font.family = 'Inter';

    const rYear = els.reportYear ? els.reportYear.value : 'all';
    const rMonth = els.reportMonth ? els.reportMonth.value : 'all';
    const rCat = els.reportCategory ? els.reportCategory.value : 'all';

    // Data Filtering for Reports
    const filteredTransactions = state.transactions.filter(t => {
        const d = new Date(t.date);
        const matchYear = rYear === 'all' || d.getFullYear() === parseInt(rYear);
        const matchMonth = rMonth === 'all' || d.getMonth() === parseInt(rMonth);
        const matchCat = rCat === 'all' || t.categoryId === rCat;
        return matchYear && matchMonth && matchCat;
    });

    // Calculate report savings
    let rInc = 0, rExp = 0;
    filteredTransactions.forEach(t => {
        if (t.type === 'income') rInc += t.amount;
        else if (t.type === 'expense') rExp += t.amount;
        else if (t.type === 'debt') {
            if (t.categoryId === 'debt_loan' || t.categoryId === 'debt_repay') rExp += t.amount;
            else rInc += t.amount;
        }
    });
    if(els.reportSavingsTotal) els.reportSavingsTotal.textContent = formatCurrency(rInc - rExp);

    // Filtered Expenses for Doughnut (Include Debt-related expenses)
    const expenses = filteredTransactions.filter(t => {
        const isDebtExp = (t.type === 'debt' && (t.categoryId === 'debt_loan' || t.categoryId === 'debt_repay'));
        return t.type === 'expense' || isDebtExp;
    });

    // Setup Category Data
    const expenseByCategory = {};
    expenses.forEach(t => {
        const catObj = getCategoryById(t.type, t.categoryId);
        const catName = catObj.name;
        expenseByCategory[catName] = (expenseByCategory[catName] || 0) + t.amount;
    });

    const categories = Object.keys(expenseByCategory);
    const amounts = Object.values(expenseByCategory);
    const totalExpValue = amounts.reduce((a, b) => a + b, 0);
    
    // Vibrant & Diverse Palette for better identification
    const palette = [
        '#CB5A32', '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', 
        '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
        '#14b8a6', '#f43f5e', '#fbbf24', '#22c55e'
    ];

    // Destroy existing charts
    if(charts.miniExpense) charts.miniExpense.destroy();
    if(charts.expenseCategory) charts.expenseCategory.destroy();
    if(charts.cashflow) charts.cashflow.destroy();
    if(charts.trend) charts.trend.destroy();

    // Timeline Aggregation Logic
    let timeLabels = [];
    let incTimeData = [];
    let expTimeData = [];

    if (rMonth !== 'all') { // Daily grouping for specific month
        const y = rYear !== 'all' ? parseInt(rYear) : new Date().getFullYear();
        const m = parseInt(rMonth);
        const daysInMonth = new Date(y, m + 1, 0).getDate();
        for (let i = 1; i <= daysInMonth; i++) {
            timeLabels.push(`${i}`); // Just the day number
            incTimeData.push(0);
            expTimeData.push(0);
        }
        filteredTransactions.forEach(t => {
            const d = new Date(t.date);
            const dayIdx = d.getDate() - 1;
            if (t.type === 'income') incTimeData[dayIdx] += t.amount;
            else if (t.type === 'expense') expTimeData[dayIdx] += t.amount;
            else if (t.type === 'debt') {
                if (t.categoryId === 'debt_loan' || t.categoryId === 'debt_repay') expTimeData[dayIdx] += t.amount;
                else incTimeData[dayIdx] += t.amount;
            }
        });
    } else { // Monthly grouping
        if (rYear !== 'all') {
            const y = parseInt(rYear);
            for (let i = 1; i <= 12; i++) {
                timeLabels.push(`T${i}/${y}`);
                incTimeData.push(0);
                expTimeData.push(0);
            }
            filteredTransactions.forEach(t => {
                const d = new Date(t.date);
                const monthIdx = d.getMonth();
                if (t.type === 'income') incTimeData[monthIdx] += t.amount;
                else if (t.type === 'expense') expTimeData[monthIdx] += t.amount;
                else if (t.type === 'debt') {
                    if (t.categoryId === 'debt_loan' || t.categoryId === 'debt_repay') expTimeData[monthIdx] += t.amount;
                    else incTimeData[monthIdx] += t.amount;
                }
            });
        } else {
            // All years dynamically grouped by YYYY-MM
            const grouped = {};
            filteredTransactions.forEach(t => {
                const d = new Date(t.date);
                const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
                if (!grouped[key]) grouped[key] = { inc: 0, exp: 0 };
                if (t.type === 'income') grouped[key].inc += t.amount;
                else if (t.type === 'expense') grouped[key].exp += t.amount;
                else if (t.type === 'debt') {
                    if (t.categoryId === 'debt_loan' || t.categoryId === 'debt_repay') grouped[key].exp += t.amount;
                    else grouped[key].inc += t.amount;
                }
            });
            const sortedKeys = Object.keys(grouped).sort();
            if (sortedKeys.length === 0) {
                const d = new Date();
                const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
                sortedKeys.push(key);
                grouped[key] = { inc: 0, exp: 0 };
            }
            sortedKeys.forEach(k => {
                const parts = k.split('-');
                timeLabels.push(`T${parseInt(parts[1])}/${parts[0]}`);
                incTimeData.push(grouped[k].inc);
                expTimeData.push(grouped[k].exp);
            });
        }
    }

    // Dynamic Title for Expense Category Chart
    let timeLabelStr = '';
    if (rYear === 'all' && rMonth === 'all') timeLabelStr = '(Tất cả các năm)';
    else if (rYear !== 'all' && rMonth === 'all') timeLabelStr = `(Năm ${rYear})`;
    else if (rYear === 'all' && rMonth !== 'all') timeLabelStr = `(Tháng ${parseInt(rMonth)+1})`;
    else timeLabelStr = `(T${parseInt(rMonth)+1}/${rYear})`;
    
    const expenseCatTitle = document.getElementById('expense-cat-title');
    if (expenseCatTitle) expenseCatTitle.textContent = timeLabelStr;

    // 1. Mini Expense Chart (Dashboard - Always current month)
    const ctx1 = document.getElementById('miniExpenseChart');
    if(ctx1) {
        const now = new Date();
        const d_expenses = state.transactions.filter(t => {
            const d = new Date(t.date);
            const isDebtExp = (t.type === 'debt' && (t.categoryId === 'debt_loan' || t.categoryId === 'debt_repay'));
            return (t.type === 'expense' || isDebtExp) && d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
        });
        const d_catData = {};
        d_expenses.forEach(t => {
            const n = getCategoryById(t.type, t.categoryId).name;
            d_catData[n] = (d_catData[n] || 0) + t.amount;
        });

        const d_labels = Object.keys(d_catData);
        const d_amounts = Object.values(d_catData);
        const d_total = d_amounts.reduce((a, b) => a + b, 0);

        charts.miniExpense = new Chart(ctx1, {
            type: 'doughnut',
            data: {
                labels: d_labels.length > 0 ? d_labels : ['Chưa có dữ liệu'],
                datasets: [{
                    data: d_amounts.length > 0 ? d_amounts : [1],
                    backgroundColor: d_amounts.length > 0 ? palette : ['#f1f5f9'],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '55%',
                plugins: {
                    legend: { 
                        display: true, 
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            padding: 10,
                            font: { size: 11 }
                        }
                    },
                    centerText: d_total > 0 ? formatCurrency(d_total) : '0 ₫'
                }
            }
        });
    }

    // 2. Full Expense Category Chart (Reports - Filtered)
    const ctx2 = document.getElementById('expenseCategoryChart');
    if(ctx2) {
        charts.expenseCategory = new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: categories.length > 0 ? categories : ['Không có dữ liệu'],
                datasets: [{
                    data: categories.length > 0 ? amounts : [1],
                    backgroundColor: categories.length > 0 ? palette : ['#f1f5f9'],
                    borderWidth: 1,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '55%',
                plugins: {
                    legend: { position: 'bottom' },
                    centerText: totalExpValue > 0 ? formatCurrency(totalExpValue) : '0 ₫',
                    tooltip: {
                        backgroundColor: 'rgba(255, 255, 255, 0.85)',
                        titleColor: '#0f172a',
                        bodyColor: '#0f172a',
                        borderColor: 'rgba(255, 255, 255, 0.6)',
                        borderWidth: 1,
                        padding: 12,
                        boxPadding: 4,
                        usePointStyle: true,
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) label += ': ';
                                if (context.parsed !== null) {
                                    label += new Intl.NumberFormat('vi-VN').format(context.parsed) + ' ₫';
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }

    // 3. Cashflow Chart (Grouped Bar Chart - Filtered)
    const ctx3 = document.getElementById('cashflowChart');
    if (ctx3) {
        charts.cashflow = new Chart(ctx3, {
            type: 'bar',
            data: {
                labels: timeLabels,
                datasets: [
                    {
                        label: 'Thu nhập',
                        data: incTimeData,
                        backgroundColor: '#34d399', // Mint
                        borderRadius: { topLeft: 6, topRight: 6, bottomLeft: 0, bottomRight: 0 },
                        barPercentage: 0.8,
                        categoryPercentage: 0.9
                    },
                    {
                        label: 'Chi tiêu',
                        data: expTimeData,
                        backgroundColor: '#ffb3a7', // Pastel Peach/Orange
                        borderRadius: { topLeft: 6, topRight: 6, bottomLeft: 0, bottomRight: 0 },
                        barPercentage: 0.8,
                        categoryPercentage: 0.9
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            autoSkip: timeLabels.length > 15,
                            maxTicksLimit: 12,
                            maxRotation: 0,
                            minRotation: 0,
                            font: { size: 10 }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        backgroundColor: 'rgba(255, 255, 255, 0.8)',
                        titleColor: '#0f172a',
                        bodyColor: '#0f172a',
                        borderColor: 'rgba(255,255,255,0.5)',
                        borderWidth: 1,
                        padding: 10,
                        boxPadding: 4,
                        usePointStyle: true,
                        callbacks: {
                            title: function(context) {
                                if (rMonth !== 'all') {
                                    return `Ngày ${context[0].label}/${parseInt(rMonth)+1}/${rYear !== 'all' ? rYear : new Date().getFullYear()}`;
                                }
                                return context[0].label;
                            }
                        }
                    }
                }
            }
        });
    }

    // 4. Trend Chart (Spline Area Chart - Filtered)
    const ctx4 = document.getElementById('trendChart');
    if (ctx4) {
        charts.trend = new Chart(ctx4, {
            type: 'line',
            data: {
                labels: timeLabels,
                datasets: [
                    {
                        label: 'Thu nhập',
                        data: incTimeData,
                        borderColor: '#10b981', // Stronger Mint
                        backgroundColor: 'rgba(16, 185, 129, 0.25)', // Transparent Mint fill
                        fill: true,
                        tension: 0.4, // Make it a spline curve
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#10b981'
                    },
                    {
                        label: 'Chi tiêu',
                        data: expTimeData,
                        borderColor: '#f97316', // Stronger Peach
                        backgroundColor: 'rgba(249, 115, 22, 0.25)', // Transparent Peach fill
                        fill: true,
                        tension: 0.4, // Make it a spline curve
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#f97316'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false, // Tooltip shows for all datasets at the vertical line
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            autoSkip: timeLabels.length > 15,
                            maxTicksLimit: 12,
                            maxRotation: 0,
                            minRotation: 0,
                            font: { size: 10 }
                        }
                    }
                },
                plugins: {
                    tooltip: { // Glassmorphism style tooltip
                        backgroundColor: 'rgba(255, 255, 255, 0.85)',
                        titleColor: '#0f172a',
                        bodyColor: '#0f172a',
                        borderColor: 'rgba(255, 255, 255, 0.6)',
                        borderWidth: 1,
                        padding: 12,
                        boxPadding: 6,
                        usePointStyle: true,
                        callbacks: {
                            title: function(context) {
                                if (rMonth !== 'all') {
                                    return `Ngày ${context[0].label}/${parseInt(rMonth)+1}/${rYear !== 'all' ? rYear : new Date().getFullYear()}`;
                                }
                                return context[0].label;
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('vi-VN').format(context.parsed.y) + ' ₫';
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
};

// Start App
document.addEventListener('DOMContentLoaded', init);
