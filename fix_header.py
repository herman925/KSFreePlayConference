import re

with open('styles/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Fix the general page header to look clean again
page_header_css = '''
.page-header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2.5rem 0;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    position: relative;
    overflow: hidden;
}

.page-header h1 {
    font-size: 2.4rem;
    color: var(--brand-navy);
    margin-bottom: 0.5rem;
    font-weight: 700;
}

.page-header .subtitle {
    color: #4a5568;
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
}

.page-header .date-info {
    color: #4a5568;
    font-size: 1rem;
    padding: 0.5rem 1.2rem;
    background: #f8fafc;
    border-radius: 20px;
    display: inline-block;
    margin-top: 0.5rem;
    border: 1px solid #e2e8f0;
}
'''

css = re.sub(r'\.page-header\s*\{.*?(?=\.nav-wrapper \{)', page_header_css.strip() + '\n\n', css, flags=re.DOTALL)

with open('styles/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)

print('Cleaned up internal page headers')
