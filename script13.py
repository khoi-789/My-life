import re
import time

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Bust cache by updating query string
timestamp = int(time.time())
html = re.sub(r'app\.js\?v=\d+', f'app.js?v={timestamp}', html)

# Fix the formatCurrency issue for editing (Wait, formatNumber IS NOT DEFINED!)
# I need to add formatNumber to app.js, or replace it in editSilverPurchase!
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace('formatNumber(p.unitPrice)', "new Intl.NumberFormat('vi-VN').format(p.unitPrice)")
js = js.replace('formatNumber(p.cost)', "new Intl.NumberFormat('vi-VN').format(p.cost)")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('Success script 13 cache bust')
