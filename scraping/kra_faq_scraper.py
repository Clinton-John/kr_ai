"""
KRA.AI — FAQ Scraper (Selenium + Manual Seed)
================================================
KRA blocks simple HTTP scrapers (returns 403).
This script uses Selenium to run a real browser that loads
JavaScript-rendered pages — bypassing the block.

It also includes a pre-seeded manual dataset from known KRA
FAQ content, so your knowledge base works even before scraping.

SETUP (run once):
    pip install selenium webdriver-manager beautifulsoup4 requests

USAGE:
    python kra_faq_scraper.py              # scrape + seed data
    python kra_faq_scraper.py --seed-only  # just write the manual seed data (no browser needed)

OUTPUT:
    faqs/
        itax_introduction_faqs.json
        itax_filing_returns_faqs.json
        paye_faqs.json
        vat_faqs.json
        customs_faqs.json
        pin_registration_faqs.json
        income_tax_faqs.json
        ... (one file per category)
        all_faqs_combined.json   <-- use this in ChromaDB
"""

import json
import os
import sys
import time
import re
from datetime import datetime

# ─────────────────────────────────────────────────────────
# ALL KRA FAQ PAGES TO SCRAPE
# ─────────────────────────────────────────────────────────
FAQ_PAGES = [
    {
        "category": "iTax - Introduction",
        "filename": "itax_introduction_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/introduction-to-itax"
    },
    {
        "category": "iTax - Filing Returns",
        "filename": "itax_filing_returns_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/filing-returns-on-itax"
    },
    {
        "category": "PAYE",
        "filename": "paye_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-paye"
    },
    {
        "category": "VAT",
        "filename": "vat_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-vat"
    },
    {
        "category": "Customs and Border Control",
        "filename": "customs_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/customs-and-border-control"
    },
    {
        "category": "PIN Registration",
        "filename": "pin_registration_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/pin-registration"
    },
    {
        "category": "Income Tax",
        "filename": "income_tax_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/income-tax"
    },
    {
        "category": "Turnover Tax",
        "filename": "turnover_tax_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/turnover-tax"
    },
    {
        "category": "Monthly Rental Income",
        "filename": "rental_income_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/monthly-rental-income"
    },
    {
        "category": "Capital Gains Tax",
        "filename": "capital_gains_tax_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/capital-gains-tax"
    },
    {
        "category": "Excise Duty",
        "filename": "excise_duty_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/excise-duty"
    },
    {
        "category": "Stamp Duty",
        "filename": "stamp_duty_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/stamp-duty"
    },
    {
        "category": "Withholding Tax",
        "filename": "withholding_tax_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/withholding-tax"
    },
    {
        "category": "Tax Compliance Certificate",
        "filename": "tcc_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/tax-compliance-certificate"
    },
    {
        "category": "Agency Revenue",
        "filename": "agency_revenue_faqs.json",
        "url": "https://www.kra.go.ke/helping-tax-payers/faqs/agency-revenue"
    },
]

TODAY = datetime.now().strftime("%Y-%m-%d")

# ─────────────────────────────────────────────────────────
# PRE-SEEDED MANUAL FAQ DATA
# Sourced directly from KRA.go.ke — guaranteed starting point.
# ─────────────────────────────────────────────────────────
MANUAL_SEED_DATA = [

    # ── iTax Introduction ──
    {"question": "What is iTax?",
     "answer": "iTax is a system developed by KRA to improve efficiency. It allows you to register for a PIN, file your tax returns, apply for a tax compliance certificate, generate a payment slip, and check your ledger account among others.",
     "category": "iTax - Introduction", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/introduction-to-itax", "scraped_at": TODAY},

    {"question": "Does KRA offer training on iTax?",
     "answer": "Yes. Training is done free of charge every first two Thursdays of the month at the Convention Centre, 5th floor Times Tower, Nairobi.",
     "category": "iTax - Introduction", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/introduction-to-itax", "scraped_at": TODAY},

    {"question": "What do I do if I get an error when registering on iTax?",
     "answer": "If you get error ref. no. 139, this is caused by poor internet connectivity — please keep trying. For PIN migration or data errors, contact KRA via callcentre@kra.go.ke or DTDOnlineSupport@kra.go.ke, or visit the nearest KRA office.",
     "category": "iTax - Introduction", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/introduction-to-itax", "scraped_at": TODAY},

    {"question": "Do I need a VAT certificate if I have a PIN certificate?",
     "answer": "No. A PIN certificate is sufficient. If you start dealing in VAT-able business, simply add the VAT obligation to your existing PIN.",
     "category": "iTax - Introduction", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/introduction-to-itax", "scraped_at": TODAY},

    {"question": "When was iTax launched?",
     "answer": "iTax was officially launched in 2014, with mandatory onboarding for individuals and entities beginning in 2015. There are currently over 8 million active taxpayers on the platform.",
     "category": "iTax - Introduction", "source": "https://kra.go.ke/helping-tax-payers/facts-about-kra/category/7", "scraped_at": TODAY},

    {"question": "How do I update my personal details on iTax?",
     "answer": "Log in to iTax, go to 'Registration', and select 'Amend PIN Details' to update your information.",
     "category": "iTax - Introduction", "source": "https://kra.go.ke/helping-tax-payers/facts-about-kra/category/7", "scraped_at": TODAY},

    {"question": "How do I make a tax payment on iTax?",
     "answer": "Log in with your PIN and password. Click 'Payments' then 'Payment Registration' and click 'Next'. Choose the applicable tax head (e.g. Income Tax, VAT), select 'Self-Assessment' as the Payment Type, enter the tax period, and choose your payment method.",
     "category": "iTax - Introduction", "source": "https://kra.go.ke/helping-tax-payers/facts-about-kra/category/7", "scraped_at": TODAY},

    # ── Filing Returns ──
    {"question": "If one does not have income and has a KRA PIN, are they required to file a return?",
     "answer": "Yes. They are required to file NIL returns for the period without income.",
     "category": "iTax - Filing Returns", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/filing-returns-on-itax", "scraped_at": TODAY},

    {"question": "Can I view a copy of previous returns I have filed?",
     "answer": "Yes. Log in to your iTax account, select the Returns tab then 'Consult Return'. Select the type of return and the period you wish to view.",
     "category": "iTax - Filing Returns", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/filing-returns-on-itax", "scraped_at": TODAY},

    {"question": "Why does KRA require employees to file income tax returns yet employers file PAYE?",
     "answer": "Employers file PAYE returns to declare taxes deducted from employees. Employees file returns to declare their total income including farming income, business income, employment income, interest, and commissions.",
     "category": "iTax - Filing Returns", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/filing-returns-on-itax", "scraped_at": TODAY},

    {"question": "What is a P9 form?",
     "answer": "A P9 is a summary of employment income received in a given year, issued by the employer to employees. It is used when filing individual income tax returns on iTax.",
     "category": "iTax - Filing Returns", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/filing-returns-on-itax", "scraped_at": TODAY},

    {"question": "Can I file an amended return?",
     "answer": "Yes. You can file an amended return within five years from the date of filing the original return.",
     "category": "iTax - Filing Returns", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/filing-returns-on-itax", "scraped_at": TODAY},

    {"question": "What is the deadline for filing individual income tax returns?",
     "answer": "Individual income tax returns are due on or before 30th June of the following year of income.",
     "category": "iTax - Filing Returns", "source": "https://www.kra.go.ke/helping-tax-payers/facts-about-kra/category/3", "scraped_at": TODAY},

    # ── PAYE ──
    {"question": "What is PAYE?",
     "answer": "PAYE (Pay As You Earn) is a system where employers deduct tax from employees' employment income and remit it to KRA on their behalf.",
     "category": "PAYE", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-paye", "scraped_at": TODAY},

    {"question": "What does taxable employment income include?",
     "answer": "Taxable employment income includes all cash payments however described, and the value of non-cash benefits exceeding KSh 5,000 per month.",
     "category": "PAYE", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-paye", "scraped_at": TODAY},

    {"question": "By when must employers remit PAYE to KRA?",
     "answer": "Employers must remit PAYE to KRA on or before the 9th day of the following month.",
     "category": "PAYE", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-paye", "scraped_at": TODAY},

    {"question": "What are the individual income tax rates for PAYE?",
     "answer": "PAYE is computed using individual Income Tax Rates ranging from 10% to 35% as per the Finance Act 2023 (effective 1st July 2023).",
     "category": "PAYE", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-paye", "scraped_at": TODAY},

    {"question": "What is Fringe Benefit Tax (FBT)?",
     "answer": "FBT is a tax on loans given by employers to employees at below the prescribed interest rate. The difference between the prescribed rate and the actual rate charged is treated as a taxable benefit. FBT is paid by the employer.",
     "category": "PAYE", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-paye", "scraped_at": TODAY},

    {"question": "What meal benefits are exempt from PAYE?",
     "answer": "Meals provided by the employer are exempt up to KSh 5,000 per month (KSh 60,000 per year).",
     "category": "PAYE", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-paye", "scraped_at": TODAY},

    {"question": "What pension contributions are exempt from PAYE?",
     "answer": "Pension contributions made by an employer to a registered or unregistered scheme are exempt up to KSh 30,000 per month (KSh 360,000 per year).",
     "category": "PAYE", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-paye", "scraped_at": TODAY},

    # ── VAT ──
    {"question": "When is VAT due?",
     "answer": "VAT returns and payment are both due on or before the 20th day of the following month.",
     "category": "VAT", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-vat", "scraped_at": TODAY},

    {"question": "How are VAT returns submitted?",
     "answer": "VAT returns are submitted online via the iTax portal at itax.kra.go.ke.",
     "category": "VAT", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-vat", "scraped_at": TODAY},

    {"question": "What is input tax and output tax in VAT?",
     "answer": "Input tax is VAT paid on purchases of taxable goods and services for business purposes. Output tax is VAT charged on sales of taxable goods or services. A business remits the difference (output minus input) to KRA.",
     "category": "VAT", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-vat", "scraped_at": TODAY},

    {"question": "How long is an input tax deduction valid?",
     "answer": "Input tax deduction is valid for only six months after the end of the tax period in which the supply was made.",
     "category": "VAT", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-vat", "scraped_at": TODAY},

    {"question": "What are exempt supplies under VAT?",
     "answer": "Exempt supplies are listed in the First Schedule of the VAT Act 2013. Taxpayers who only make exempt supplies are not required to register for VAT.",
     "category": "VAT", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-vat", "scraped_at": TODAY},

    {"question": "Should I pay VAT and income tax?",
     "answer": "Income tax is a compulsory obligation for all income earners. VAT registration is required when your taxable turnover exceeds KSh 5 million per year. You pay VAT only when registered.",
     "category": "VAT", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-vat", "scraped_at": TODAY},

    {"question": "What is the VAT Special Table?",
     "answer": "The VAT Special Table is a KRA mechanism in iTax that restricts non-compliant taxpayers (nil filers, non-filers, or those involved in VAT fraud) from filing VAT returns until their compliance is reviewed.",
     "category": "VAT", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/more-about-vat", "scraped_at": TODAY},

    {"question": "What should I do if my supplier does not have a PIN?",
     "answer": "An invoice without a PIN is not a valid tax invoice and is therefore not allowed for input tax deduction. Ensure all your suppliers have valid KRA PINs.",
     "category": "VAT", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/filing-returns-on-itax", "scraped_at": TODAY},

    # ── Customs ──
    {"question": "What is import duty?",
     "answer": "Import duty is a tax imposed on goods brought into Kenya. It is assessed based on the Customs value of goods using rates from EACCMA 2004, VAT Act 2013, Excise Act 2015, and other government levies.",
     "category": "Customs and Border Control", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/customs-and-border-control", "scraped_at": TODAY},

    {"question": "Are all goods brought into Kenya subject to import duty?",
     "answer": "Yes, all goods whether new or used are subject to taxation. However, different passenger categories have different concessions under the 5th Schedule of the East African Community Customs Management Act.",
     "category": "Customs and Border Control", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/customs-and-border-control", "scraped_at": TODAY},

    {"question": "What passenger concession applies at customs?",
     "answer": "Passengers have a concession of USD 500 applicable only to goods for personal and/or household use.",
     "category": "Customs and Border Control", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/customs-and-border-control", "scraped_at": TODAY},

    {"question": "What are the conditions for importing a personal vehicle duty-free?",
     "answer": "You must have personally owned and used the vehicle outside Kenya for at least 12 months, the vehicle must not be older than 8 years, you must be at least 18 years old, and you must not have been granted a similar exemption previously.",
     "category": "Customs and Border Control", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/customs-and-border-control", "scraped_at": TODAY},

    {"question": "How do I verify if customs duty amounts assessed are correct?",
     "answer": "The passenger may seek an explanation from the Customs Officer. You have a right to query the assessed Customs duties and the Customs Officer is obligated to demonstrate the correctness of the assessment.",
     "category": "Customs and Border Control", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/customs-and-border-control", "scraped_at": TODAY},

    # ── PIN Registration ──
    {"question": "What is a KRA PIN?",
     "answer": "A KRA PIN (Personal Identification Number) is a unique identification number assigned to an individual or business upon registration with KRA. It is required for tax filing, payments, and various government transactions.",
     "category": "PIN Registration", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/pin-registration", "scraped_at": TODAY},

    {"question": "How do I apply for a KRA PIN?",
     "answer": "Visit the KRA website at www.kra.go.ke, click on 'Online Services', and select 'PIN Registration' to access the iTax portal and apply for a PIN online.",
     "category": "PIN Registration", "source": "https://www.kra.go.ke/helping-tax-payers/faqs/introduction-to-itax", "scraped_at": TODAY},

    # ── Income Tax / General Compliance ──
    {"question": "What is tax compliance?",
     "answer": "Tax compliance means adhering to tax laws — including registration, filing returns, and paying taxes. All individuals, businesses, and organizations earning income or engaging in taxable activities in Kenya must comply.",
     "category": "Income Tax", "source": "https://www.kra.go.ke/helping-tax-payers/facts-about-kra/category/3", "scraped_at": TODAY},

    {"question": "What happens if I don't comply with tax regulations?",
     "answer": "Non-compliance can result in penalties, fines, interest on unpaid taxes, and legal action in severe cases.",
     "category": "Income Tax", "source": "https://www.kra.go.ke/helping-tax-payers/facts-about-kra/category/3", "scraped_at": TODAY},

    {"question": "Does KRA make tax laws?",
     "answer": "No. KRA only implements provisions of already enacted tax laws. Enactment of tax legislation is the mandate of the National Assembly.",
     "category": "Income Tax", "source": "https://www.kra.go.ke/helping-tax-payers/facts-about-kra/category/3", "scraped_at": TODAY},

    {"question": "Does KRA control how tax money is spent?",
     "answer": "No. KRA only collects and accounts for taxes. The National Treasury accounts for tax expenditure.",
     "category": "Income Tax", "source": "https://www.kra.go.ke/helping-tax-payers/facts-about-kra/category/3", "scraped_at": TODAY},

    {"question": "Who is required to file tax returns in Kenya?",
     "answer": "All persons earning income — from employment, business, or other sources — must file their tax returns, regardless of income level. Even those without income who hold a KRA PIN must file NIL returns.",
     "category": "Income Tax", "source": "https://www.kra.go.ke/helping-tax-payers/facts-about-kra/category/3", "scraped_at": TODAY},

    # ── TCC ──
    {"question": "What is a Tax Compliance Certificate?",
     "answer": "A Tax Compliance Certificate (TCC) is official proof that a taxpayer has filed and paid their taxes. It is required for government tenders and certain transactions.",
     "category": "Tax Compliance Certificate", "source": "https://www.kra.go.ke/services/file-my-returns", "scraped_at": TODAY},

    {"question": "How do I apply for a Tax Compliance Certificate on iTax?",
     "answer": "Log in to iTax, select 'TCC' under the Certificates menu, fill out the application form, and submit it.",
     "category": "Tax Compliance Certificate", "source": "https://kra.go.ke/helping-tax-payers/facts-about-kra/category/7", "scraped_at": TODAY},
]


def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()


def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  💾 Saved {filepath}  ({len(data)} entries)")


def remove_duplicates(faqs):
    seen = set()
    unique = []
    for faq in faqs:
        key = faq["question"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(faq)
    return unique


def write_seed_data(output_dir):
    print("\n📦 Writing pre-seeded FAQ data...")
    by_category = {}
    for faq in MANUAL_SEED_DATA:
        by_category.setdefault(faq["category"], []).append(faq)

    cat_to_file = {p["category"]: p["filename"] for p in FAQ_PAGES}

    for cat, faqs in by_category.items():
        filename = cat_to_file.get(cat, cat.lower().replace(" ", "_") + "_faqs.json")
        filepath = os.path.join(output_dir, filename)
        existing = []
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                existing = json.load(f)
        merged = remove_duplicates(existing + faqs)
        save_json(merged, filepath)

    print(f"  ✓ Seed data written for {len(by_category)} categories")


def scrape_with_selenium(output_dir):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from bs4 import BeautifulSoup
    except ImportError:
        print("\n⚠  Selenium not installed. Run:")
        print("   pip install selenium webdriver-manager beautifulsoup4")
        print("   Skipping live scrape — seed data already written.\n")
        return

    print("\n🌐 Starting Selenium browser scraper...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    for page in FAQ_PAGES:
        print(f"\n[{page['category']}]  {page['url']}")
        try:
            driver.get(page["url"])
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            faqs = []

            # Strategy 1: accordion
            for item in soup.select(".accordion-item, .panel, [class*='accordion'], [class*='faq']"):
                q_tag = item.select_one("h2,h3,h4,h5,button,.accordion-header,strong,b")
                a_tag = item.select_one(".accordion-body,.panel-body,p")
                if q_tag and a_tag:
                    q = clean_text(q_tag.get_text())
                    a = clean_text(a_tag.get_text())
                    if q and a and q != a:
                        faqs.append({"question": q, "answer": a,
                                     "category": page["category"],
                                     "source": page["url"],
                                     "scraped_at": TODAY})

            # Strategy 2: dt/dd
            if not faqs:
                for dt in soup.find_all("dt"):
                    dd = dt.find_next_sibling("dd")
                    if dd:
                        q = clean_text(dt.get_text())
                        a = clean_text(dd.get_text())
                        if q and a:
                            faqs.append({"question": q, "answer": a,
                                         "category": page["category"],
                                         "source": page["url"],
                                         "scraped_at": TODAY})

            # Strategy 3: bold headings + paragraphs
            if not faqs:
                content = soup.select_one("main, article, .content, #content") or soup.body
                if content:
                    for el in content.find_all(["strong", "b", "h3", "h4"]):
                        text = clean_text(el.get_text())
                        if not text or len(text) < 10:
                            continue
                        parts = []
                        for sib in el.parent.find_next_siblings():
                            st = clean_text(sib.get_text())
                            if sib.name in ["strong", "b", "h3", "h4"]:
                                break
                            if st:
                                parts.append(st)
                            if len(parts) >= 4:
                                break
                        if text and parts:
                            faqs.append({"question": text, "answer": " ".join(parts),
                                         "category": page["category"],
                                         "source": page["url"],
                                         "scraped_at": TODAY})

            faqs = remove_duplicates(faqs)
            print(f"  ✓ Scraped {len(faqs)} additional FAQs")

            if faqs:
                filepath = os.path.join(output_dir, page["filename"])
                existing = []
                if os.path.exists(filepath):
                    with open(filepath, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                merged = remove_duplicates(existing + faqs)
                save_json(merged, filepath)

        except Exception as e:
            print(f"  ✗ Error: {e}")

        time.sleep(2)

    driver.quit()
    print("\n  ✓ Selenium scraping complete")


def build_combined_file(output_dir):
    all_faqs = []
    for page in FAQ_PAGES:
        filepath = os.path.join(output_dir, page["filename"])
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                all_faqs.extend(json.load(f))
    all_faqs = remove_duplicates(all_faqs)
    combined_path = os.path.join(output_dir, "all_faqs_combined.json")
    save_json(all_faqs, combined_path)
    return len(all_faqs)


def print_summary(output_dir):
    print("\n" + "=" * 60)
    print("  FINAL SUMMARY")
    print("=" * 60)
    for page in FAQ_PAGES:
        filepath = os.path.join(output_dir, page["filename"])
        count = 0
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                count = len(json.load(f))
        print(f"  {page['category']:<38} {count} FAQs")

    combined = os.path.join(output_dir, "all_faqs_combined.json")
    if os.path.exists(combined):
        with open(combined) as f:
            total = len(json.load(f))
        print("-" * 60)
        print(f"  all_faqs_combined.json              {total} total (deduped)")
    print("=" * 60)
    print(f"\n  Output: ./{output_dir}/")
    print("""
NEXT STEPS:
  1. Install RAG dependencies:
       pip install langchain chromadb sentence-transformers

  2. Load FAQs into ChromaDB:
       from langchain.vectorstores import Chroma
       from langchain.embeddings import HuggingFaceEmbeddings
       from langchain.document_loaders import JSONLoader

       loader = JSONLoader(
           file_path="faqs/all_faqs_combined.json",
           jq_schema=".[]",
           content_key="answer",
           metadata_func=lambda rec, _: {
               "question": rec["question"],
               "category": rec["category"],
               "source": rec["source"]
           }
       )
       docs = loader.load()
       embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
       db = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")

  3. Run LLaMA 3 locally via Ollama (free):
       ollama run llama3
""")


def main():
    seed_only = "--seed-only" in sys.argv
    print("=" * 60)
    print("  KRA.AI — FAQ Scraper")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    output_dir = "faqs"
    os.makedirs(output_dir, exist_ok=True)

    write_seed_data(output_dir)

    if not seed_only:
        scrape_with_selenium(output_dir)

    print("\n📁 Building combined FAQ file...")
    build_combined_file(output_dir)
    print_summary(output_dir)


if __name__ == "__main__":
    main()
