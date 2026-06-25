import sys

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if '<!-- Card 2: Quản lý Vàng -->' in line:
        start_idx = i
        break

if start_idx != -1:
    for i in range(start_idx, len(lines)):
        if '<!-- Settings Tab -->' in lines[i]:
            end_idx = i - 2
            break

if start_idx == -1 or end_idx == -1:
    print('Could not find boundaries')
    sys.exit(1)

replacement = """                </div> <!-- Closes dashboard-grid containing Card 1 and Card 3 -->

                <!-- Asset Type Navigation -->
                <div class="asset-tabs-nav" style="display:flex; gap:12px; margin-bottom: 24px; margin-top: 8px;">
                    <button class="btn btn-primary" id="btn-tab-gold" onclick="switchAssetTab('gold')" style="flex:1; padding: 12px; font-size: 15px; border-radius: 12px; transition: all 0.2s;"><i class="ph ph-coins"></i> Kho Vàng</button>
                    <button class="btn" id="btn-tab-silver" onclick="switchAssetTab('silver')" style="flex:1; padding: 12px; font-size: 15px; border-radius: 12px; background: rgba(255,255,255,0.4); color: var(--text-main); border: 1px solid var(--card-border); transition: all 0.2s;"><i class="ph ph-sketch-logo"></i> Kho Bạc</button>
                </div>

                <!-- GOLD VIEW -->
                <div id="assets-gold-view">
                    <div class="dashboard-grid h-full" style="margin-bottom: 24px;">
                        <!-- Card 2: Quản lý Vàng -->
                        <div class="card glass-panel col-span-1">
                            <div class="card-header">
                                <h3>Quản lý Vàng</h3>
                            </div>

                            <!-- Số lượng vàng -->
                            <div class="form-group">
                                <label><i class="ph ph-coins"></i> Số lượng vàng đang giữ</label>
                                <div style="display:flex; gap:8px; align-items:center;">
                                    <input type="number" id="gold-amount" class="glass-input" placeholder="0" step="0.01" min="0" style="flex:1;">
                                    <select id="gold-unit" class="glass-input" style="width:145px;">
                                        <option value="chi">Chỉ</option>
                                        <option value="cay">Cây (Lượng)</option>
                                        <option value="phan">Phân</option>
                                    </select>
                                    <button id="btn-save-gold-amount" class="btn btn-primary" style="padding:0 14px; height:42px; font-size:12px; white-space:nowrap; flex-shrink:0;">
                                        <i class="ph ph-floppy-disk"></i> Lưu
                                    </button>
                                </div>
                            </div>

                            <!-- Giá vàng -->
                            <div class="form-group" style="margin-top:20px;">
                                <label style="color:var(--primary); font-weight:600;"><i class="ph ph-tag"></i> Giá vàng (VND / Chỉ)</label>
                                <div style="display:flex; gap:8px; align-items:center;">
                                    <input type="text" id="manual-gold-price-input" class="glass-input" placeholder="" style="flex:1;">
                                    <button id="btn-save-gold-price" class="btn btn-primary" style="padding:0 14px; height:42px; font-size:12px; white-space:nowrap; flex-shrink:0;">
                                        <i class="ph ph-floppy-disk"></i> Lưu giá
                                    </button>
                                </div>
                            </div>

                            <!-- Kết quả quy đổi -->
                            <div id="gold-calc-breakdown" style="margin-top:16px; padding:14px; background:var(--primary-light); border-radius:12px; border:1px solid var(--primary); font-size:13px; line-height:1.8; display:none;"></div>
                        </div>
                    </div>

                    <!-- Section: Chi tiết mua vàng -->
                    <div id="gold-purchase-section" style="width: 100%;">
                        <div class="card glass-panel" id="gold-purchase-card" style="width: 100%;">
                            <div class="card-header" style="display:flex; justify-content:space-between; align-items:center; flex-wrap: wrap; gap: 15px;">
                                <h3 style="margin:0;"><i class="ph ph-scroll"></i> Chi tiết danh mục vàng đã mua</h3>
                                
                                <div class="gold-filter-group" style="display:flex; background:rgba(0,0,0,0.05); padding:4px; border-radius:10px; gap:4px;">
                                    <button class="filter-btn active" data-filter="all" style="border:none; padding:6px 12px; border-radius:8px; font-size:12px; cursor:pointer; font-weight:600; transition:all 0.2s;">Tất cả</button>
                                    <button class="filter-btn" data-filter="tài sản" style="border:none; padding:6px 12px; border-radius:8px; font-size:12px; cursor:pointer; font-weight:600; transition:all 0.2s;">Tài sản</button>
                                    <button class="filter-btn" data-filter="kỷ niệm" style="border:none; padding:6px 12px; border-radius:8px; font-size:12px; cursor:pointer; font-weight:600; transition:all 0.2s;">Kỷ niệm</button>
                                </div>

                                <div style="display:flex; gap:20px; align-items:center;">
                                    <div style="font-size:13px; color:var(--text-muted);">
                                        Vốn: <strong id="total-gold-cost" style="color:var(--text-main);">0 ₫</strong>
                                    </div>
                                    <div style="font-size:13px; color:var(--text-muted);">
                                        Chênh lệch: <strong id="gold-profit-loss" style="font-size:16px;">0 ₫</strong>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Form nhập mua vàng -->
                            <div id="gold-purchase-form-container" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:12px; margin-bottom:20px; padding:20px; background:rgba(0,0,0,0.02); border-radius:15px; border:1px solid var(--card-border);">
                                <input type="hidden" id="gold-purchase-edit-id">
                                
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-calendar"></i> Ngày mua</label>
                                    <div style="display:flex; gap:4px; position:relative;">
                                        <input type="text" id="gold-purchase-date-display" class="glass-input" placeholder="Ngày/Tháng/Năm" maxlength="10" style="flex:1;">
                                        <input type="date" id="gold-purchase-date" style="position:absolute; opacity:0; width:0; height:0; pointer-events:none;">
                                        <button type="button" id="btn-open-gold-calendar" class="btn btn-secondary" style="padding:0 8px; height:42px; min-width:40px;">
                                            <i class="ph ph-calendar-blank" style="font-size:18px;"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-coins"></i> Số lượng</label>
                                    <div style="display:flex; gap:4px;">
                                        <input type="number" id="gold-purchase-amount" class="glass-input" placeholder="0" step="0.01" style="flex:1;">
                                        <select id="gold-purchase-unit" class="glass-input" style="width:70px; padding:4px;">
                                            <option value="chi">Chỉ</option>
                                            <option value="cay">Cây</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-tag"></i> Đơn giá mua</label>
                                    <input type="text" id="gold-purchase-unit-price" class="glass-input" placeholder="Giá/Chỉ/Cây...">
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-fingerprint"></i> Loại vàng</label>
                                    <input type="text" id="gold-purchase-type" class="glass-input" placeholder="Loại...">
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-folders"></i> Phân loại</label>
                                    <select id="gold-purchase-category" class="glass-input">
                                        <option value="tài sản">Tài sản</option>
                                        <option value="kỷ niệm">Kỷ niệm</option>
                                    </select>
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-money"></i> Tiền vốn (VND)</label>
                                    <input type="text" id="gold-purchase-cost" class="glass-input" placeholder="Giá mua...">
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-storefront"></i> Tiệm vàng</label>
                                    <input type="text" id="gold-purchase-shop" class="glass-input" placeholder="Tên tiệm...">
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-map-pin"></i> Địa chỉ tiệm</label>
                                    <input type="text" id="gold-purchase-address" class="glass-input" placeholder="Địa chỉ...">
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-note"></i> Ghi chú</label>
                                    <input type="text" id="gold-purchase-note" class="glass-input" placeholder="Ghi chú thêm...">
                                </div>
                                <div style="display:flex; align-items:flex-end;">
                                    <button id="btn-add-gold-purchase" class="btn btn-primary w-full" style="height:42px; font-weight:600; white-space:nowrap; justify-content:center;">
                                        <i class="ph ph-plus-circle"></i> <span id="gold-purchase-btn-text">Thêm/Lưu</span>
                                    </button>
                                </div>
                            </div>

                            <div style="display:flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <h3 style="font-size: 16px; font-weight: 600; margin: 0;"><i class="ph ph-list-bullets"></i> Danh sách chi tiết</h3>
                                <div id="selected-gold-total-display" style="font-weight: 600; color: var(--primary); font-size: 14px; background: var(--primary-light); padding: 4px 12px; border-radius: 20px; display: none;">
                                    Đang chọn: <span id="selected-gold-sum">0</span> Chi
                                </div>
                            </div>

                            <div class="table-responsive" style="margin-top: 10px; overflow-x: auto;">
                                <table class="transaction-table" style="width: 100%; min-width: 1100px; border-collapse: collapse;">
                                    <thead>
                                        <tr>
                                            <th style="width: 40px; padding: 12px; text-align: center;">
                                                <input type="checkbox" id="gold-select-all" style="width:18px; height:18px; cursor:pointer;">
                                            </th>
                                            <th style="text-align: left; padding: 12px; width: 100px;">Ngày mua</th>
                                            <th style="text-align: left; padding: 12px; width: 120px;">Số lượng</th>
                                            <th style="text-align: right; padding: 12px; width: 130px;">Đơn giá</th>
                                            <th style="text-align: left; padding: 12px; width: 100px;">Loại vàng</th>
                                            <th style="text-align: left; padding: 12px; width: 100px;">Phân loại</th>
                                            <th style="text-align: right; padding: 12px; width: 130px;">Tiền vốn</th>
                                            <th style="text-align: left; padding: 12px; width: 150px;">Tiệm vàng</th>
                                            <th style="text-align: left; padding: 12px; width: 150px;">Địa chỉ</th>
                                            <th style="text-align: left; padding: 12px;">Ghi chú</th>
                                            <th style="text-align: center; padding: 12px; width: 100px;">Thao tác</th>
                                        </tr>
                                    </thead>
                                    <tbody id="gold-purchase-list">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- SILVER VIEW -->
                <div id="assets-silver-view" style="display: none;">
                    <div class="dashboard-grid h-full" style="margin-bottom: 24px;">
                        <!-- Card: Quản lý Bạc -->
                        <div class="card glass-panel col-span-1">
                            <div class="card-header">
                                <h3>Quản lý Bạc</h3>
                            </div>

                            <!-- Số lượng bạc -->
                            <div class="form-group">
                                <label><i class="ph ph-sketch-logo"></i> Số lượng bạc đang giữ</label>
                                <div style="display:flex; gap:8px; align-items:center;">
                                    <input type="number" id="silver-amount" class="glass-input" placeholder="0" step="0.01" min="0" style="flex:1;">
                                    <select id="silver-unit" class="glass-input" style="width:145px;">
                                        <option value="chi">Chỉ</option>
                                        <option value="cay">Lượng (Cây)</option>
                                        <option value="kg">Kilogram</option>
                                    </select>
                                    <button id="btn-save-silver-amount" class="btn btn-primary" style="padding:0 14px; height:42px; font-size:12px; white-space:nowrap; flex-shrink:0;">
                                        <i class="ph ph-floppy-disk"></i> Lưu
                                    </button>
                                </div>
                            </div>

                            <!-- Giá bạc thủ công theo từng đơn vị -->
                            <div class="form-group" style="margin-top:20px;">
                                <label style="color:var(--primary); font-weight:600;"><i class="ph ph-tag"></i> Giá bạc thị trường (VND)</label>
                                
                                <div style="display:flex; flex-direction:column; gap:8px; margin-top:8px;">
                                    <div style="display:flex; gap:8px; align-items:center;">
                                        <span style="width: 60px; font-size: 13px; font-weight: 500;">/ Kg:</span>
                                        <input type="text" id="manual-silver-price-kg" class="glass-input" placeholder="Giá 1 Kg bạc..." style="flex:1;">
                                    </div>
                                    <div style="display:flex; gap:8px; align-items:center;">
                                        <span style="width: 60px; font-size: 13px; font-weight: 500;">/ Lượng:</span>
                                        <input type="text" id="manual-silver-price-cay" class="glass-input" placeholder="Giá 1 lượng bạc..." style="flex:1;">
                                    </div>
                                    <div style="display:flex; gap:8px; align-items:center;">
                                        <span style="width: 60px; font-size: 13px; font-weight: 500;">/ Chỉ:</span>
                                        <input type="text" id="manual-silver-price-chi" class="glass-input" placeholder="Giá 1 chỉ bạc..." style="flex:1;">
                                    </div>
                                </div>

                                <button id="btn-save-silver-price" class="btn btn-primary w-full" style="margin-top:12px; height:42px; font-size:13px; font-weight:600; justify-content:center;">
                                    <i class="ph ph-floppy-disk"></i> Lưu bộ giá bạc
                                </button>
                            </div>

                            <!-- Kết quả quy đổi -->
                            <div id="silver-calc-breakdown" style="margin-top:16px; padding:14px; background:var(--primary-light); border-radius:12px; border:1px solid var(--primary); font-size:13px; line-height:1.8; display:none;"></div>
                        </div>
                    </div>

                    <!-- Section: Chi tiết mua bạc -->
                    <div id="silver-purchase-section" style="width: 100%;">
                        <div class="card glass-panel" id="silver-purchase-card" style="width: 100%;">
                            <div class="card-header" style="display:flex; justify-content:space-between; align-items:center; flex-wrap: wrap; gap: 15px;">
                                <h3 style="margin:0;"><i class="ph ph-scroll"></i> Chi tiết danh mục bạc đã mua</h3>
                                
                                <div class="silver-filter-group" style="display:flex; background:rgba(0,0,0,0.05); padding:4px; border-radius:10px; gap:4px;">
                                    <button class="filter-btn active" data-filter="all" style="border:none; padding:6px 12px; border-radius:8px; font-size:12px; cursor:pointer; font-weight:600; transition:all 0.2s;">Tất cả</button>
                                    <button class="filter-btn" data-filter="bạc tích trữ" style="border:none; padding:6px 12px; border-radius:8px; font-size:12px; cursor:pointer; font-weight:600; transition:all 0.2s;">Tích trữ</button>
                                    <button class="filter-btn" data-filter="bạc mỹ nghệ" style="border:none; padding:6px 12px; border-radius:8px; font-size:12px; cursor:pointer; font-weight:600; transition:all 0.2s;">Mỹ nghệ</button>
                                    <button class="filter-btn" data-filter="bạc mỹ nghệ limited" style="border:none; padding:6px 12px; border-radius:8px; font-size:12px; cursor:pointer; font-weight:600; transition:all 0.2s;">Limited</button>
                                </div>

                                <div style="display:flex; gap:20px; align-items:center;">
                                    <div style="font-size:13px; color:var(--text-muted);">
                                        Vốn: <strong id="total-silver-cost" style="color:var(--text-main);">0 ₫</strong>
                                    </div>
                                    <div style="font-size:13px; color:var(--text-muted);">
                                        Chênh lệch: <strong id="silver-profit-loss" style="font-size:16px;">0 ₫</strong>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Form nhập mua bạc -->
                            <div id="silver-purchase-form-container" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:12px; margin-bottom:20px; padding:20px; background:rgba(0,0,0,0.02); border-radius:15px; border:1px solid var(--card-border);">
                                <input type="hidden" id="silver-purchase-edit-id">
                                
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-calendar"></i> Ngày mua</label>
                                    <div style="display:flex; gap:4px; position:relative;">
                                        <input type="text" id="silver-purchase-date-display" class="glass-input" placeholder="Ngày/Tháng/Năm" maxlength="10" style="flex:1;">
                                        <input type="date" id="silver-purchase-date" style="position:absolute; opacity:0; width:0; height:0; pointer-events:none;">
                                        <button type="button" id="btn-open-silver-calendar" class="btn btn-secondary" style="padding:0 8px; height:42px; min-width:40px;">
                                            <i class="ph ph-calendar-blank" style="font-size:18px;"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-sketch-logo"></i> Số lượng</label>
                                    <div style="display:flex; gap:4px;">
                                        <input type="number" id="silver-purchase-amount" class="glass-input" placeholder="0" step="0.01" style="flex:1;">
                                        <select id="silver-purchase-unit" class="glass-input" style="width:70px; padding:4px;">
                                            <option value="chi">Chỉ</option>
                                            <option value="cay">Lượng</option>
                                            <option value="kg">Kg</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-tag"></i> Đơn giá mua</label>
                                    <input type="text" id="silver-purchase-unit-price" class="glass-input" placeholder="Giá mua...">
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-fingerprint"></i> Loại bạc</label>
                                    <input type="text" id="silver-purchase-type" class="glass-input" placeholder="Loại (Bạc 925...)...">
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-folders"></i> Phân loại</label>
                                    <select id="silver-purchase-category" class="glass-input">
                                        <option value="bạc tích trữ">Bạc tích trữ</option>
                                        <option value="bạc mỹ nghệ">Bạc mỹ nghệ</option>
                                        <option value="bạc mỹ nghệ limited">Bạc mỹ nghệ limited</option>
                                    </select>
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-money"></i> Tiền vốn (VND)</label>
                                    <input type="text" id="silver-purchase-cost" class="glass-input" placeholder="Tiền vốn...">
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-storefront"></i> Nơi mua</label>
                                    <input type="text" id="silver-purchase-shop" class="glass-input" placeholder="Tên tiệm...">
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-map-pin"></i> Địa chỉ</label>
                                    <input type="text" id="silver-purchase-address" class="glass-input" placeholder="Địa chỉ...">
                                </div>
                                <div class="form-group" style="margin-bottom:0;">
                                    <label style="font-size:12px; font-weight:600;"><i class="ph ph-note"></i> Ghi chú</label>
                                    <input type="text" id="silver-purchase-note" class="glass-input" placeholder="Ghi chú thêm...">
                                </div>
                                <div style="display:flex; align-items:flex-end;">
                                    <button id="btn-add-silver-purchase" class="btn btn-primary w-full" style="height:42px; font-weight:600; white-space:nowrap; justify-content:center;">
                                        <i class="ph ph-plus-circle"></i> <span id="silver-purchase-btn-text">Thêm/Lưu</span>
                                    </button>
                                </div>
                            </div>

                            <div style="display:flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <h3 style="font-size: 16px; font-weight: 600; margin: 0;"><i class="ph ph-list-bullets"></i> Danh sách chi tiết Bạc</h3>
                                <div id="selected-silver-total-display" style="font-weight: 600; color: var(--primary); font-size: 14px; background: var(--primary-light); padding: 4px 12px; border-radius: 20px; display: none;">
                                    Đang chọn: <span id="selected-silver-sum">0</span>
                                </div>
                            </div>
                            
                            <div class="table-responsive" style="margin-top: 10px; overflow-x: auto;">
                                <table class="transaction-table" style="width: 100%; min-width: 1100px; border-collapse: collapse;">
                                    <thead>
                                        <tr>
                                            <th style="width: 40px; padding: 12px; text-align: center;">
                                                <input type="checkbox" id="silver-select-all" style="width:18px; height:18px; cursor:pointer;">
                                            </th>
                                            <th style="text-align: left; padding: 12px; width: 100px;">Ngày mua</th>
                                            <th style="text-align: left; padding: 12px; width: 120px;">Số lượng</th>
                                            <th style="text-align: right; padding: 12px; width: 130px;">Đơn giá</th>
                                            <th style="text-align: left; padding: 12px; width: 100px;">Loại bạc</th>
                                            <th style="text-align: left; padding: 12px; width: 100px;">Phân loại</th>
                                            <th style="text-align: right; padding: 12px; width: 130px;">Tiền vốn</th>
                                            <th style="text-align: left; padding: 12px; width: 150px;">Nơi mua</th>
                                            <th style="text-align: left; padding: 12px; width: 150px;">Địa chỉ</th>
                                            <th style="text-align: left; padding: 12px;">Ghi chú</th>
                                            <th style="text-align: center; padding: 12px; width: 100px;">Thao tác</th>
                                        </tr>
                                    </thead>
                                    <tbody id="silver-purchase-list">
                                        <!-- Rendered by JS -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
\n"""

new_lines = lines[:start_idx] + [replacement] + lines[end_idx:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Success')
