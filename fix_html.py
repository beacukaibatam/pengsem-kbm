with open('Formulir_Pemohon_CEISA_PENGSEM_KBM.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix broken newlines
text = text.replace("const lines = rawText.split('\n');", "const lines = rawText.split(/\\r?\\n/).map(l => l.trim().toUpperCase()).filter(Boolean);")
text = text.replace("const lines = rawText.split('\n", "const lines = rawText.split(/\\r?\\n/).map(l => l.trim().toUpperCase()).filter(Boolean);\n// ")
text = text.replace("');", "');")

# Also replace rawText.split('\n')
import re
text = re.sub(r"rawText\.split\(\s*'\s*\n\s*'\s*\)", r"rawText.split(/\\r?\\n/)", text)

with open('Formulir_Pemohon_CEISA_PENGSEM_KBM.html', 'w', encoding='utf-8') as f:
    f.write(text)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Formulir and index.html fixed!")
