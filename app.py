import anthropic
import streamlit as st
from bs4 import BeautifulSoup
import pymupdf
import urllib.request
import urllib.robotparser
import subprocess
import tempfile
import os
import base64
import re
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

st.set_page_config(
    page_title="Picky Eater - Vegetarian & Vegan Menu Finder",
    page_icon="🌿",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #c8dcc0;
    color: #1a2a14;
}

.main, .block-container {
    background-color: #c8dcc0;
    padding-top: 3rem;
    max-width: 720px;
}

h1, h2, h3 { font-family: 'DM Serif Display', serif; }

.pe-eyebrow {
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #3a5a2a;
    margin-bottom: 0.75rem;
    font-weight: 500;
}

.pe-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    color: #1a2a14;
    line-height: 1.08;
    margin-bottom: 0.75rem;
    letter-spacing: -0.02em;
}

.pe-subtitle {
    font-size: 0.95rem;
    color: #4a6a3a;
    font-weight: 300;
    line-height: 1.7;
    margin-bottom: 0;
}

.pe-divider {
    border: none;
    border-top: 1px solid #a8c8a0;
    margin: 2rem 0;
}

.stTextInput > div > div > input {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid #ddd8cc !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    padding: 8px 0 !important;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    color: #1a1a14;
    background-color: transparent !important;
}

.stTextInput > div > div > input:focus {
    border-bottom: 1px solid #5a7a4a !important;
    box-shadow: none !important;
}

.stTextInput > div {
    background-color: transparent !important;
}

.stButton > button {
    background: #3a5a2a;
    color: #f5f0e8;
    border: none;
    border-radius: 4px;
    padding: 0.65rem 2rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    transition: opacity 0.2s;
    width: auto;
}

.stButton > button:hover { opacity: 0.8; }

.url-row-num {
    font-size: 0.75rem;
    color: #b8b4a8;
    padding-top: 10px;
    font-weight: 500;
}

.restaurant-block {
    background: #fff;
    border: 1px solid #d4e8d4;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 1.25rem;
}

.restaurant-name {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    color: #1a1a14;
    margin-bottom: 0;
    display: inline;
}

.count-badge {
    display: inline-block;
    background: #c8dcc0;
    color: #2a4a1a;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 20px;
    margin-left: 10px;
    vertical-align: middle;
    position: relative;
    top: -3px;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.02em;
}

.source-badge {
    background: #e8e0cc;
    color: #6a4a10;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.65rem;
    font-weight: 500;
    margin-left: 8px;
}

.section-label {
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5a7a4a;
    margin-top: 1.25rem;
    margin-bottom: 0.4rem;
}

.dish-row {
    padding: 0.7rem 0;
    border-bottom: 1px solid #e8e2d8;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.dish-row:last-child { border-bottom: none; }

.dish-info { flex: 1; }
.dish-name { font-weight: 500; color: #1a1a14; font-size: 0.92rem; margin-bottom: 2px; }
.dish-reason { color: #8a8a78; font-size: 0.78rem; line-height: 1.4; }

.tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    white-space: nowrap;
    flex-shrink: 0;
    margin-top: 3px;
}

.tag-vegan { background: #2a4a14; color: #c8e0a0; }
.tag-vegetarian { background: #dcecd0; color: #2a5010; }
.tag-eggs { background: #f5e4c0; color: #7a4408; }
.tag-gelatin { background: #e8e4f8; color: #4a3a9a; }
.tag-possible { background: #e8e2d8; color: #5a5a4a; }
.tag-unsure { background: #ede8e0; color: #8a8a78; }

.blocked-card {
    padding: 1.25rem 0;
    border-bottom: 1px solid #e8e2d8;
}

.blocked-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    color: #1a1a14;
    margin-bottom: 0.4rem;
}

.blocked-msg { font-size: 0.85rem; color: #8a8a78; }
.blocked-link { color: #3a5a2a; text-decoration: none; }

.no-results-msg {
    font-size: 0.85rem;
    color: #8a8a78;
    font-style: italic;
    padding: 0.75rem 0;
}

.section-hint {
    font-size: 0.75rem;
    color: #a8a89a;
    font-style: italic;
    margin-top: 1rem;
    padding-top: 0.75rem;
    border-top: 1px solid #e8e2d8;
    line-height: 1.5;
}

.results-label {
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #5a7a4a;
    margin-bottom: 1.5rem;
    font-weight: 500;
}

.disclaimer {
    font-size: 0.72rem;
    color: #b8b4a8;
    text-align: center;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #ddd8cc;
    line-height: 1.6;
}

.stProgress > div > div > div > div {
    background: #3a5a2a !important;
    border-radius: 10px !important;
}

.stProgress > div > div {
    background-color: #ddd8cc !important;
    border-radius: 10px !important;
    height: 3px !important;
}

.loading-bar {
    background: #3a5a2a;
    border: none;
    border-radius: 6px;
    padding: 16px 22px;
    font-size: 0.88rem;
    color: #c8e0a0;
    font-weight: 500;
    letter-spacing: 0.01em;
}

/* Form container */
[data-testid="stForm"] {
    background: #ede8e0 !important;
    border: 1px solid #ddd8cc !important;
    border-radius: 8px !important;
    padding: 1.25rem !important;
}

/* Pills */
.stPills [data-baseweb="button-group"] button {
    font-size: 0.75rem !important;
    border-radius: 20px !important;
    border: 1px solid #ddd8cc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important;
    background: #ede8e0 !important;
    color: #5a5a4a !important;
}

.stPills [data-baseweb="button-group"] button[aria-pressed="true"] {
    background: #3a5a2a !important;
    color: #f5f0e8 !important;
    border-color: #3a5a2a !important;
}
</style>
""", unsafe_allow_html=True)

PROMPT = """Here is a restaurant menu:

{content}

You are a vegetarian food expert. A vegetarian friend is coming to dinner and needs to know what they can eat.

Return ONLY the vegetarian and vegan dishes in this exact format and nothing else:

SECTION: [section name]
DISH: [dish name] | [VEGAN SAFE or VEGETARIAN or CONTAINS EGGS or CONTAINS GELATIN or POSSIBLE VEGETARIAN or UNSURE] | [one line reason]

MOST IMPORTANT RULE: Always read the full description before categorizing. If the description mentions any fish, meat or seafood - even if the dish name sounds vegetarian - exclude it entirely. The description overrides the dish name.

GOLDEN RULE: Use your full food knowledge across all languages. If a dish contains or likely contains any meat, fish, seafood or poultry - leave it out completely. Do not mention it. Do not mark it UNSURE. Just exclude it silently.

LANGUAGE RULE: Menus may be in any language including Thai, Italian, French, Spanish, Japanese etc.
- "Pla" in Thai means fish - any dish with pla in the name contains fish - exclude it
- "Moo" in Thai means pork - exclude it
- "Gai" in Thai means chicken - exclude it
- "Nua" in Thai means beef - exclude it
- Italian: "polpo" is octopus, "tonno" is tuna, "acciughe" is anchovies, "prosciutto" is ham - exclude them
- French: "canard" is duck, "saumon" is salmon, "thon" is tuna, "poulet" is chicken, "boeuf" is beef, "veau" is veal, "agneau" is lamb, "porc" is pork, "lapin" is rabbit, "lardons" are bacon bits, "jambon" is ham, "andouille" is sausage, "boudin" is blood sausage, "moules" are mussels, "crevettes" are shrimp, "homard" is lobster, "crabe" is crab, "huitres" are oysters, "Saint-Jacques" or "coquilles" are scallops, "foie" is liver - exclude all of these
- French salads often contain lardons (bacon) even if not in the name - mark as UNSURE if salad description is unclear
- Spanish: "jamon" is ham, "cerdo" is pork, "pollo" is chicken, "ternera" is veal, "cordero" is lamb, "atun" is tuna, "gambas" are shrimp, "pulpo" is octopus, "chorizo" is pork sausage, "butifarra" is sausage, "morcilla" is blood sausage, "anchoas" are anchovies - exclude all of these
- When in doubt about a foreign language dish name, mark as POSSIBLE VEGETARIAN rather than VEGETARIAN

UNSURE is ONLY for dishes where you have absolutely zero information about ingredients.

POSSIBLE VEGETARIAN is ONLY for dishes where the ingredients are genuinely ambiguous — not for dishes where the exclusion is obvious. If you know the dish contains meat, fish, or seafood, exclude it silently. Do not use POSSIBLE VEGETARIAN as a soft exclusion.

CUISINE RULE: For Thai, Vietnamese, and Chinese dishes, fish sauce and oyster sauce are common base ingredients even when not listed. Unless the dish is explicitly marked vegetarian or ingredients are confirmed clean, label as POSSIBLE VEGETARIAN rather than VEGETARIAN, and note "may contain fish sauce or oyster sauce" in the reason.

Key exclusions - exclude these silently:
- ALL Caesar salads contain anchovies - exclude every Caesar salad
- Calamari is squid - exclude it
- Ahi, Poke, Ahi Poke contains tuna - exclude it
- Lox is smoked salmon - exclude it
- Sweetbreads are organ meat - exclude them
- Escargot and snails are animals - exclude them
- Polpette means meatballs - exclude them
- Tom Kha with chicken - exclude it
- Pad See Ew and Pad See You contain fish sauce - exclude them
- Pad Thai traditionally contains fish sauce - exclude it
- Any dish with bacon anywhere in the description - exclude it
- Meatballs always contain meat - exclude them
- Caviar and fish roe are fish products - exclude them entirely
- Any dish containing jamon serrano, jamon iberico, or any cured ham - exclude it
- Mussels, clams, oysters, scallops are shellfish - exclude them
- Shrimp, lobster, crab are seafood - exclude them

Egg and dairy rules:
- Any dish with egg or eggs as an ingredient cannot be VEGAN SAFE - mark as CONTAINS EGGS
- Eggs are never vegan regardless of cooking method or context
- CRITICAL: "Eggplant" and "aubergine" are vegetables - they contain NO eggs. Never mark eggplant or aubergine as CONTAINS EGGS.
- Aioli contains egg - any dish with aioli cannot be VEGAN SAFE, mark as VEGETARIAN or CONTAINS EGGS

BAKED GOODS AND DESSERT RULE:
The following categories almost always contain eggs unless explicitly stated otherwise. Mark as CONTAINS EGGS by default unless the description explicitly confirms egg-free or vegan:
- Cakes (carrot cake, chocolate cake, birthday cake, layer cake, cheesecake, etc.)
- Cookies and biscuits
- Brownies
- Custards, puddings, and crème brûlée
- Pies with custard or cream fillings (banana cream pie, key lime pie, etc.)
- Pastries, croissants, and brioche
- Waffles, pancakes, and crepes
- Soufflés and mousses
Only mark these as VEGETARIAN if the description explicitly confirms no eggs (e.g., "vegan", "egg-free", or lists only non-egg ingredients).

VEGAN SAFE rule - STRICT:
- Only mark a dish VEGAN SAFE if the description explicitly lists ingredients that confirm it is vegan (e.g. "roasted vegetables, olive oil, sea salt")
- If ingredients are not listed or are ambiguous, mark as VEGETARIAN instead
- Do NOT assume vegan based on the absence of animal products in the description

Other rules:
1. Do not use words like Remove, Skip, Excluded, Cannot anywhere in output
2. Do not include beverages, cocktails, wines or drinks
3. If a section has nothing suitable write: SECTION: [name] then EMPTY on the next line
4. Panna cotta contains gelatin - mark as VEGETARIAN + CONTAINS GELATIN
5. French onion soup - mark as UNSURE only if no broth type is mentioned"""

VISION_PROMPT = """This is an image of a restaurant menu.

You are a vegetarian food expert. A vegetarian friend is coming to dinner and needs to know what they can eat.

Return ONLY the vegetarian and vegan dishes in this exact format and nothing else:

SECTION: [section name]
DISH: [dish name] | [VEGAN SAFE or VEGETARIAN or CONTAINS EGGS or CONTAINS GELATIN or POSSIBLE VEGETARIAN or UNSURE] | [one line reason]

MOST IMPORTANT RULE: Always read the full description before categorizing. If the description mentions any fish, meat or seafood - exclude it entirely.

LANGUAGE RULE: Menus may be in any language.
- "Pla" in Thai means fish - exclude any dish with pla in the name
- "Moo" in Thai means pork - exclude it
- "Gai" in Thai means chicken - exclude it
- Italian: "polpo" is octopus, "tonno" is tuna - exclude them
- French: "canard" is duck, "saumon" is salmon, "thon" is tuna, "poulet" is chicken, "boeuf" is beef, "veau" is veal, "agneau" is lamb, "lardons" are bacon bits, "jambon" is ham, "moules" are mussels, "crevettes" are shrimp, "homard" is lobster, "huitres" are oysters - exclude all of these
- When in doubt about a foreign language dish, mark as POSSIBLE VEGETARIAN

GOLDEN RULE: Use your full food knowledge. If a dish contains any meat, fish, seafood or poultry - leave it out completely.

POSSIBLE VEGETARIAN is ONLY for genuinely ambiguous cases — not for obvious exclusions.

CUISINE RULE: For Thai, Vietnamese, and Chinese dishes, label as POSSIBLE VEGETARIAN unless explicitly confirmed vegetarian, and note "may contain fish sauce or oyster sauce."

Egg rules:
- Any dish with egg or eggs as an ingredient cannot be VEGAN SAFE - mark as CONTAINS EGGS
- Eggs are never vegan regardless of context
- CRITICAL: "Eggplant" and "aubergine" are vegetables - they contain NO eggs. Never mark eggplant or aubergine as CONTAINS EGGS.

Other rules:
1. Do not use words like Remove, Skip, Excluded anywhere
2. Do not include beverages, cocktails, wines or drinks
3. If a section has nothing suitable write: SECTION: [name] then EMPTY on the next line"""

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
results_lock = threading.Lock()

MEAL_PERIODS = ["brunch", "lunch", "dinner", "breakfast", "happy hour", "late night", "supper"]
NAV_KEYWORDS = ["about", "reservations", "reserve", "contact", "gift", "jobs", "careers", "privacy", "press", "party", "catering", "order", "shop", "faq", "accessibility", "skip", "main-content", "drinks", "cocktail"]

FILTER_OPTIONS = {
    "Vegan Safe": "VEGAN SAFE",
    "Vegetarian": "VEGETARIAN",
    "Contains Eggs": "CONTAINS EGGS",
    "Contains Gelatin": "CONTAINS GELATIN",
    "Possibly Vegetarian": "POSSIBLE VEGETARIAN",
    "Unsure": "UNSURE",
}

def check_robots(url):
    try:
        parsed = urlparse(url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(root + "/robots.txt")
        rp.read()
        return rp.can_fetch("*", url)
    except:
        return True

def fetch_pdf(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(urllib.request.urlopen(req).read())
            tmp_path = tmp.name
        doc = pymupdf.open(tmp_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        os.unlink(tmp_path)
        return text
    except urllib.error.HTTPError as e:
        if e.code in [403, 401, 429]:
            raise Exception(f"PDF_BLOCKED:{e.code}")
        raise

def fetch_html_content(url):
    script = (
        "from playwright.sync_api import sync_playwright\n"
        "from bs4 import BeautifulSoup\n"
        "import sys\n"
        "with sync_playwright() as p:\n"
        "    browser = p.chromium.launch(headless=True)\n"
        "    page = browser.new_page()\n"
        "    page.goto('" + url + "', wait_until='domcontentloaded', timeout=15000)\n"
        "    page.wait_for_timeout(5000)\n"
        "    content = page.content()\n"
        "    browser.close()\n"
        "soup = BeautifulSoup(content, 'html.parser')\n"
        "for tag in soup(['script', 'style', 'head']):\n"
        "    tag.decompose()\n"
        "sys.stdout.buffer.write(soup.get_text(separator='\\n', strip=True).encode('utf-8'))\n"
    )
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True,
        timeout=30,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}
    )
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8", errors="replace"))
    return result.stdout.decode("utf-8", errors="replace")

def fetch_html_raw(url):
    script = (
        "from playwright.sync_api import sync_playwright\n"
        "import sys\n"
        "with sync_playwright() as p:\n"
        "    browser = p.chromium.launch(headless=True)\n"
        "    page = browser.new_page()\n"
        "    page.goto('" + url + "', wait_until='domcontentloaded', timeout=15000)\n"
        "    page.wait_for_timeout(5000)\n"
        "    content = page.content()\n"
        "    browser.close()\n"
        "sys.stdout.buffer.write(content.encode('utf-8'))\n"
    )
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True,
        timeout=30,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}
    )
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8", errors="replace"))
    return result.stdout.decode("utf-8", errors="replace")

def find_meal_period_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc
    found = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.netloc != base_domain:
            continue
        if full_url in seen or full_url == base_url:
            continue
        label_text = a.get_text(strip=True).lower()
        if any(nav in label_text for nav in NAV_KEYWORDS):
            continue
        if any(meal in label_text for meal in MEAL_PERIODS):
            seen.add(full_url)
            found.append((full_url, a.get_text(strip=True)))
    return found[:4]

def fetch_image_and_analyze(img_url):
    req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
    img_data = urllib.request.urlopen(req).read()
    b64 = base64.standard_b64encode(img_data).decode("utf-8")
    ext = img_url.split(".")[-1].split("?")[0].lower()
    media_type = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                {"type": "text", "text": VISION_PROMPT}
            ]
        }]
    )
    return message.content[0].text

def find_menu_images(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src:
            continue
        full_url = urljoin(base_url, src)
        lower = full_url.lower()
        if any(kw in lower for kw in ["menu", "food", "lunch", "dinner", "brunch"]):
            if any(ext in lower for ext in [".jpg", ".jpeg", ".png"]):
                images.append(full_url)
    return images[:4]

def analyze_menu_text(content):
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": PROMPT.format(content=content)}]
    )
    return message.content[0].text

def extract_name_from_url(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        name = domain.split(".")[0]
        return name.replace("-", " ").replace("_", " ").title()
    except:
        return "Restaurant"

def process_restaurant(index, url):
    base_name = extract_name_from_url(url)
    try:
        if url.endswith(".pdf"):
            parsed = urlparse(url)
            root = f"{parsed.scheme}://{parsed.netloc}"
            if not check_robots(root):
                return [(index, 0, base_name, "BLOCKED", [], False)]
            try:
                content = fetch_pdf(url)
                result = analyze_menu_text(content)
                return [(index, 0, base_name, "DONE", parse_result(result), False)]
            except Exception as e:
                if "PDF_BLOCKED" in str(e):
                    return [(index, 0, base_name, "SERVER_BLOCKED", [], False)]
                raise

        if not check_robots(url):
            return [(index, 0, base_name, "BLOCKED", [], False)]

        raw_html = fetch_html_raw(url)
        meal_links = find_meal_period_links(raw_html, url)

        if meal_links:
            results = []
            for sub_i, (sub_url, sub_label) in enumerate(meal_links):
                try:
                    content = fetch_html_content(sub_url)
                    if len(content.strip()) < 300:
                        continue
                    card_name = f"{base_name} — {sub_label.title()}"
                    result = analyze_menu_text(content)
                    dishes = parse_result(result)
                    results.append((index, sub_i, card_name, "DONE", dishes, False))
                except:
                    continue
            if results:
                return results

        soup = BeautifulSoup(raw_html, "html.parser")
        for tag in soup(["script", "style", "head"]):
            tag.decompose()
        text_content = soup.get_text(separator="\n", strip=True)

        if len(text_content.strip()) < 500:
            menu_images = find_menu_images(raw_html, url)
            if menu_images:
                all_dishes = []
                for img_url in menu_images:
                    try:
                        result = fetch_image_and_analyze(img_url)
                        all_dishes.extend(parse_result(result))
                    except:
                        continue
                if all_dishes:
                    return [(index, 0, base_name, "VISION", all_dishes, False)]

        result = analyze_menu_text(text_content)
        return [(index, 0, base_name, "DONE", parse_result(result), True)]

    except Exception as e:
        return [(index, 0, base_name, "ERROR", str(e), False)]

def parse_result(text):
    dishes = []
    current_section = "Menu"
    bad_reason_words = [
        "excluded", "not vegetarian", "fish sauce",
        "veal", "contains beef", "contains pork", "contains lamb",
        "contains chicken", "mackerel", "branzino", "catfish", "petrale",
        "sweetbread", "organ", "sole fillet", "contains shrimp",
        "contains bacon", "contains tuna", "contains salmon",
        "contains crab", "contains lobster", "anchov",
        " - exclude", "exclude it"
    ]
    bad_dish_names = [
        "tuna", "blt", "salmon", "shrimp", "lobster", "crab", "bacon",
        "chicken", "beef", "pork", "lamb", "calamari", "anchov", "lox",
        "ahi", "poke", "duck egg", "duck", "prosciutto", "pancetta",
        "guanciale", "nduja", "mortadella", "salami", "chorizo",
        "meatball", "polpette", "pad see ew", "pad see you", "pad thai",
        "tom kha", "sweetbread", "mackerel", "branzino", "catfish",
        "petrale", "miang pla", "khao kluk", "gaeng som pla",
        "escargot", "snail", "mussel", "clam", "oyster", "scallop"
    ]
    for line in text.strip().split("\n"):
        line = line.strip()
        if line.startswith("SECTION:"):
            current_section = line.replace("SECTION:", "").strip()
        elif line == "EMPTY":
            continue
        elif line.startswith("DISH:"):
            parts = line.replace("DISH:", "").strip().split("|")
            if len(parts) >= 2:
                dish_name = parts[0].strip()
                category = parts[1].strip() if len(parts) > 1 else "UNSURE"
                reason = parts[2].strip() if len(parts) > 2 else ""
                if any(bad in category.lower() for bad in ["excluded", "not vegetarian", "contains meat", "contains fish"]):
                    continue
                if any(bad in reason.lower() for bad in bad_reason_words):
                    continue
                if any(bad in dish_name.lower() for bad in bad_dish_names):
                    continue
                if "vegan" in category.lower() and "egg" in reason.lower():
                    category = "CONTAINS EGGS"
                # Safety net: eggplant/aubergine are vegetables, never contain eggs
                if any(v in dish_name.lower() for v in ["eggplant", "aubergine"]):
                    if category == "CONTAINS EGGS":
                        category = "VEGETARIAN"
                dishes.append({
                    "section": current_section,
                    "name": dish_name,
                    "category": category,
                    "reason": reason
                })
    return dishes

def get_tag_class(category):
    cat = category.upper()
    if "VEGAN" in cat:
        return "tag-vegan"
    if "CONTAINS EGGS" in cat:
        return "tag-eggs"
    if "CONTAINS GELATIN" in cat:
        return "tag-gelatin"
    if "POSSIBLE" in cat:
        return "tag-possible"
    if "UNSURE" in cat:
        return "tag-unsure"
    return "tag-vegetarian"

def matches_filter(category, active_filters):
    if not active_filters:
        return True
    cat = category.upper()
    for f in active_filters:
        filter_val = FILTER_OPTIONS[f].upper()
        if filter_val in cat:
            return True
    return False

def render_card(name, status, data, show_hint=False, active_filters=None):
    if status == "BLOCKED":
        google_url = f"https://www.google.com/search?q={name.replace(' ', '+')}+menu"
        st.markdown(f"""
        <div class="blocked-card">
            <div class="blocked-title">{name}</div>
            <div class="blocked-msg">This site has asked not to be crawled. <a href="{google_url}" target="_blank" class="blocked-link">Search their menu on Google →</a></div>
        </div>""", unsafe_allow_html=True)
    elif status == "SERVER_BLOCKED":
        google_url = f"https://www.google.com/search?q={name.replace(' ', '+')}+menu"
        st.markdown(f"""
        <div class="blocked-card">
            <div class="blocked-title">{name}</div>
            <div class="blocked-msg">This site is blocking automated access. <a href="{google_url}" target="_blank" class="blocked-link">Search their menu on Google →</a></div>
        </div>""", unsafe_allow_html=True)
    elif status == "ERROR":
        st.markdown(f"""
        <div class="blocked-card">
            <div class="blocked-title">{name}</div>
            <div class="blocked-msg" style="color:#c45a5a">{data}</div>
        </div>""", unsafe_allow_html=True)
    else:
        dishes = data
        if active_filters:
            dishes = [d for d in dishes if matches_filter(d["category"], active_filters)]
        else:
            dishes = [d for d in dishes if "UNSURE" not in d["category"].upper()]

        count = len(dishes)
        sections = {}
        for d in dishes:
            sections.setdefault(d["section"], []).append(d)

        source_badge = '<span class="source-badge">via image</span>' if status == "VISION" else ""
        card_html = f'<div class="restaurant-block"><div style="margin-bottom:1rem; border-bottom:1px solid #d4e8d4; padding-bottom:0.75rem;"><span class="restaurant-name">{name}</span><span class="count-badge">{count} options</span>{source_badge}</div>'

        if not dishes and active_filters:
            card_html += '<div class="no-results-msg">No dishes match the selected filters.</div>'
        elif not dishes:
            card_html += '<div class="no-results-msg">Nothing made the cut at this one.</div>'
        else:
            for section, section_dishes in sections.items():
                card_html += f'<div class="section-label">{section}</div>'
                for d in section_dishes:
                    tag_class = get_tag_class(d["category"])
                    card_html += f"""
                    <div class="dish-row">
                        <div class="dish-info">
                            <div class="dish-name">{d["name"]}</div>
                            <div class="dish-reason">{d["reason"]}</div>
                        </div>
                        <span class="tag {tag_class}">{d["category"]}</span>
                    </div>"""

        if show_hint:
            card_html += '<div class="section-hint">Want to check a specific section like Dinner or Happy Hour? Paste that page\'s URL directly for more accurate results.</div>'

        card_html += "</div>"
        st.markdown(card_html, unsafe_allow_html=True)

# ── Header ──
st.markdown('<p class="pe-eyebrow">Picky Eater</p>', unsafe_allow_html=True)
st.markdown('<h1 class="pe-title">Find what you can eat<br><em>before</em> you commit.</h1>', unsafe_allow_html=True)
st.markdown('<p class="pe-subtitle">Paste up to 5 restaurant URLs. We scan the menu and surface vegetarian and vegan options — with honest caveats.</p>', unsafe_allow_html=True)
st.markdown('<hr class="pe-divider">', unsafe_allow_html=True)

# ── Input form ──
with st.form("restaurant_form"):
    st.markdown("<p style='font-size:0.82rem; color:#4a6a3a; margin-bottom:0.5rem;'>Paste up to 5 menu URLs below — restaurant websites, PDFs, or image menus.</p>", unsafe_allow_html=True)
    urls = []
    for i in range(5):
        c1, c2 = st.columns([0.05, 0.95])
        with c1:
            st.markdown(f"<div class='url-row-num'>{i+1}</div>", unsafe_allow_html=True)
        with c2:
            url = st.text_input(f"url_{i}", key=f"url_{i}", placeholder="", label_visibility="collapsed")
            urls.append(url)
    submitted = st.form_submit_button("Find Options")

if submitted:
    restaurant_urls = [u.strip() for u in urls if u.strip()]

    if not restaurant_urls:
        st.warning("Please enter at least one restaurant URL.")
    else:
        st.markdown('<hr class="pe-divider">', unsafe_allow_html=True)
        progress_placeholder = st.empty()
        progress_placeholder.markdown("""
        <div class="loading-bar">Scanning menus — this usually takes 20–40 seconds…</div>
        """, unsafe_allow_html=True)

        all_cards = []
        completed = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_restaurant, i, url): i for i, url in enumerate(restaurant_urls)}
            for future in as_completed(futures):
                card_results = future.result()
                with results_lock:
                    for card in card_results:
                        all_cards.append(card)
                completed += 1
                progress_placeholder.progress(completed / len(restaurant_urls))

        progress_placeholder.empty()
        st.session_state["all_cards"] = all_cards

if "all_cards" in st.session_state and st.session_state["all_cards"]:
    all_cards = st.session_state["all_cards"]
    all_cards.sort(key=lambda x: (x[0], x[1]))

    st.markdown('<hr class="pe-divider">', unsafe_allow_html=True)

    # Build dynamic filter options from actual categories present in results
    # Exclude UNSURE from filter options entirely
    present_categories = set()
    for card in all_cards:
        _, _, _, status, data, _ = card
        if status in ("DONE", "VISION") and isinstance(data, list):
            for dish in data:
                cat = dish.get("category", "").upper()
                if "UNSURE" not in cat:
                    present_categories.add(dish.get("category", ""))

    # Preserve display order
    CATEGORY_ORDER = ["VEGAN SAFE", "VEGETARIAN", "CONTAINS EGGS", "CONTAINS GELATIN", "POSSIBLE VEGETARIAN"]
    available_filters = [
        label for label, val in FILTER_OPTIONS.items()
        if val in present_categories and "UNSURE" not in val
    ]

    active_filters = []
    if available_filters:
        try:
            active_filters = st.pills(
                "Filter",
                options=available_filters,
                selection_mode="multi",
                label_visibility="collapsed"
            )
        except Exception:
            active_filters = st.multiselect(
                "Filter by category",
                options=available_filters,
                default=[],
                label_visibility="collapsed",
                placeholder="Filter by category"
            )

    total_restaurants = len(set(c[0] for c in all_cards))
    st.markdown(f'<div class="results-label">Results — {total_restaurants} restaurant{"s" if total_restaurants != 1 else ""}</div>', unsafe_allow_html=True)

    grouped = {}
    for card in all_cards:
        idx = card[0]
        if idx not in grouped:
            grouped[idx] = []
        grouped[idx].append(card)

    for idx in sorted(grouped.keys()):
        group = grouped[idx]
        for (_, _, name, status, data, show_hint) in group:
            render_card(name, status, data, show_hint, active_filters)

    st.markdown("""
    <div class="disclaimer">
        Results are AI-generated and may occasionally misclassify dishes.<br>
        Always verify with the restaurant for strict dietary requirements.
    </div>""", unsafe_allow_html=True)
