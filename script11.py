import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Remove the broken exports at the bottom
js = js.replace('window.editSilverPurchase = editSilverPurchase;', '')
js = js.replace('window.deleteSilverPurchase = deleteSilverPurchase;', '')

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('Success script 11 app.js')
