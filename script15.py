import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Try ascii matching in case of encoding differences
old_savings_dashboard = '''                        <div class="card-icon" style="color: var(--primary); background: var(--primary-light);"><i class="ph ph-piggy-bank"></i></div>
                        <span class="card-label">Tích lũy</span>
                        <div class="card-amount" id="savings-previous">0 ₫</div>
                    </div>'''
new_savings_dashboard = '''                        <div class="card-icon" style="color: var(--primary); background: var(--primary-light);"><i class="ph ph-piggy-bank"></i></div>
                        <span class="card-label">Tích lũy</span>
                        <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                            <div class="card-amount" id="savings-previous">0 ₫</div>
                            <button onclick="if(window.openWithdrawSavingsModal) window.openWithdrawSavingsModal()" class="btn btn-secondary small" style="padding:4px 8px; font-size:12px; background:var(--primary-light); color:var(--primary); margin-bottom:2px;" title="Rút tiền"><i class="ph ph-hand-coins"></i> Rút</button>
                        </div>
                    </div>'''

if old_savings_dashboard in html:
    html = html.replace(old_savings_dashboard, new_savings_dashboard)
else:
    # try regex
    html = re.sub(
        r'<div class="card-amount" id="savings-previous">.*?</div>\s*</div>',
        r'<div style="display:flex; justify-content:space-between; align-items:flex-end;"><div class="card-amount" id="savings-previous">0 ₫</div><button onclick="if(window.openWithdrawSavingsModal) window.openWithdrawSavingsModal()" class="btn btn-secondary small" style="padding:4px 8px; font-size:12px; background:var(--primary-light); color:var(--primary); margin-bottom:2px;" title="Rút tiền"><i class="ph ph-hand-coins"></i> Rút</button></div></div>',
        html, flags=re.DOTALL
    )

# 2. Update asset-app-balance in Total Assets card
old_asset_balance = '''<strong id="asset-app-balance" style="color:var(--success);">0 ₫</strong>
                            </div>'''
new_asset_balance = '''<div style="display:flex; align-items:center; gap:8px;">
                                    <strong id="asset-app-balance" style="color:var(--success);">0 ₫</strong>
                                    <button onclick="if(window.openWithdrawSavingsModal) window.openWithdrawSavingsModal()" class="btn btn-secondary small" style="padding: 2px 6px; font-size:12px; background:var(--primary-light); color:var(--primary);" title="Rút tiền"><i class="ph ph-hand-coins"></i></button>
                                </div>
                            </div>'''

if old_asset_balance in html:
    html = html.replace(old_asset_balance, new_asset_balance)
else:
    html = re.sub(
        r'<strong id="asset-app-balance".*?</strong>\s*</div>',
        r'<div style="display:flex; align-items:center; gap:8px;"><strong id="asset-app-balance" style="color:var(--success);">0 ₫</strong><button onclick="if(window.openWithdrawSavingsModal) window.openWithdrawSavingsModal()" class="btn btn-secondary small" style="padding: 2px 6px; font-size:12px; background:var(--primary-light); color:var(--primary);" title="Rút tiền"><i class="ph ph-hand-coins"></i></button></div></div>',
        html, flags=re.DOTALL
    )

# 3. Insert Modal HTML right before </body>
modal_html = '''
    <!-- Withdraw Savings Modal -->
    <div id="withdraw-savings-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; justify-content:center; align-items:center;">
        <div class="card glass-panel form-card" style="width: 400px; max-width:90%; padding:20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
            <h3 style="margin-top:0; color:var(--primary); font-size:18px; margin-bottom:15px; display:flex; align-items:center; gap:8px;">
                <i class="ph ph-hand-coins"></i> Rút tiền từ Tích Lũy
            </h3>
            <p style="font-size:13px; color:var(--text-muted); margin-bottom:15px; line-height:1.5;">Khoản rút này sẽ được cộng vào Thu nhập tháng hiện tại của bạn.</p>
            
            <div style="margin-bottom:15px;">
                <label style="display:block; margin-bottom:5px; font-weight:500; font-size:13px;">Số tiền rút (VND) <span style="color:red;">*</span></label>
                <div style="display:flex; gap:8px;">
                    <input type="text" id="withdraw-savings-amount" class="glass-input" placeholder="Ví dụ: 3.000.000" style="flex:1;">
                    <button id="btn-withdraw-savings-all" class="btn btn-secondary" style="padding:0 12px; font-size:13px; background:var(--primary-light); color:var(--primary);">Rút toàn bộ</button>
                </div>
            </div>
            
            <div style="margin-bottom:15px;">
                <label style="display:block; margin-bottom:5px; font-weight:500; font-size:13px;">Ngày thao tác</label>
                <input type="date" id="withdraw-savings-date" class="glass-input" style="width:100%;">
            </div>
            
            <div style="margin-bottom:20px;">
                <label style="display:block; margin-bottom:5px; font-weight:500; font-size:13px;">Ghi chú</label>
                <input type="text" id="withdraw-savings-note" class="glass-input" value="Rút từ Tích lũy cũ" style="width:100%;">
            </div>
            
            <div style="display:flex; justify-content:flex-end; gap:10px;">
                <button onclick="if(window.closeWithdrawSavingsModal) window.closeWithdrawSavingsModal()" class="btn btn-secondary" style="background:transparent; border:1px solid var(--card-border);">Hủy</button>
                <button onclick="if(window.confirmWithdrawSavings) window.confirmWithdrawSavings()" class="btn btn-primary">Xác nhận</button>
            </div>
        </div>
    </div>
</body>'''

html = html.replace('</body>', modal_html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Success script 15 index.html')
