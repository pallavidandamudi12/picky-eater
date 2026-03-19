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
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #eef4ee;
}

.main, .block-container {
    background-color: #eef4ee;
    padding-top: 2rem;
}

h1, h2, h3 { font-family: 'DM Serif Display', serif; }

.hero-wrap {
    background: linear-gradient(135deg, #7a9e7e 0%, #5f836a 100%);
    border-radius: 20px;
    padding: 40px 40px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    text-align: center;
}

.hero-pattern {
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle, rgba(255,255,255,0.08) 1px, transparent 1px);
    background-size: 22px 22px;
    border-radius: 20px;
}

.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3rem;
    color: white;
    letter-spacing: -0.02em;
    margin-bottom: 6px;
    position: relative;
}

.hero-subtitle {
    font-size: 1rem;
    color: rgba(255,255,255,0.8);
    font-weight: 300;
    position: relative;
}

.stTextInput > div > div > input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    color: #2c2c2a;
}

.stTextInput > div > div > input:focus {
    border: none !important;
    box-shadow: none !important;
}

.stButton > button {
    background: linear-gradient(135deg, #7a9e7e 0%, #5f836a 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 500;
    width: 100%;
    letter-spacing: 0.02em;
    transition: opacity 0.2s;
}

.stButton > button:hover { opacity: 0.9; }

.restaurant-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    border: 1px solid #d4e8d4;
    min-height: 420px;
    margin-bottom: 16px;
}

.restaurant-card h3 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: #2c2c2a;
    border-bottom: 2px solid #7a9e7e;
    padding-bottom: 8px;
    margin-bottom: 10px;
}

.dish-row {
    padding: 7px 0;
    border-bottom: 1px solid #eef4ee;
}

.dish-name { font-weight: 500; color: #2c2c2a; font-size: 0.88rem; }
.dish-reason { color: #7a7a72; font-size: 0.78rem; margin-top: 2px; }

.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 500;
    margin-bottom: 3px;
}

.tag-vegan { background: #27500a; color: #eaf3de; }
.tag-vegetarian { background: #eef4e0; color: #4a6a1a; }
.tag-eggs { background: #fef9c3; color: #854d0e; }
.tag-gelatin { background: #f0eef8; color: #4a3a8a; }
.tag-possible { background: #e8f2f8; color: #1a4a6a; }
.tag-unsure { background: #f4f4f0; color: #5a5a52; }

.section-label {
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #7a9e7e;
    margin-top: 12px;
    margin-bottom: 4px;
}

.count-badge {
    background: #7a9e7e;
    color: white;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 500;
    margin-left: 8px;
}

.source-badge {
    background: #fdf3e0;
    color: #7a5a10;
    border-radius: 20px;
    padding: 2px 8px;
    font-size: 0.65rem;
    font-weight: 500;
    margin-left: 6px;
}

.section-hint {
    font-size: 0.76rem;
    color: #7a9e7e;
    font-style: italic;
    margin-top: 14px;
    padding-top: 10px;
    border-top: 1px solid #eef4ee;
    line-height: 1.5;
}

.no-results-msg {
    font-size: 0.85rem;
    color: #9a9a92;
    font-style: italic;
    padding: 12px 0;
}

.disclaimer {
    font-size: 0.75rem;
    color: #8ab48a;
    text-align: center;
    margin-top: 2rem;
    padding: 1rem;
    border-top: 1px solid #d4e8d4;
}

.results-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    color: #2c2c2a;
    margin-bottom: 16px;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #7a9e7e, #5f836a) !important;
    border-radius: 10px !important;
}

.stProgress > div > div {
    background-color: #d4e8d4 !important;
    border-radius: 10px !important;
    height: 6px !important;
}

.stMultiSelect [data-baseweb="tag"] {
    background-color: #f1efe8 !important;
    color: #2c2c2a !important;
    border-radius: 20px !important;
}

.stMultiSelect [data-baseweb="tag"] span[role="presentation"] {
    color: #2c2c2a !important;
}

.stMultiSelect [data-baseweb="select"] {
    background-color: white !important;
    border-color: #d4e8d4 !important;
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
- French: "canard" is duck, "saumon" is salmon, "thon" is tuna, "poulet" is chicken - exclude them
- When in doubt about a foreign language dish name, mark as POSSIBLE VEGETARIAN rather than VEGETARIAN

UNSURE is ONLY for dishes where you have absolutely zero information about ingredients.

Key exclusions - exclude these silently:
- ALL Caesar salads contain anchovies - exclude every Caesar salad
- Calamari is squid - exclude it
- Ahi, Poke, Ahi Poke contains tuna - exclude it
- Lox is smoked salmon - exclude it
- Sweetbreads are organ meat - exclude them
- Polpette means meatballs - exclude them
- Tom Kha with chicken - exclude it
- Pad See Ew and Pad See You contain fish sauce - exclude them
- Pad Thai traditionally contains fish sauce - exclude it
- Any dish with bacon anywhere in the description - exclude it
- Meatballs always contain meat - exclude them

Egg rules:
- Any dish with egg or eggs in the description cannot be VEGAN SAFE - mark as CONTAINS EGGS
- Eggs are never vegan regardless of cooking method or context

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
- French: "canard" is duck, "saumon" is salmon - exclude them
- When in doubt about a foreign language dish, mark as POSSIBLE VEGETARIAN

GOLDEN RULE: Use your full food knowledge. If a dish contains any meat, fish, seafood or poultry - leave it out completely.

Egg rules:
- Any dish with egg in the description cannot be VEGAN SAFE - mark as CONTAINS EGGS
- Eggs are never vegan regardless of context

Other rules:
1. Do not use words like Remove, Skip, Excluded anywhere
2. Do not include beverages, cocktails, wines or drinks
3. If a section has nothing suitable write: SECTION: [name] then EMPTY on the next line"""

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
results_lock = threading.Lock()

MEAL_PERIODS = ["brunch", "lunch", "dinner", "breakfast", "happy hour", "late night", "supper"]
NAV_KEYWORDS = ["about", "reservations", "reserve", "contact", "gift", "jobs", "careers", "privacy", "press", "party", "catering", "order", "shop", "faq", "accessibility", "skip", "main-content", "drinks", "cocktail"]

FILTER_OPTIONS = {
    "Vegan Safe": "VEGAN SAFE",
    "Vegetarian": "VEGETARIAN",
    "Contains Eggs": "CONTAINS EGGS",
    "Contains Gelatin": "CONTAINS GELATIN",
    "Possible Vegetarian": "POSSIBLE VEGETARIAN",
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
        ["py", "-c", script],
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
        ["py", "-c", script],
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
            content = fetch_pdf(url)
            result = analyze_menu_text(content)
            return [(index, 0, base_name, "DONE", parse_result(result), False)]

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
        "contains crab", "contains lobster", "anchov"
    ]
    bad_dish_names = [
        "tuna", "blt", "salmon", "shrimp", "lobster", "crab", "bacon",
        "chicken", "beef", "pork", "lamb", "calamari", "anchov", "lox",
        "ahi", "poke", "duck egg", "duck", "prosciutto", "pancetta",
        "guanciale", "nduja", "mortadella", "salami", "chorizo",
        "meatball", "polpette", "pad see ew", "pad see you", "pad thai",
        "tom kha", "sweetbread", "mackerel", "branzino", "catfish",
        "petrale", "miang pla", "khao kluk", "gaeng som pla"
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
        st.markdown(f"""
        <div class="restaurant-card">
            <h3>{name}</h3>
            <div class="dish-reason" style="margin-top:1rem">
                This restaurant does not permit AI processing.<br>
                Try searching for their menu on Google directly.
            </div>
        </div>""", unsafe_allow_html=True)
    elif status == "ERROR":
        st.markdown(f"""
        <div class="restaurant-card">
            <h3>{name}</h3>
            <div class="dish-reason" style="margin-top:1rem; color:#c45a5a">
                {data}
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        dishes = data
        if active_filters:
            dishes = [d for d in dishes if matches_filter(d["category"], active_filters)]

        count = len(dishes)
        sections = {}
        for d in dishes:
            sections.setdefault(d["section"], []).append(d)

        source_badge = '<span class="source-badge">via menu image</span>' if status == "VISION" else ""
        card_html = f'<div class="restaurant-card"><h3>{name} <span class="count-badge">{count} options</span>{source_badge}</h3>'

        if not dishes and active_filters:
            card_html += '<div class="no-results-msg">No dishes match the selected filters for this restaurant.</div>'
        else:
            for section, section_dishes in sections.items():
                card_html += f'<div class="section-label">{section}</div>'
                for d in section_dishes:
                    tag_class = get_tag_class(d["category"])
                    card_html += f"""
                    <div class="dish-row">
                        <span class="tag {tag_class}">{d["category"]}</span>
                        <div class="dish-name">{d["name"]}</div>
                        <div class="dish-reason">{d["reason"]}</div>
                    </div>"""

            if not dishes and not active_filters:
                card_html += '<div class="dish-reason" style="margin-top:1rem">No vegetarian or vegan options found.</div>'

        if show_hint:
            card_html += '<div class="section-hint">Want to check a specific section like Dinner or Happy Hour? Paste that page\'s URL directly for more accurate results.</div>'

        card_html += "</div>"
        st.markdown(card_html, unsafe_allow_html=True)

st.markdown("""
<div class="hero-wrap">
    <div class="hero-pattern"></div>
    <div class="hero-title">🌿 Picky Eater</div>
    <div class="hero-subtitle">Find vegetarian & vegan options across restaurants — before you commit to a reservation.</div>
</div>
""", unsafe_allow_html=True)

col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    with st.form("restaurant_form"):
        urls = []
        for i in range(5):
            c1, c2 = st.columns([0.05, 0.95])
            with c1:
                st.markdown(f"<div style='padding-top:8px; color:#a8c8a8; font-size:0.8rem; font-weight:500;'>{i+1}</div>", unsafe_allow_html=True)
            with c2:
                url = st.text_input(f"url_{i}", key=f"url_{i}", placeholder="Paste a menu URL here...", label_visibility="collapsed")
                urls.append(url)
        st.caption("Supports restaurant website URLs, PDF menus, and image-based menus. Results may vary by site.")
        submitted = st.form_submit_button("Find Options")

if submitted:
    restaurant_urls = [u.strip() for u in urls if u.strip()]

    if not restaurant_urls:
        st.warning("Please enter at least one restaurant URL.")
    else:
        st.markdown("---")
        progress_placeholder = st.empty()
        progress_placeholder.markdown("""
        <div style='background:white; border-radius:14px; padding:20px 24px;
        border:1px solid #d4e8d4; color:#7a9e7e; font-size:0.85rem;'>
            🌿 Scanning menus — this usually takes 20-40 seconds...
        </div>""", unsafe_allow_html=True)

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

    active_filters = st.multiselect(
        "Filter by category",
        options=list(FILTER_OPTIONS.keys()),
        default=[],
        max_selections=3,
        label_visibility="collapsed",
        placeholder="Filter by category — select up to 3"
    )

    st.markdown('<div class="results-title">Results</div>', unsafe_allow_html=True)

    grouped = {}
    for card in all_cards:
        idx = card[0]
        if idx not in grouped:
            grouped[idx] = []
        grouped[idx].append(card)

    for idx in sorted(grouped.keys()):
        group = grouped[idx]
        num = len(group)
        cols = st.columns(min(num, 4))
        for i, (_, _, name, status, data, show_hint) in enumerate(group):
            with cols[i % min(num, 4)]:
                render_card(name, status, data, show_hint, active_filters)

    st.markdown("""
    <div class="disclaimer">
        Results are AI-generated and may occasionally misclassify dishes.
        Always verify with the restaurant for strict dietary requirements.
    </div>""", unsafe_allow_html=True)
