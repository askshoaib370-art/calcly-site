#!/usr/bin/env python3
"""
Static site generator for the calculator hub.
Reads CALCULATORS (below) and writes full static HTML pages:
  /calculators/<category>/<slug>/index.html
plus category index pages and the homepage.

Run: python3 build.py
"""
import os, json, html

SITE_NAME = "Calcly"
SITE_TAGLINE = "Free calculators for everyday life, finance, health, and home projects."
BASE_URL = "https://calcly.tools"  # change to your real domain later

OUT = os.path.dirname(os.path.abspath(__file__))

CATEGORIES = {
    "finance": {"name": "Finance", "desc": "Loans, mortgages, savings, and paychecks."},
    "health": {"name": "Health & Fitness", "desc": "BMI, calories, macros, and more."},
    "construction": {"name": "Construction & Home", "desc": "Material estimators for home projects."},
    "everyday-math": {"name": "Everyday Math", "desc": "Percentages, dates, grades, tips."},
    "business": {"name": "Business", "desc": "Margins, break-even, and selling fees."},
    "automotive": {"name": "Automotive", "desc": "Fuel cost and driving calculators."},
    "education": {"name": "Education", "desc": "Grades and GPA tools for students."},
}

HEADER_LINKS = "".join(
    f'<a href="/calculators/{slug}/">{c["name"]}</a>' for slug, c in CATEGORIES.items()
)

def page_shell(title, meta_desc, body, canonical, jsonld="", extra_js=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(meta_desc)}">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="/assets/css/style.css">
{jsonld}
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="logo" href="/"><span>{SITE_NAME}</span></a>
    <nav class="main">{HEADER_LINKS}</nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site">
  <div class="wrap">
    <div>
      <div class="logo"><span>{SITE_NAME}</span></div>
      <p style="color:var(--muted);font-size:14px;max-width:320px">{SITE_TAGLINE}</p>
    </div>
    <div><h4>Categories</h4><ul>{"".join(f'<li><a href="/calculators/{s}/">{c["name"]}</a></li>' for s,c in CATEGORIES.items())}</ul></div>
    <div><h4>Company</h4><ul><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li></ul></div>
    <div><h4>Legal</h4><ul><li><a href="/privacy/">Privacy Policy</a></li><li><a href="/terms/">Terms</a></li></ul></div>
  </div>
  <div class="footer-bottom">&copy; 2026 {SITE_NAME}. All calculators are provided for informational purposes only.</div>
</footer>
{extra_js}
</body>
</html>"""

def faq_jsonld(faqs):
    items = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}
    return f'<script type="application/ld+json">{json.dumps(data)}</script>'

def related_links(cat, slug):
    others = [c for c in CALCULATORS if c["category"] == cat and c["slug"] != slug][:4]
    if not others:
        others = [c for c in CALCULATORS if c["slug"] != slug][:4]
    return "".join(f'<a href="/calculators/{o["category"]}/{o["slug"]}/">{o["name"]}</a>' for o in others)

def calc_page(c):
    cat = CATEGORIES[c["category"]]
    canonical = f"{BASE_URL}/calculators/{c['category']}/{c['slug']}/"
    crumb = f'<div class="crumb"><a href="/">Home</a> &rsaquo; <a href="/calculators/{c["category"]}/">{cat["name"]}</a> &rsaquo; {c["name"]}</div>'
    faq_html = "".join(
        f'<div class="faq-item"><div class="q">{html.escape(q)}</div><div class="a">{html.escape(a)}</div></div>'
        for q, a in c["faq"]
    )
    related = related_links(c["category"], c["slug"])
    body = f"""
{crumb}
<div class="page-head">
  <h1>{html.escape(c['name'])}</h1>
  <p class="lede">{html.escape(c['intro'])}</p>
</div>

<div class="ad-slot">Ad placeholder &mdash; above the fold</div>

<div class="card">
  {c['form_html']}
  <div id="result" class="result">
    {c['result_html']}
  </div>
</div>

<div class="card">
  <h2 class="section-title">How the {html.escape(c['name'])} works</h2>
  <p>{c['how_it_works']}</p>
</div>

<div class="ad-slot">Ad placeholder &mdash; below the fold</div>

<div class="card">
  <h2 class="section-title">Frequently asked questions</h2>
  {faq_html}
</div>

<div class="card">
  <h2 class="section-title">Related calculators</h2>
  <div class="related-links">{related}</div>
</div>
"""
    jsonld = faq_jsonld(c["faq"])
    extra_js = f"<script>\n{c['script']}\n</script>"
    html_out = page_shell(
        f"{c['name']} - Free Online {cat['name']} Tool | {SITE_NAME}",
        c["intro"],
        body,
        canonical,
        jsonld,
        extra_js,
    )
    path = os.path.join(OUT, "calculators", c["category"], c["slug"])
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "index.html"), "w") as f:
        f.write(html_out)

def category_page(slug, cat):
    items = [c for c in CALCULATORS if c["category"] == slug]
    cards = "".join(
        f'<div class="cat-card"><h3><a href="/calculators/{slug}/{c["slug"]}/">{c["name"]}</a></h3><p>{html.escape(c["intro"][:90])}&hellip;</p></div>'
        for c in items
    )
    body = f"""
<div class="crumb"><a href="/">Home</a> &rsaquo; {cat['name']}</div>
<div class="page-head">
  <h1>{cat['name']} Calculators</h1>
  <p class="lede">{cat['desc']}</p>
</div>
<div class="cat-grid">{cards}</div>
"""
    out = page_shell(f"{cat['name']} Calculators | {SITE_NAME}", cat["desc"], body, f"{BASE_URL}/calculators/{slug}/")
    path = os.path.join(OUT, "calculators", slug)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "index.html"), "w") as f:
        f.write(out)

def homepage():
    cat_cards = "".join(
        f'''<div class="cat-card"><h3><a href="/calculators/{slug}/">{c["name"]}</a></h3><p>{c["desc"]}</p>
        <ul>{"".join(f'<li><a href="/calculators/{slug}/{x["slug"]}/">{x["name"]}</a></li>' for x in CALCULATORS if x["category"]==slug)}</ul></div>'''
        for slug, c in CATEGORIES.items()
    )
    body = f"""
<div class="page-head" style="padding-top:40px">
  <h1 style="font-size:36px">Free calculators for every part of life</h1>
  <p class="lede">{SITE_NAME} has fast, accurate calculators for finance, health, home projects, school, business, and more &mdash; no sign-up, no clutter.</p>
</div>
<div class="ad-slot">Ad placeholder &mdash; homepage banner</div>
<div class="cat-grid">{cat_cards}</div>
"""
    out = page_shell(f"{SITE_NAME} - Free Online Calculators", SITE_TAGLINE, body, f"{BASE_URL}/")
    with open(os.path.join(OUT, "index.html"), "w") as f:
        f.write(out)

def sitemap_and_robots():
    urls = [f"{BASE_URL}/"] + [f"{BASE_URL}/calculators/{s}/" for s in CATEGORIES] + \
           [f"{BASE_URL}/calculators/{c['category']}/{c['slug']}/" for c in CALCULATORS]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        xml.append(f"<url><loc>{u}</loc></url>")
    xml.append("</urlset>")
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write("\n".join(xml))
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")

# ---------------------------------------------------------------------------
# small helpers for building form markup
# ---------------------------------------------------------------------------
def field(fid, label, hint="", type="number", step="any", value="", extra=""):
    hint_html = f'<span class="hint">{hint}</span>' if hint else ""
    return f'''<div class="field"><label for="{fid}">{label}</label>
    <input type="{type}" id="{fid}" step="{step}" value="{value}" {extra}>{hint_html}</div>'''

def select(fid, label, options, hint=""):
    opts = "".join(f'<option value="{v}">{t}</option>' for v, t in options)
    hint_html = f'<span class="hint">{hint}</span>' if hint else ""
    return f'''<div class="field"><label for="{fid}">{label}</label>
    <select id="{fid}">{opts}</select>{hint_html}</div>'''

def btn(label="Calculate"):
    return f'<button class="btn" onclick="calc()">{label}</button>'

def big(label, rid="res-main"):
    return f'<div class="big"><span id="{rid}">&mdash;</span></div><div class="hint" style="margin-top:4px">{label}</div>'

def row(rid, label):
    return f'<div class="row"><span class="label">{label}</span><span id="{rid}"><strong>&mdash;</strong></span></div>'

# ---------------------------------------------------------------------------
# CALCULATOR DATA — formulas, content, and real working JS for each.
# ---------------------------------------------------------------------------
CALCULATORS = [

# ---------------- FINANCE ----------------
{
  "slug":"mortgage-calculator","category":"finance","name":"Mortgage Calculator",
  "intro":"Estimate your monthly mortgage payment, total interest, and total cost based on home price, down payment, interest rate, and loan term.",
  "form_html": f'''<div class="calc-grid">
    {field("price","Home price ($)",value="350000")}
    {field("down","Down payment ($)",value="70000")}
    {field("rate","Interest rate (% / year)",value="6.5")}
    {field("years","Loan term (years)",value="30",type="number",step="1")}
  </div>{btn()}''',
  "result_html": f'''{big("Estimated monthly payment")}
    {row("res-total","Total of all payments")}
    {row("res-interest","Total interest paid")}
    {row("res-principal","Loan amount (principal)")}''',
  "script": """function calc(){
    const price=+document.getElementById('price').value||0;
    const down=+document.getElementById('down').value||0;
    const rate=+document.getElementById('rate').value||0;
    const years=+document.getElementById('years').value||0;
    const principal=Math.max(price-down,0);
    const n=years*12, r=rate/100/12;
    const m = r===0 ? principal/n : principal*r*Math.pow(1+r,n)/(Math.pow(1+r,n)-1);
    const total = m*n, interest = total-principal;
    document.getElementById('res-main').textContent = isFinite(m)? '$'+m.toFixed(2)+' / mo' : '—';
    document.getElementById('res-total').innerHTML = '<strong>$'+total.toFixed(2)+'</strong>';
    document.getElementById('res-interest').innerHTML = '<strong>$'+interest.toFixed(2)+'</strong>';
    document.getElementById('res-principal').innerHTML = '<strong>$'+principal.toFixed(2)+'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"This calculator uses the standard amortization formula M&nbsp;=&nbsp;P[r(1+r)<sup>n</sup>]/[(1+r)<sup>n</sup>&minus;1], where P is your loan amount (home price minus down payment), r is your monthly interest rate, and n is the number of monthly payments. Example: a $280,000 loan at 6.5% for 30 years comes to about $1,769/month, with roughly $356,000 paid in interest over the life of the loan.",
  "faq":[
    ("How much house can I afford?","A common guideline is spending no more than 28% of your gross monthly income on housing costs, including principal, interest, taxes, and insurance."),
    ("Does this include property taxes and insurance?","No, this calculator shows principal and interest only. Add your local property tax rate and homeowner's insurance estimate for a full monthly PITI payment."),
    ("What's a good down payment?","20% avoids private mortgage insurance (PMI) on conventional loans, but many loan programs allow much less.")
  ]
},
{
  "slug":"compound-interest-calculator","category":"finance","name":"Compound Interest Calculator",
  "intro":"See how your savings or investment grows over time with compound interest, and how much of the final balance is interest you earned.",
  "form_html": f'''<div class="calc-grid">
    {field("principal","Initial amount ($)",value="5000")}
    {field("rate","Annual interest rate (%)",value="7")}
    {select("n","Compounding frequency",[("1","Annually"),("4","Quarterly"),("12","Monthly"),("365","Daily")])}
    {field("years","Years",value="10",step="1")}
  </div>{btn()}''',
  "result_html": f'''{big("Future value")}
    {row("res-interest","Total interest earned")}
    {row("res-principal","Starting amount")}''',
  "script": """function calc(){
    const p=+document.getElementById('principal').value||0;
    const rate=+document.getElementById('rate').value||0;
    const n=+document.getElementById('n').value||1;
    const t=+document.getElementById('years').value||0;
    const a = p*Math.pow(1+(rate/100)/n, n*t);
    const interest = a-p;
    document.getElementById('res-main').textContent='$'+a.toFixed(2);
    document.getElementById('res-interest').innerHTML='<strong>$'+interest.toFixed(2)+'</strong>';
    document.getElementById('res-principal').innerHTML='<strong>$'+p.toFixed(2)+'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"This uses A = P(1 + r/n)<sup>nt</sup>, where P is your starting amount, r is the annual rate, n is how many times per year interest compounds, and t is the number of years. Example: $5,000 at 7% compounded monthly for 10 years grows to about $10,048, meaning roughly $5,048 was earned purely from interest.",
  "faq":[
    ("What's the difference between simple and compound interest?","Compound interest earns interest on previously earned interest, so growth accelerates over time; simple interest only applies to the original principal."),
    ("How often should interest compound for the best growth?","Daily or monthly compounding grows slightly faster than annual compounding, though the real-world difference is small at typical rates."),
    ("Does this account for additional contributions?","No, this version assumes a single lump sum with no further deposits.")
  ]
},
{
  "slug":"paycheck-calculator","category":"finance","name":"Paycheck Calculator",
  "intro":"Estimate your net take-home pay after federal tax, state tax, and FICA, based on your gross salary and pay frequency.",
  "form_html": f'''<div class="calc-grid">
    {field("gross","Gross annual salary ($)",value="65000")}
    {select("state","State tax rate",[("0","No state income tax"),("3","Low (~3%)"),("5","Medium (~5%)"),("7","High (~7%)"),("9.3","Very high (~9.3%)")])}
    {select("freq","Pay frequency",[("52","Weekly"),("26","Bi-weekly"),("24","Semi-monthly"),("12","Monthly")])}
  </div>{btn()}''',
  "result_html": f'''{big("Take-home pay per paycheck")}
    {row("res-annual","Estimated annual net pay")}
    {row("res-fed","Estimated federal tax")}
    {row("res-fica","FICA (Social Security + Medicare)")}
    {row("res-state","Estimated state tax")}''',
  "script": """function federalTax(gross){
    // simplified 2025-style single-filer brackets, approximate, for estimation only
    const brackets=[[11600,0.10],[47150,0.12],[100525,0.22],[191950,0.24],[243725,0.32],[609350,0.35],[Infinity,0.37]];
    let tax=0, prev=0;
    for(const [cap,rate] of brackets){
      if(gross>prev){ tax += (Math.min(gross,cap)-prev)*rate; prev=cap; } else break;
    }
    return tax;
  }
  function calc(){
    const gross=+document.getElementById('gross').value||0;
    const stateRate=+document.getElementById('state').value||0;
    const freq=+document.getElementById('freq').value||12;
    const fed=federalTax(gross);
    const fica=gross*0.0765;
    const state=gross*(stateRate/100);
    const net=Math.max(gross-fed-fica-state,0);
    document.getElementById('res-main').textContent='$'+(net/freq).toFixed(2);
    document.getElementById('res-annual').innerHTML='<strong>$'+net.toFixed(2)+'</strong>';
    document.getElementById('res-fed').innerHTML='<strong>$'+fed.toFixed(2)+'</strong>';
    document.getElementById('res-fica').innerHTML='<strong>$'+fica.toFixed(2)+'</strong>';
    document.getElementById('res-state').innerHTML='<strong>$'+state.toFixed(2)+'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Your gross pay has federal income tax, FICA (a flat 7.65% for Social Security and Medicare), and state income tax withheld. This calculator applies simplified, approximate 2025-style federal brackets and a state rate you select, then divides the result by your pay frequency. Actual withholding also depends on filing status, dependents, and deductions, so treat this as an estimate.",
  "faq":[
    ("Why is my take-home pay different from my salary?","Federal tax, state tax, and FICA are withheld from every paycheck, so your net pay is always lower than your gross salary."),
    ("What is FICA?","A combined 7.65% tax (6.2% Social Security + 1.45% Medicare) that funds those federal programs."),
    ("Is this exact?","No — it's a simplified estimate. Your actual withholding depends on your W-4 elections, filing status, and local taxes.")
  ]
},
{
  "slug":"debt-payoff-calculator","category":"finance","name":"Debt Payoff Calculator (Snowball Method)",
  "intro":"Find out how many months it will take to become debt-free using the snowball method, which pays off your smallest balance first.",
  "form_html": f'''<div class="calc-grid">
    {field("d1","Debt 1 balance ($)",value="1200")}
    {field("p1","Debt 1 min. payment ($)",value="50")}
    {field("d2","Debt 2 balance ($)",value="4500")}
    {field("p2","Debt 2 min. payment ($)",value="120")}
    {field("d3","Debt 3 balance ($)",value="9000")}
    {field("p3","Debt 3 min. payment ($)",value="200")}
    {field("extra","Extra payment per month ($)",value="100")}
  </div>{btn()}''',
  "result_html": f'''{big("Months to debt-free")}
    {row("res-totalpaid","Total paid (principal, no interest modeled)")}
    {row("res-order","Payoff order")}''',
  "script": """function calc(){
    let debts=[
      {name:'Debt 1', bal:+document.getElementById('d1').value||0, min:+document.getElementById('p1').value||0},
      {name:'Debt 2', bal:+document.getElementById('d2').value||0, min:+document.getElementById('p2').value||0},
      {name:'Debt 3', bal:+document.getElementById('d3').value||0, min:+document.getElementById('p3').value||0},
    ].filter(d=>d.bal>0);
    let extra=+document.getElementById('extra').value||0;
    debts.sort((a,b)=>a.bal-b.bal);
    let months=0, totalPaid=0, order=debts.map(d=>d.name);
    const maxMonths=1200;
    while(debts.some(d=>d.bal>0) && months<maxMonths){
      months++;
      let pool=extra;
      for(const d of debts){
        if(d.bal<=0) continue;
        let pay=d.min+pool;
        pool=0;
        if(pay>d.bal){ pool=pay-d.bal; pay=d.bal; }
        d.bal-=pay; totalPaid+=pay;
        if(pool>0) continue; else break;
      }
    }
    document.getElementById('res-main').textContent = months<maxMonths ? months+' months' : '20+ years';
    document.getElementById('res-totalpaid').innerHTML='<strong>$'+totalPaid.toFixed(2)+'</strong>';
    document.getElementById('res-order').innerHTML='<strong>'+order.join(' &rarr; ')+'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"The snowball method applies every extra dollar to your smallest balance first, while paying the minimum on everything else. Once the smallest debt is paid off, its entire payment rolls into the next-smallest debt, snowballing until every debt is gone. This calculator simulates that process month by month across up to three debts.",
  "faq":[
    ("Snowball vs. avalanche method?","Snowball pays off the smallest balance first for quick psychological wins; avalanche pays the highest interest rate first to save more money overall."),
    ("Does this include interest?","This simplified version models principal paydown only; real payoff timelines will be longer once interest accrual is factored in."),
    ("What if I have more than 3 debts?","List your largest debts here, or group smaller ones together, to get a close estimate.")
  ]
},
{
  "slug":"auto-loan-calculator","category":"finance","name":"Auto Loan Calculator",
  "intro":"Estimate your monthly car payment based on vehicle price, down payment, trade-in value, interest rate, and loan length.",
  "form_html": f'''<div class="calc-grid">
    {field("price","Vehicle price ($)",value="32000")}
    {field("down","Down payment ($)",value="3000")}
    {field("trade","Trade-in value ($)",value="0")}
    {field("rate","Interest rate (% / year)",value="7.2")}
    {select("months","Loan term",[("36","36 months"),("48","48 months"),("60","60 months"),("72","72 months"),("84","84 months")])}
  </div>{btn()}''',
  "result_html": f'''{big("Estimated monthly payment")}
    {row("res-total","Total of all payments")}
    {row("res-interest","Total interest paid")}
    {row("res-principal","Amount financed")}''',
  "script": """function calc(){
    const price=+document.getElementById('price').value||0;
    const down=+document.getElementById('down').value||0;
    const trade=+document.getElementById('trade').value||0;
    const rate=+document.getElementById('rate').value||0;
    const n=+document.getElementById('months').value||36;
    const principal=Math.max(price-down-trade,0);
    const r=rate/100/12;
    const m = r===0 ? principal/n : principal*r*Math.pow(1+r,n)/(Math.pow(1+r,n)-1);
    const total=m*n, interest=total-principal;
    document.getElementById('res-main').textContent = isFinite(m) ? '$'+m.toFixed(2)+' / mo' : '—';
    document.getElementById('res-total').innerHTML='<strong>$'+total.toFixed(2)+'</strong>';
    document.getElementById('res-interest').innerHTML='<strong>$'+interest.toFixed(2)+'</strong>';
    document.getElementById('res-principal').innerHTML='<strong>$'+principal.toFixed(2)+'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"This calculator subtracts your down payment and trade-in value from the vehicle price to get the amount financed, then applies the standard loan amortization formula across your chosen term. Example: financing $29,000 at 7.2% for 60 months comes to about $577/month.",
  "faq":[
    ("What's a good interest rate for a car loan?","Rates vary widely by credit score and loan age, but good credit typically sees roughly 5-9% on new cars as of recent years."),
    ("Should I choose a 60 or 72 month loan?","Longer terms lower your monthly payment but increase total interest paid and raise the risk of owing more than the car is worth."),
    ("Does this include tax, title, and fees?","No, enter the out-the-door price if you want those included, or treat this as principal and interest only.")
  ]
},

# ---------------- HEALTH ----------------
{
  "slug":"bmi-calculator","category":"health","name":"BMI Calculator",
  "intro":"Calculate your Body Mass Index (BMI) from your height and weight to see which weight category you fall into.",
  "form_html": f'''<div class="calc-grid">
    {field("weight","Weight (lbs)",value="160")}
    {field("height","Height (inches)",value="67")}
  </div>{btn()}''',
  "result_html": f'''{big("Your BMI")}
    {row("res-cat","Category")}''',
  "script": """function calc(){
    const w=+document.getElementById('weight').value||0;
    const h=+document.getElementById('height').value||0;
    const bmi = h>0 ? (w/(h*h))*703 : 0;
    let cat='—';
    if(bmi>0){
      if(bmi<18.5) cat='Underweight';
      else if(bmi<25) cat='Normal weight';
      else if(bmi<30) cat='Overweight';
      else cat='Obesity';
    }
    document.getElementById('res-main').textContent = bmi? bmi.toFixed(1):'—';
    document.getElementById('res-cat').innerHTML='<strong>'+cat+'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"BMI uses the formula weight(kg) / height(m)&sup2;, here computed from pounds and inches as 703 &times; weight / height&sup2;. Example: a 160 lb person at 5'7\\\" (67 in) has a BMI of about 25.1, just inside the \\\"overweight\\\" range.",
  "faq":[
    ("Is BMI accurate for everyone?","BMI doesn't account for muscle mass, so very muscular people may show as \\\"overweight\\\" despite having low body fat."),
    ("What's a healthy BMI range?","18.5 to 24.9 is generally considered the normal range for most adults."),
    ("Does BMI differ by age or sex?","Standard adult BMI categories don't adjust for age or sex, though some health providers use different thresholds for children and older adults.")
  ]
},
{
  "slug":"calorie-calculator","category":"health","name":"Calorie Calculator (TDEE)",
  "intro":"Find your Total Daily Energy Expenditure (TDEE) and daily calorie targets for maintaining, losing, or gaining weight.",
  "form_html": f'''<div class="calc-grid">
    {select("sex","Sex",[("male","Male"),("female","Female")])}
    {field("age","Age (years)",value="30",step="1")}
    {field("weight","Weight (kg)",value="75")}
    {field("height","Height (cm)",value="175")}
    {select("activity","Activity level",[("1.2","Sedentary (little/no exercise)"),("1.375","Light (1-3 days/week)"),("1.55","Moderate (3-5 days/week)"),("1.725","Active (6-7 days/week)"),("1.9","Very active (hard daily exercise)")])}
  </div>{btn()}''',
  "result_html": f'''{big("Maintenance calories (TDEE)")}
    {row("res-lose","To lose ~1 lb/week")}
    {row("res-gain","To gain ~1 lb/week")}''',
  "script": """function calc(){
    const sex=document.getElementById('sex').value;
    const age=+document.getElementById('age').value||0;
    const w=+document.getElementById('weight').value||0;
    const h=+document.getElementById('height').value||0;
    const act=+document.getElementById('activity').value||1.2;
    let bmr = sex==='male' ? 10*w+6.25*h-5*age+5 : 10*w+6.25*h-5*age-161;
    const tdee=bmr*act;
    document.getElementById('res-main').textContent=Math.round(tdee)+' kcal/day';
    document.getElementById('res-lose').innerHTML='<strong>'+Math.round(tdee-500)+' kcal/day</strong>';
    document.getElementById('res-gain').innerHTML='<strong>'+Math.round(tdee+500)+' kcal/day</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"This uses the Mifflin-St Jeor equation to estimate your Basal Metabolic Rate (BMR), then multiplies it by an activity factor to get TDEE &mdash; the calories you burn in a typical day. A deficit of about 500 calories/day from TDEE tends to produce roughly 1 lb of weight loss per week, and a 500-calorie surplus tends to produce roughly 1 lb of gain per week.",
  "faq":[
    ("How many calories should I eat to lose weight?","A deficit of about 500 calories/day below your TDEE typically produces around 1 lb of weight loss per week."),
    ("What is TDEE?","Total Daily Energy Expenditure &mdash; all the calories you burn in a day, including activity, not just resting metabolism."),
    ("Is this accurate for everyone?","It's a population-average estimate; individual metabolism can vary by 10% or more in either direction.")
  ]
},
{
  "slug":"pregnancy-due-date-calculator","category":"health","name":"Pregnancy Due Date Calculator",
  "intro":"Estimate your baby's due date based on the first day of your last menstrual period.",
  "form_html": f'''<div class="calc-grid">
    {field("lmp","First day of last period",type="date")}
  </div>{btn()}''',
  "result_html": f'''{big("Estimated due date")}
    {row("res-weeks","Current estimated week (as of today)")}''',
  "script": """function calc(){
    const lmp=document.getElementById('lmp').value;
    if(!lmp) return;
    const start=new Date(lmp+'T00:00:00');
    const due=new Date(start.getTime()+280*24*60*60*1000);
    const today=new Date();
    const daysPregnant=Math.floor((today-start)/(24*60*60*1000));
    const weeks=Math.floor(daysPregnant/7);
    document.getElementById('res-main').textContent=due.toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'});
    document.getElementById('res-weeks').innerHTML='<strong>'+ (weeks>=0 && weeks<45 ? 'Week '+weeks : '—') +'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"This adds 280 days (40 weeks) to the first day of your last menstrual period, the standard method used by most due-date estimators and healthcare providers (Naegele's rule).",
  "faq":[
    ("How accurate is this estimate?","Only about 5% of babies are born exactly on their due date; think of it as the center of a roughly two-week window."),
    ("Can I calculate from a conception date instead?","Yes &mdash; add 266 days to the conception date instead of 280 days from the last period."),
    ("Does cycle length affect this?","Yes, this assumes a standard 28-day cycle; shorter or longer cycles shift the actual due date somewhat.")
  ]
},
{
  "slug":"macro-calculator","category":"health","name":"Macro Calculator",
  "intro":"Get personalized protein, carbohydrate, and fat targets in grams based on your calorie needs and fitness goal.",
  "form_html": f'''<div class="calc-grid">
    {field("calories","Daily calorie target (kcal)",value="2200")}
    {select("goal","Goal",[("balanced","Balanced (30/40/30)"),("highprotein","High protein (40/30/30)"),("lowcarb","Lower carb (35/25/40)")])}
  </div>{btn()}''',
  "result_html": f'''{row("res-protein","Protein")}
    {row("res-carbs","Carbohydrates")}
    {row("res-fat","Fat")}''',
  "script": """function calc(){
    const cals=+document.getElementById('calories').value||0;
    const goal=document.getElementById('goal').value;
    let split = goal==='highprotein' ? [0.40,0.30,0.30] : goal==='lowcarb' ? [0.35,0.25,0.40] : [0.30,0.40,0.30];
    const proteinG=(cals*split[0])/4, carbsG=(cals*split[1])/4, fatG=(cals*split[2])/9;
    document.getElementById('res-protein').innerHTML='<strong>'+Math.round(proteinG)+' g</strong>';
    document.getElementById('res-carbs').innerHTML='<strong>'+Math.round(carbsG)+' g</strong>';
    document.getElementById('res-fat').innerHTML='<strong>'+Math.round(fatG)+' g</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Protein and carbs provide about 4 calories per gram, and fat provides about 9 calories per gram. This calculator splits your daily calorie target into grams using the percentage split for your chosen goal. Example: 2,200 kcal on a balanced 30/40/30 split works out to about 165g protein, 220g carbs, and 73g fat.",
  "faq":[
    ("What macro split is best for fat loss?","A common starting point is roughly 40% protein / 30% carbs / 30% fat, though any split that fits your calorie target and preferences can work."),
    ("Do I need to hit my macros exactly every day?","No &mdash; weekly averages matter far more than hitting an exact number every single day."),
    ("How do I find my calorie target?","Use a TDEE/calorie calculator first, then apply a deficit or surplus for your goal before splitting into macros.")
  ]
},
{
  "slug":"one-rep-max-calculator","category":"health","name":"One-Rep Max Calculator",
  "intro":"Estimate your one-rep max (1RM) for any lift using the weight and reps from a recent set.",
  "form_html": f'''<div class="calc-grid">
    {field("weight","Weight lifted (lbs or kg)",value="185")}
    {field("reps","Reps completed",value="5",step="1")}
  </div>{btn()}''',
  "result_html": f'''{big("Estimated one-rep max")}
    {row("res-90","90% of 1RM")}
    {row("res-80","80% of 1RM")}
    {row("res-70","70% of 1RM")}''',
  "script": """function calc(){
    const w=+document.getElementById('weight').value||0;
    const reps=+document.getElementById('reps').value||1;
    const onerm = reps<=1 ? w : w*(1+reps/30);
    document.getElementById('res-main').textContent=onerm.toFixed(1);
    document.getElementById('res-90').innerHTML='<strong>'+(onerm*0.9).toFixed(1)+'</strong>';
    document.getElementById('res-80').innerHTML='<strong>'+(onerm*0.8).toFixed(1)+'</strong>';
    document.getElementById('res-70').innerHTML='<strong>'+(onerm*0.7).toFixed(1)+'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"This uses the Epley formula: 1RM = weight &times; (1 + reps/30). Example: lifting 185 for 5 reps estimates a one-rep max of about 216. The percentage breakdowns below are commonly used to plan training weights for strength programs.",
  "faq":[
    ("Is this accurate for high rep sets?","Accuracy decreases above about 10 reps; the formula is most reliable for sets of 1-5 reps."),
    ("How often should I test my actual 1RM?","Most lifters test every 8-12 weeks to track progress while avoiding the injury risk of frequent true max attempts."),
    ("Does this work the same for any exercise?","It works reasonably well for most barbell compound lifts; isolation exercises can behave differently.")
  ]
},

# ---------------- CONSTRUCTION ----------------
{
  "slug":"concrete-calculator","category":"construction","name":"Concrete Calculator",
  "intro":"Calculate how many cubic yards of concrete you need for a slab, footing, or driveway.",
  "form_html": f'''<div class="calc-grid">
    {field("length","Length (ft)",value="20")}
    {field("width","Width (ft)",value="10")}
    {field("depth","Depth (inches)",value="4")}
  </div>{btn()}''',
  "result_html": f'''{big("Cubic yards needed")}
    {row("res-withwaste","With 10% waste allowance")}
    {row("res-bags","Approx. 80 lb bags (if bagged mix)")}''',
  "script": """function calc(){
    const l=+document.getElementById('length').value||0;
    const w=+document.getElementById('width').value||0;
    const d=+document.getElementById('depth').value||0;
    const cuft = l*w*(d/12);
    const cuyd = cuft/27;
    document.getElementById('res-main').textContent=cuyd.toFixed(2)+' yd³';
    document.getElementById('res-withwaste').innerHTML='<strong>'+(cuyd*1.1).toFixed(2)+' yd³</strong>';
    document.getElementById('res-bags').innerHTML='<strong>~'+Math.ceil(cuyd*54)+' bags</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Cubic yards = (length &times; width &times; depth in feet) &divide; 27. Depth is entered in inches and converted to feet. Example: a 20&times;10 ft slab at 4 inches deep needs about 2.47 cubic yards. Most contractors add 5-10% extra to cover spillage and an uneven subgrade.",
  "faq":[
    ("How much extra concrete should I order?","Most contractors add 5-10% to account for spillage and an uneven subgrade."),
    ("How thick should a driveway slab be?","Typically 4 inches for passenger cars, 6 inches for driveways that will carry heavier vehicles."),
    ("How many 80 lb bags make a cubic yard?","Roughly 54 bags of 80 lb bagged concrete mix make one cubic yard.")
  ]
},
{
  "slug":"paint-calculator","category":"construction","name":"Paint Calculator",
  "intro":"Find out how many gallons of paint you need for a room based on wall dimensions, doors, windows, and number of coats.",
  "form_html": f'''<div class="calc-grid">
    {field("perimeter","Room perimeter (ft)",value="56")}
    {field("wallheight","Wall height (ft)",value="9")}
    {field("doors","Number of doors",value="2",step="1")}
    {field("windows","Number of windows",value="3",step="1")}
    {select("coats","Number of coats",[("1","1 coat"),("2","2 coats")])}
  </div>{btn()}''',
  "result_html": f'''{big("Gallons needed")}
    {row("res-area","Paintable wall area")}''',
  "script": """function calc(){
    const perim=+document.getElementById('perimeter').value||0;
    const h=+document.getElementById('wallheight').value||0;
    const doors=+document.getElementById('doors').value||0;
    const windows=+document.getElementById('windows').value||0;
    const coats=+document.getElementById('coats').value||1;
    const grossArea = perim*h;
    const deductions = doors*20 + windows*15; // approx sq ft each
    const netArea = Math.max(grossArea-deductions,0);
    const gallons = (netArea*coats)/350;
    document.getElementById('res-main').textContent=gallons.toFixed(1)+' gal';
    document.getElementById('res-area').innerHTML='<strong>'+netArea.toFixed(0)+' sq ft</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Gallons = (paintable wall area &times; number of coats) &divide; 350, since one gallon of paint typically covers about 350 sq ft per coat. Doors are estimated at 20 sq ft and windows at 15 sq ft each and subtracted from the gross wall area.",
  "faq":[
    ("Do I need to subtract windows and doors?","Yes, for accuracy subtract their combined area from the total wall area &mdash; this calculator does it automatically using standard estimates."),
    ("How many coats should I plan for?","Two coats is standard for full, even color coverage, especially over a different base color."),
    ("Does one gallon really cover 350 sq ft?","That's the typical manufacturer estimate for smooth walls; textured surfaces may need more.")
  ]
},
{
  "slug":"flooring-calculator","category":"construction","name":"Flooring Calculator",
  "intro":"Calculate how much flooring material and how many boxes you need, including a waste allowance for cuts.",
  "form_html": f'''<div class="calc-grid">
    {field("length","Room length (ft)",value="14")}
    {field("width","Room width (ft)",value="12")}
    {field("coverage","Coverage per box (sq ft)",value="20")}
    {field("waste","Waste allowance (%)",value="10")}
  </div>{btn()}''',
  "result_html": f'''{big("Boxes needed")}
    {row("res-area","Room area")}
    {row("res-areaneeded","Total sq ft to buy (with waste)")}''',
  "script": """function calc(){
    const l=+document.getElementById('length').value||0;
    const w=+document.getElementById('width').value||0;
    const cov=+document.getElementById('coverage').value||1;
    const waste=+document.getElementById('waste').value||0;
    const area=l*w;
    const areaNeeded=area*(1+waste/100);
    const boxes=Math.ceil(areaNeeded/cov);
    document.getElementById('res-main').textContent=boxes+' boxes';
    document.getElementById('res-area').innerHTML='<strong>'+area.toFixed(0)+' sq ft</strong>';
    document.getElementById('res-areaneeded').innerHTML='<strong>'+areaNeeded.toFixed(0)+' sq ft</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Room area = length &times; width. We add your waste percentage to that area, then divide by the coverage per box (from the product packaging) and round up, since boxes must be bought whole.",
  "faq":[
    ("Why add 10% extra?","To cover cuts, mistakes, and future repairs made with material from the same batch and dye lot."),
    ("Does this work for tile, laminate, and hardwood?","Yes &mdash; just enter the coverage per box or carton listed on your specific product's packaging."),
    ("Should I round up or down on boxes?","Always round up; partial boxes still need to be purchased in full.")
  ]
},
{
  "slug":"mulch-calculator","category":"construction","name":"Mulch Calculator",
  "intro":"Calculate how many cubic yards (and bags) of mulch you need for your garden beds.",
  "form_html": f'''<div class="calc-grid">
    {field("area","Bed area (sq ft)",value="200")}
    {field("depth","Desired depth (inches)",value="3")}
  </div>{btn()}''',
  "result_html": f'''{big("Cubic yards needed")}
    {row("res-bags2","Standard 2 cu ft bags needed")}''',
  "script": """function calc(){
    const area=+document.getElementById('area').value||0;
    const depth=+document.getElementById('depth').value||0;
    const cuyd=(area*depth)/324;
    document.getElementById('res-main').textContent=cuyd.toFixed(2)+' yd³';
    document.getElementById('res-bags2').innerHTML='<strong>'+Math.ceil(cuyd*13.5)+' bags</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Cubic yards = (area in sq ft &times; depth in inches) &divide; 324. Example: a 200 sq ft bed at 3 inches deep needs about 1.85 cubic yards, or roughly 25 standard 2 cu ft bags.",
  "faq":[
    ("How deep should mulch be?","2-3 inches is standard &mdash; enough to suppress weeds without smothering plant roots."),
    ("How many bags is a cubic yard?","Roughly 13-14 standard 2 cubic foot bags make one cubic yard."),
    ("Should I remove old mulch first?","Not usually &mdash; a couple inches of old, decomposed mulch can stay; just top it off to your target depth.")
  ]
},
{
  "slug":"roofing-calculator","category":"construction","name":"Roofing Calculator",
  "intro":"Estimate how many roofing squares and shingle bundles you need based on your roof's area.",
  "form_html": f'''<div class="calc-grid">
    {field("area","Roof area (sq ft)",value="1800")}
    {field("waste","Waste allowance (%)",value="10")}
  </div>{btn()}''',
  "result_html": f'''{big("Roofing squares needed")}
    {row("res-bundles","Shingle bundles (3 per square)")}''',
  "script": """function calc(){
    const area=+document.getElementById('area').value||0;
    const waste=+document.getElementById('waste').value||0;
    const squares=(area*(1+waste/100))/100;
    document.getElementById('res-main').textContent=squares.toFixed(1)+' squares';
    document.getElementById('res-bundles').innerHTML='<strong>'+Math.ceil(squares*3)+' bundles</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"A roofing \\\"square\\\" equals 100 sq ft of roof area. Squares = (roof area &times; (1 + waste%)) &divide; 100, and most standard shingles come 3 bundles to a square.",
  "faq":[
    ("What's a roofing 'square'?","100 square feet of roof area &mdash; the standard unit roofers use for estimating materials."),
    ("How much extra should I order?","Add about 10% for waste, cuts, and ridge caps; steep or complex roofs may need more."),
    ("Does this account for roof pitch?","No, enter the actual sloped surface area, which is larger than the home's footprint on a pitched roof.")
  ]
},

# ---------------- EVERYDAY MATH ----------------
{
  "slug":"percentage-calculator","category":"everyday-math","name":"Percentage Calculator",
  "intro":"Calculate what percent one number is of another, find a percentage of a number, or calculate percentage change.",
  "form_html": f'''<div class="calc-grid">
    {field("x","Value X",value="40")}
    {field("y","Value Y",value="160")}
  </div>{btn()}
  <p class="hint" style="margin-top:10px">Shows: X% of Y, X as a % of Y, and the % change from X to Y.</p>''',
  "result_html": f'''{row("res-xofy","X% of Y")}
    {row("res-xisy","X as a percent of Y")}
    {row("res-change","Percent change from X to Y")}''',
  "script": """function calc(){
    const x=+document.getElementById('x').value||0;
    const y=+document.getElementById('y').value||0;
    const xofy=(x/100)*y;
    const xisy = y!==0 ? (x/y)*100 : 0;
    const change = x!==0 ? ((y-x)/x)*100 : 0;
    document.getElementById('res-xofy').innerHTML='<strong>'+xofy.toFixed(2)+'</strong>';
    document.getElementById('res-xisy').innerHTML='<strong>'+xisy.toFixed(2)+'%</strong>';
    document.getElementById('res-change').innerHTML='<strong>'+change.toFixed(2)+'%</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Three common percentage calculations: X% of Y = (X/100)&times;Y; X as a percent of Y = (X/Y)&times;100; percent change from X to Y = ((Y&minus;X)/X)&times;100. Example: 40% of 160 is 64, and the change from 40 to 160 is a 300% increase.",
  "faq":[
    ("How do I calculate percentage increase?","Use ((new &minus; old) / old) &times; 100 &mdash; a positive result is an increase, negative is a decrease."),
    ("How do I find 15% of a number?","Multiply the number by 0.15, or enter 15 as X and the number as Y above."),
    ("Why is X as a percent of Y different from X% of Y?","They answer different questions: one scales Y by a percentage, the other expresses X relative to Y as a percentage.")
  ]
},
{
  "slug":"age-calculator","category":"everyday-math","name":"Age Calculator",
  "intro":"Find your exact age in years, months, and days from your birth date.",
  "form_html": f'''<div class="calc-grid">
    {field("dob","Date of birth",type="date")}
    {field("asof","As of date",type="date")}
  </div>{btn()}''',
  "result_html": f'''{big("Your age")}
    {row("res-days","Total days lived")}''',
  "script": """function calc(){
    const dob=document.getElementById('dob').value;
    let asof=document.getElementById('asof').value;
    if(!dob) return;
    const start=new Date(dob+'T00:00:00');
    const end=asof? new Date(asof+'T00:00:00') : new Date();
    let years=end.getFullYear()-start.getFullYear();
    let months=end.getMonth()-start.getMonth();
    let days=end.getDate()-start.getDate();
    if(days<0){ months--; const prevMonth=new Date(end.getFullYear(),end.getMonth(),0); days+=prevMonth.getDate(); }
    if(months<0){ years--; months+=12; }
    const totalDays=Math.floor((end-start)/(24*60*60*1000));
    document.getElementById('res-main').textContent=years+'y '+months+'m '+days+'d';
    document.getElementById('res-days').innerHTML='<strong>'+totalDays.toLocaleString()+' days</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"This subtracts your birth date from the reference date (today, by default), carrying over months and days correctly across different month lengths and leap years.",
  "faq":[
    ("Why isn't my age just years divided evenly?","Because months have different lengths and leap years add an extra day every 4 years, so simple division doesn't give an exact age."),
    ("Can I calculate age as of a future or past date?","Yes, enter any reference date instead of leaving it on today."),
    ("Does this account for leap years?","Yes, it uses actual calendar dates, so leap years are handled automatically.")
  ]
},
{
  "slug":"date-difference-calculator","category":"everyday-math","name":"Date Difference Calculator",
  "intro":"Calculate the exact number of days, weeks, or months between two dates.",
  "form_html": f'''<div class="calc-grid">
    {field("start","Start date",type="date")}
    {field("end","End date",type="date")}
  </div>{btn()}''',
  "result_html": f'''{big("Days between")}
    {row("res-weeks","Weeks (and remainder days)")}
    {row("res-months","Approximate months")}''',
  "script": """function calc(){
    const s=document.getElementById('start').value;
    const e=document.getElementById('end').value;
    if(!s||!e) return;
    const start=new Date(s+'T00:00:00'), end=new Date(e+'T00:00:00');
    const days=Math.round((end-start)/(24*60*60*1000));
    const weeks=Math.floor(Math.abs(days)/7), rem=Math.abs(days)%7;
    const months=(days/30.44).toFixed(1);
    document.getElementById('res-main').textContent=days+' days';
    document.getElementById('res-weeks').innerHTML='<strong>'+weeks+' weeks, '+rem+' days</strong>';
    document.getElementById('res-months').innerHTML='<strong>~'+months+' months</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"This subtracts the start date from the end date in milliseconds and converts to whole days, then expresses that span in weeks and approximate months (using an average month length of 30.44 days).",
  "faq":[
    ("Does this count the end date?","This calculator shows the number of full days between the two dates; add 1 if you need an inclusive count of both dates."),
    ("Can I exclude weekends for business-day counts?","Not in this simple version &mdash; a dedicated business-days calculator excludes Saturdays and Sundays."),
    ("Why are the months approximate?","Months vary from 28 to 31 days, so any days-to-months conversion uses an average month length.")
  ]
},
{
  "slug":"gpa-calculator","category":"everyday-math","name":"GPA Calculator",
  "intro":"Calculate your semester GPA from your course grades and credit hours.",
  "form_html": f'''<div class="calc-grid">
    {select("g1","Course 1 grade",[("4","A"),("3.7","A-"),("3.3","B+"),("3","B"),("2.7","B-"),("2.3","C+"),("2","C"),("1","D"),("0","F")])}
    {field("c1","Course 1 credit hours",value="3",step="0.5")}
    {select("g2","Course 2 grade",[("4","A"),("3.7","A-"),("3.3","B+"),("3","B"),("2.7","B-"),("2.3","C+"),("2","C"),("1","D"),("0","F")])}
    {field("c2","Course 2 credit hours",value="3",step="0.5")}
    {select("g3","Course 3 grade",[("4","A"),("3.7","A-"),("3.3","B+"),("3","B"),("2.7","B-"),("2.3","C+"),("2","C"),("1","D"),("0","F")])}
    {field("c3","Course 3 credit hours",value="3",step="0.5")}
  </div>{btn()}''',
  "result_html": f'''{big("Your GPA")}
    {row("res-hours","Total credit hours")}''',
  "script": """function calc(){
    const courses=[[1,1],[2,2],[3,3]].map(([g,c])=>[+document.getElementById('g'+g).value, +document.getElementById('c'+c).value||0]);
    let points=0, hours=0;
    for(const [grade,credit] of courses){ points+=grade*credit; hours+=credit; }
    const gpa = hours>0 ? points/hours : 0;
    document.getElementById('res-main').textContent=gpa.toFixed(2);
    document.getElementById('res-hours').innerHTML='<strong>'+hours+'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"GPA = &Sigma;(grade points &times; credit hours) &divide; &Sigma;(credit hours). Each letter grade is converted to its standard point value (A=4.0, A-=3.7, etc.), multiplied by that course's credit hours, summed, then divided by total credit hours.",
  "faq":[
    ("What's the difference between weighted and unweighted GPA?","Weighted GPA gives extra points for AP, IB, or honors courses (sometimes up to 5.0 scale); unweighted treats every course equally on a 4.0 scale."),
    ("How do I calculate cumulative GPA across semesters?","Total all grade points earned across every semester, divided by total credit hours attempted across all semesters."),
    ("Does a withdrawal (W) affect GPA?","Typically no, a W is excluded from GPA calculations at most schools, though policies vary.")
  ]
},
{
  "slug":"tip-calculator","category":"everyday-math","name":"Tip Calculator",
  "intro":"Calculate the tip amount and total bill, with an option to split the cost between multiple people.",
  "form_html": f'''<div class="calc-grid">
    {field("bill","Bill amount ($)",value="68")}
    {field("tip","Tip percentage (%)",value="18")}
    {field("people","Number of people",value="2",step="1")}
  </div>{btn()}''',
  "result_html": f'''{big("Tip amount")}
    {row("res-total","Total bill (with tip)")}
    {row("res-perperson","Per person (bill + tip)")}''',
  "script": """function calc(){
    const bill=+document.getElementById('bill').value||0;
    const tipPct=+document.getElementById('tip').value||0;
    const people=+document.getElementById('people').value||1;
    const tip=bill*(tipPct/100);
    const total=bill+tip;
    document.getElementById('res-main').textContent='$'+tip.toFixed(2);
    document.getElementById('res-total').innerHTML='<strong>$'+total.toFixed(2)+'</strong>';
    document.getElementById('res-perperson').innerHTML='<strong>$'+(total/people).toFixed(2)+'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Tip = bill &times; tip percentage. Total = bill + tip. When splitting, the total is divided evenly by the number of people.",
  "faq":[
    ("What's a standard tip percentage?","15-20% is standard in the US for good service at a sit-down restaurant."),
    ("How do I split a bill unevenly?","This calculator splits evenly; for itemized splitting, each person should total their own items plus a proportional share of tax and tip."),
    ("Should tip be calculated before or after tax?","Etiquette varies, but many people calculate tip on the pre-tax subtotal.")
  ]
},

# ---------------- BUSINESS ----------------
{
  "slug":"profit-margin-calculator","category":"business","name":"Profit Margin Calculator",
  "intro":"Calculate your profit margin and markup percentage from your cost and selling price.",
  "form_html": f'''<div class="calc-grid">
    {field("cost","Cost ($)",value="40")}
    {field("price","Selling price ($)",value="65")}
  </div>{btn()}''',
  "result_html": f'''{big("Profit margin")}
    {row("res-markup","Markup percentage")}
    {row("res-profit","Profit per unit")}''',
  "script": """function calc(){
    const cost=+document.getElementById('cost').value||0;
    const price=+document.getElementById('price').value||0;
    const profit=price-cost;
    const margin = price!==0 ? (profit/price)*100 : 0;
    const markup = cost!==0 ? (profit/cost)*100 : 0;
    document.getElementById('res-main').textContent=margin.toFixed(1)+'%';
    document.getElementById('res-markup').innerHTML='<strong>'+markup.toFixed(1)+'%</strong>';
    document.getElementById('res-profit').innerHTML='<strong>$'+profit.toFixed(2)+'</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Margin % = ((price &minus; cost) / price) &times; 100. Markup % = ((price &minus; cost) / cost) &times; 100. Example: a $40 cost sold for $65 gives a 38.5% margin but a 62.5% markup &mdash; the same dollar profit expressed two different ways.",
  "faq":[
    ("What's the difference between margin and markup?","Margin is profit as a percent of selling price; markup is profit as a percent of cost &mdash; they're always different numbers for the same sale."),
    ("What's a good profit margin?","It varies widely by industry &mdash; retail often runs 20-50%, while services and software can run much higher."),
    ("How do I price for a target margin?","Price = cost / (1 &minus; target margin), e.g. for a 40% margin on a $40 cost: 40 / 0.6 = $66.67.")
  ]
},
{
  "slug":"break-even-calculator","category":"business","name":"Break-Even Point Calculator",
  "intro":"Find out how many units you need to sell to cover your costs before you start making a profit.",
  "form_html": f'''<div class="calc-grid">
    {field("fixed","Fixed costs ($)",value="5000")}
    {field("price","Price per unit ($)",value="25")}
    {field("variable","Variable cost per unit ($)",value="10")}
  </div>{btn()}''',
  "result_html": f'''{big("Break-even units")}
    {row("res-revenue","Break-even revenue")}''',
  "script": """function calc(){
    const fixed=+document.getElementById('fixed').value||0;
    const price=+document.getElementById('price').value||0;
    const variable=+document.getElementById('variable').value||0;
    const contribution=price-variable;
    const units = contribution>0 ? fixed/contribution : Infinity;
    document.getElementById('res-main').textContent = isFinite(units) ? Math.ceil(units).toLocaleString()+' units' : 'Not achievable';
    document.getElementById('res-revenue').innerHTML = isFinite(units) ? '<strong>$'+(units*price).toFixed(2)+'</strong>' : '<strong>—</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Break-even units = fixed costs / (price per unit &minus; variable cost per unit). The denominator is your \\\"contribution margin\\\" &mdash; what each unit contributes toward covering fixed costs after its own variable cost.",
  "faq":[
    ("What counts as a fixed cost?","Rent, salaries, and insurance &mdash; costs that don't change with how many units you sell."),
    ("What if my variable cost is higher than my price?","You can never break even; you lose money on every unit sold, regardless of volume."),
    ("Does break-even mean I'm profitable?","No &mdash; it means you've covered costs exactly. Every unit sold beyond break-even is profit.")
  ]
},
{
  "slug":"amazon-fba-fee-calculator","category":"business","name":"Amazon FBA Fee Calculator",
  "intro":"Estimate Amazon's referral and FBA fulfillment fees to find your true profit per unit.",
  "form_html": f'''<div class="calc-grid">
    {field("price","Sale price ($)",value="24.99")}
    {field("cost","Product cost ($)",value="7")}
    {field("referral","Referral fee (%)",value="15")}
    {field("fulfillment","FBA fulfillment fee ($)",value="5.5")}
    {field("storage","Monthly storage fee, per unit ($)",value="0.4")}
  </div>{btn()}''',
  "result_html": f'''{big("Net profit per unit")}
    {row("res-fees","Total fees")}
    {row("res-margin2","Profit margin")}''',
  "script": """function calc(){
    const price=+document.getElementById('price').value||0;
    const cost=+document.getElementById('cost').value||0;
    const referralPct=+document.getElementById('referral').value||0;
    const fulfillment=+document.getElementById('fulfillment').value||0;
    const storage=+document.getElementById('storage').value||0;
    const referralFee=price*(referralPct/100);
    const totalFees=referralFee+fulfillment+storage;
    const profit=price-cost-totalFees;
    const margin = price!==0 ? (profit/price)*100 : 0;
    document.getElementById('res-main').textContent='$'+profit.toFixed(2);
    document.getElementById('res-fees').innerHTML='<strong>$'+totalFees.toFixed(2)+'</strong>';
    document.getElementById('res-margin2').innerHTML='<strong>'+margin.toFixed(1)+'%</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Net profit = sale price &minus; product cost &minus; referral fee &minus; fulfillment fee &minus; storage fee. The referral fee is a percentage of sale price (varies by category, commonly 8-17%); fulfillment and storage fees come from Amazon's published FBA rate tables based on size and weight tier.",
  "faq":[
    ("What's included in the FBA fulfillment fee?","Picking, packing, shipping, and customer service for that order, based on your product's size and weight tier."),
    ("How do I lower my FBA fees?","Optimizing product dimensions and weight to stay within a lower size tier is the most common way to reduce fulfillment costs."),
    ("Does this include advertising costs?","No, enter any PPC/advertising spend per unit separately if you want it reflected in your true profit.")
  ]
},

# ---------------- AUTOMOTIVE ----------------
{
  "slug":"gas-cost-calculator","category":"automotive","name":"Gas Cost Calculator",
  "intro":"Calculate how much a road trip or daily commute will cost in gas based on distance, fuel efficiency, and gas price.",
  "form_html": f'''<div class="calc-grid">
    {field("distance","Distance (miles)",value="300")}
    {field("mpg","Fuel efficiency (MPG)",value="28")}
    {field("gasprice","Price per gallon ($)",value="3.45")}
  </div>{btn()}''',
  "result_html": f'''{big("Total gas cost")}
    {row("res-gallons","Gallons needed")}''',
  "script": """function calc(){
    const dist=+document.getElementById('distance').value||0;
    const mpg=+document.getElementById('mpg').value||1;
    const price=+document.getElementById('gasprice').value||0;
    const gallons=dist/mpg;
    const cost=gallons*price;
    document.getElementById('res-main').textContent='$'+cost.toFixed(2);
    document.getElementById('res-gallons').innerHTML='<strong>'+gallons.toFixed(2)+' gal</strong>';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Gallons needed = distance &divide; MPG. Total cost = gallons &times; price per gallon. Example: a 300-mile trip at 28 MPG with gas at $3.45/gal costs about $36.96.",
  "faq":[
    ("How do I find my car's actual MPG?","Divide miles driven by gallons used at your last fill-up, or check your owner's manual for the EPA-rated combined MPG."),
    ("Does this account for highway vs. city driving?","Enter your combined MPG for the most realistic estimate, or use your highway MPG for a long road trip."),
    ("Does this include tolls or other trip costs?","No, this covers fuel cost only.")
  ]
},

# ---------------- EDUCATION ----------------
{
  "slug":"final-grade-calculator","category":"education","name":"Final Grade Calculator",
  "intro":"Find out what score you need on your final exam to get the grade you want in the class.",
  "form_html": f'''<div class="calc-grid">
    {field("current","Current grade (%)",value="85")}
    {field("weight","Final exam weight (%)",value="20")}
    {field("desired","Desired final grade (%)",value="90")}
  </div>{btn()}''',
  "result_html": f'''{big("Score needed on final")}''',
  "script": """function calc(){
    const current=+document.getElementById('current').value||0;
    const weight=(+document.getElementById('weight').value||0)/100;
    const desired=+document.getElementById('desired').value||0;
    const needed = weight>0 ? (desired-(current*(1-weight)))/weight : 0;
    document.getElementById('res-main').textContent = needed>100 ? needed.toFixed(1)+'% (not achievable)' : needed<0 ? '0% (already secured)' : needed.toFixed(1)+'%';
    document.getElementById('result').classList.add('show');
  }""",
  "how_it_works":"Desired grade = (current grade &times; (1 &minus; exam weight)) + (final exam score &times; exam weight). Solving for the final exam score gives: needed score = (desired grade &minus; current grade &times; (1 &minus; weight)) / weight.",
  "faq":[
    ("What if the required score is over 100%?","It means that grade isn't achievable from the final exam alone &mdash; check for extra credit or a different weighting."),
    ("Does this work for any weighting system?","Yes, enter your exam's weight as a percentage of the total final grade."),
    ("What if I don't know my current grade exactly?","Use your best estimate from your syllabus's grade breakdown; small errors won't change the needed score dramatically.")
  ]
},
]


def simple_page(slug, title, body_html):
    body = f'<div class="page-head"><h1>{title}</h1></div><div class="card">{body_html}</div>'
    out = page_shell(f"{title} | {SITE_NAME}", title, body, f"{BASE_URL}/{slug}/")
    path = os.path.join(OUT, slug)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "index.html"), "w") as f:
        f.write(out)

def static_pages():
    simple_page("about", "About Calcly", f"""
    <p>{SITE_NAME} builds fast, free calculators for the everyday decisions people actually search for &mdash;
    from mortgage payments and paychecks to concrete estimates and calorie targets. Every calculator runs
    entirely in your browser: no account, no email wall, and your numbers are never sent anywhere.</p>
    <p>We're building toward thousands of calculators across finance, health, construction, business, and
    everyday math. If there's a calculator you'd like to see, <a href="/contact/">let us know</a>.</p>
    """)
    simple_page("privacy", "Privacy Policy", f"""
    <p><em>Last updated: 2026.</em></p>
    <p>{SITE_NAME} does not require an account and does not collect the numbers you enter into any calculator
    &mdash; all calculations run locally in your browser using JavaScript, and your inputs are never transmitted
    to our servers.</p>
    <p>We use standard web analytics (such as Google Analytics) to understand aggregate traffic patterns, and
    we may display advertising through third-party ad networks (such as Google AdSense), which may use cookies
    to serve relevant ads. You can control cookie preferences through your browser settings or by visiting
    Google's Ads Settings page.</p>
    <p>If you have questions about this policy, <a href="/contact/">contact us</a>.</p>
    """)
    simple_page("terms", "Terms of Use", f"""
    <p>{SITE_NAME}'s calculators are provided for general informational and educational purposes only, and do
    not constitute financial, medical, legal, or professional advice of any kind. Results are estimates based
    on the inputs you provide and standard formulas; always consult a qualified professional before making
    financial, health, or legal decisions.</p>
    <p>We make reasonable efforts to keep calculators accurate, but we make no warranties about completeness,
    reliability, or accuracy, and are not liable for decisions made based on these tools.</p>
    """)
    simple_page("contact", "Contact", f"""
    <p>Questions, feedback, or a calculator you'd like us to build? Reach out at
    <a href="mailto:hello@calcly.tools">hello@calcly.tools</a>.</p>
    """)

# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    for c in CALCULATORS:
        calc_page(c)
    for slug, cat in CATEGORIES.items():
        category_page(slug, cat)
    homepage()
    static_pages()
    sitemap_and_robots()
    print(f"Built {len(CALCULATORS)} calculator pages across {len(CATEGORIES)} categories + static pages.")
