import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace window.renderSilverPurchases completely
old_render = '''window.renderSilverPurchases = () => {'''
new_render = '''window.renderSilverPurchases = () => {
    try {'''

old_end = '''    calculateInitialSilverTickSum();
};'''
new_end = '''    calculateInitialSilverTickSum();
    } catch (e) {
        console.error("Crash inside renderSilverPurchases:", e);
    }
};'''

content = content.replace(old_render, new_render)
content = content.replace(old_end, new_end)

# Inside the forEach, wrap with try/catch
old_foreach = '''    sorted.forEach(p => {
        const row = document.createElement('tr');'''

new_foreach = '''    sorted.forEach(p => {
        try {
            if (!p || typeof p !== 'object') return;
        const row = document.createElement('tr');'''

old_foreach_end = '''        els.silverPurchaseList.appendChild(row);
    });'''

new_foreach_end = '''        els.silverPurchaseList.appendChild(row);
        } catch (e) {
            console.error("Crash inside sorted.forEach:", p, e);
        }
    });'''

content = content.replace(old_foreach, new_foreach)
content = content.replace(old_foreach_end, new_foreach_end)

# Also fix the global filter listener bug that removes active class from Silver when Gold is clicked, or vice versa!
# Currently in app.js around line 949:
# document.querySelectorAll('.filter-btn').forEach(btn => { ...
# This interferes with silver buttons!
# Let's fix it by making the Gold listener only apply to '.gold-filter-group .filter-btn'
old_gold_listener = '''    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // 1. Cập nhật UI nút active
            document.querySelectorAll('.filter-btn').forEach(b => {'''

new_gold_listener = '''    document.querySelectorAll('.gold-filter-group .filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // 1. Cập nhật UI nút active
            document.querySelectorAll('.gold-filter-group .filter-btn').forEach(b => {'''

content = content.replace(old_gold_listener, new_gold_listener)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Success script 5')
