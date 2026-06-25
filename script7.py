import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the manual price section in index.html
old_html = '''                            <!-- Gi b?c th? cng theo t?ng don v? -->
                            <div class="form-group" style="margin-top:20px;">
                                <label style="color:var(--primary); font-weight:600;"><i class="ph ph-tag"></i> Gi b?c th? tru?ng (VND)</label>
                                
                                <div style="display:flex; flex-direction:column; gap:8px; margin-top:8px;">
                                    <div style="display:flex; gap:8px; align-items:center;">
                                        <span style="width: 60px; font-size: 13px; font-weight: 500;">/ Kg:</span>
                                        <input type="text" id="manual-silver-price-kg" class="glass-input" placeholder="Gi 1 Kg b?c..." style="flex:1;">
                                    </div>
                                    <div style="display:flex; gap:8px; align-items:center;">
                                        <span style="width: 60px; font-size: 13px; font-weight: 500;">/ Lu?ng:</span>
                                        <input type="text" id="manual-silver-price-cay" class="glass-input" placeholder="Gi 1 lu?ng b?c..." style="flex:1;">
                                    </div>
                                    <div style="display:flex; gap:8px; align-items:center;">
                                        <span style="width: 60px; font-size: 13px; font-weight: 500;">/ Ch?:</span>
                                        <input type="text" id="manual-silver-price-chi" class="glass-input" placeholder="Gi 1 ch? b?c..." style="flex:1;">
                                    </div>
                                </div>

                                <button id="btn-save-silver-price" class="btn btn-primary w-full" style="margin-top:12px; height:42px; font-size:13px; font-weight:600; justify-content:center;">
                                    <i class="ph ph-floppy-disk"></i> Luu b? gi b?c
                                </button>
                            </div>

                            <!-- K?t qu? quy d?i -->
                            <div id="silver-calc-breakdown" style="margin-top:16px; padding:14px; background:var(--primary-light); border-radius:12px; border:1px solid var(--primary); font-size:13px; line-height:1.8; display:none;"></div>'''

# Fallback for old_html using regex if encoding issues
old_html_regex = r'<!-- Giá bạc thủ công theo từng đơn vị -->.*?<div id="silver-calc-breakdown".*?</div>'

new_html = '''                            <!-- Giá bạc thủ công 1 đơn vị -->
                            <div class="form-group" style="margin-top:20px;">
                                <label style="color:var(--primary); font-weight:600;" id="silver-price-label"><i class="ph ph-tag"></i> Giá bạc (VND / Chỉ)</label>
                                
                                <div style="display:flex; gap:8px; margin-top:8px;">
                                    <input type="text" id="manual-silver-price" class="glass-input" placeholder="Nhập giá..." style="flex:1;">
                                    <button id="btn-save-silver-price" class="btn btn-primary" style="padding:0 14px; height:42px; font-size:12px; white-space:nowrap; flex-shrink:0;">
                                        <i class="ph ph-floppy-disk"></i> Lưu giá
                                    </button>
                                </div>
                            </div>

                            <!-- Kết quả quy đổi -->
                            <div id="selected-silver-total-display" style="margin-top: 15px; padding: 15px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; display: none;">
                                <div style="margin-bottom: 5px; color: var(--text-main); font-size: 14px;">Chi tiết: <strong id="selected-silver-sum">0 Chỉ</strong></div>
                                <div style="margin-bottom: 5px; color: var(--text-main); font-size: 14px;">Quy đổi: <strong id="selected-silver-converted">0 Chỉ</strong></div>
                                <div style="margin-bottom: 8px; color: var(--text-main); font-size: 14px;">Giá 1 <span id="silver-summary-unit-name">Chỉ</span>: <strong id="selected-silver-price">0 ₫</strong></div>
                                <div style="color: var(--primary); font-size: 16px; font-weight: 700;">= <span id="selected-silver-total-money">0 ₫</span></div>
                            </div>'''

html = re.sub(r'<!-- Gi. b.c th. c.ng theo t.ng don v. -->.*?<div id="silver-calc-breakdown".*?</div>', new_html, html, flags=re.DOTALL)
html = re.sub(r'<!-- Giá bạc thủ công theo từng đơn vị -->.*?<div id="silver-calc-breakdown".*?</div>', new_html, html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Success script 7 index.html')
