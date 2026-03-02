import re

with open('styles/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Fix Header
header_css = '''
header {
    background-color: white;
    padding: 1rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    position: sticky;
    top: 0;
    z-index: 100;
}
header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, 
        var(--brand-navy) 0%, var(--brand-navy) 20%,
        var(--brand-orange) 20%, var(--brand-orange) 40%,
        var(--brand-pink) 40%, var(--brand-pink) 60%,
        var(--brand-green) 60%, var(--brand-green) 80%,
        var(--brand-yellow) 80%, var(--brand-yellow) 100%
    );
}
'''
css = re.sub(r'header\s*\{.*?\}\s*header::before\s*\{.*?\}', header_css.strip(), css, flags=re.DOTALL)

# Fix Hero
hero_css = '''
.hero {
    text-align: center;
    padding: 3.5rem 1rem;
    position: relative;
    background: transparent;
    margin-bottom: 1rem;
}

.hero h1 {
    font-size: 2.8rem;
    font-weight: 800;
    color: var(--brand-navy);
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}

.hero .subtitle {
    font-size: 1.25rem;
    color: var(--brand-orange);
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.hero .subtitle:nth-of-type(2) {
    color: #4a5568;
    font-weight: 500;
    margin-bottom: 1.5rem;
}

.hero .date-info {
    color: var(--brand-navy);
    font-weight: 600;
    font-size: 0.95rem;
    padding: 0.6rem 1.2rem;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    margin-top: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.hero .date-info i {
    margin-right: 0.5rem;
    color: var(--brand-orange);
}
'''
css = re.sub(r'\.hero\s*\{.*?(?=\.dashboard-grid \{)', hero_css.strip() + '\n\n', css, flags=re.DOTALL)


# Fix Dashboard Cards
card_css = '''
.dashboard-grid {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem 2rem 3rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.card {
    background: white;
    padding: 2rem 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
    border: 1px solid #f0f4f8;
    position: relative;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(43, 57, 144, 0.08);
    border-color: #e2e8f0;
}

.card i {
    font-size: 2rem;
    margin-bottom: 1rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    border-radius: 12px;
    transition: all 0.2s ease;
}

.card:nth-child(5n+1) i { color: var(--brand-navy); background: #f0f4ff; }
.card:nth-child(5n+2) i { color: var(--brand-orange); background: #fff4e5; }
.card:nth-child(5n+3) i { color: var(--brand-pink); background: #fde8ec; }
.card:nth-child(5n+4) i { color: var(--brand-green); background: #f4f9ed; }
.card:nth-child(5n+5) i { color: var(--brand-yellow); background: #fffbe5; }

.card:hover i {
    transform: scale(1.05);
}

.card h2 {
    color: var(--brand-navy);
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
}

.card p {
    color: #64748b;
    font-size: 0.95rem;
    line-height: 1.5;
}
'''
css = re.sub(r'\.dashboard-grid \{.*?(?=\.card h2 \{)', card_css.strip() + '\n\n', css, flags=re.DOTALL)
css = re.sub(r'\.card h2\s*\{.*?\}\s*\.card p\s*\{.*?\}', '', css, flags=re.DOTALL)

with open('styles/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)

print('Restored a clean and professional UI layout')
