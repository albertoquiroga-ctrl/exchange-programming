import urllib.request
import re
import bs4

# this function take a hktvmall item webpage URL as input.
# and return the price
# please complete the function
#
# New Learning Point:
#   - The sample code below has "User-Agent" specified. That's for pretending it's a real browser
#


def fetch_product_html(url):
    """Download the product page and return it as text."""
    # HKTVmall rejects unknown bots, so we send a browser-like header.
    request = urllib.request.Request(
        url,
        data=None,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/107.0.0.0 Safari/537.36"
            )
        },
    )

    # Using a context manager keeps the network connection tidy.
    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_price_from_dom(html_text):
    """Look for the visible price element like <div class='price'>$ 61.00</div>."""
    soup = bs4.BeautifulSoup(html_text, "html.parser")

    # The price lives inside a <div class="price"> tag on most product pages.
    price_container = soup.select_one("div.price")
    if not price_container:
        return None

    # Strip extra words, remove thousands separators, and capture the number.
    price_text = price_container.get_text(strip=True)
    cleaned_price = price_text.replace(",", "")
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", cleaned_price)
    if not match:
        return None

    return float(match.group(1))


def extract_price_from_embedded_json(html_text):
    """Fallback: pull the BUY price from the JSON blob embedded in the HTML."""
    pattern = re.compile(
        r'"price"\s*:\s*\{'
        r'[^}]*"priceType"\s*:\s*"BUY"'
        r'[^}]*"value"\s*:\s*([0-9]+(?:\.[0-9]+)?)',
        re.DOTALL,
    )
    match = pattern.search(html_text)
    if not match:
        return None

    return float(match.group(1))


def get_item_price(url):
    """Co-ordinate the full flow: download, parse, and return the product price."""
    html_text = fetch_product_html(url)

    # Try the simple, human-facing price display first.
    price = extract_price_from_dom(html_text)
    if price is not None:
        return price

    # If the visible price is missing, try to read the machine data instead.
    price = extract_price_from_embedded_json(html_text)
    if price is not None:
        return price

    # If both approaches fail, make the error message explicit.
    raise ValueError("Unable to determine price from page")


item_urls = ["https://www.hktvmall.com/hktv/en/main/Virjoy/s/H1050001/Supermarket/Supermarket/Tissues%2C-Disposable-%26-Household-Products/Flushable-Toilet-Wet-Wipe/Full-Case-Luxury-Moist-Flushable-Tissue/p/H0888001_S_P10153967",
             "https://www.hktvmall.com/hktv/zh/main/Yummy-Bear/s/H0956006/%E8%B6%85%E7%B4%9A%E5%B7%BF%E5%A0%B4/%E8%B6%85%E7%B4%9A%E5%B8%82%E5%A0%B4/%E5%8D%B3%E9%A3%9F%E9%BA%B5-%E9%BA%B5-%E6%84%8F%E7%B2%89/%E6%9D%AF%E9%BA%B5/%E6%9D%AF%E9%BA%B5/%E5%85%83%E7%A5%96%E9%9B%9E%E6%B1%81%E6%B3%A1%E9%BA%B5425g-5%E5%8C%85%E8%A3%9D%E5%B9%B3%E8%A1%8C%E9%80%B2%E5%8F%A3%E4%B8%8D%E5%90%8C%E5%8C%85%E8%A3%9D%E9%9A%A8%E6%A9%9F%E5%87%BA/p/H0956006_S_LT10003711",
             "https://www.hktvmall.com/hktv/zh/main/%E7%BE%A9%E7%94%9F%E6%B4%8B%E8%A1%8C%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8/s/B0424001/%E8%B6%85%E7%B4%9A%E5%B7%BF%E5%A0%B4/%E8%B6%85%E7%B4%9A%E5%B8%82%E5%A0%B4/%E5%8D%B3%E9%A3%9F%E9%BA%B5-%E9%BA%B5-%E6%84%8F%E7%B2%89/%E6%84%8F%E7%B2%89-%E9%80%9A%E5%BF%83%E7%B2%89/%E6%84%8F%E7%B2%89/%E6%84%8F%E5%A4%A7%E5%88%A9-%E9%98%BF%E5%B8%83%E7%B4%A0-%E7%85%99%E8%82%89%E7%99%BD%E6%B1%81%E9%86%AC-270%E5%85%8B-/p/B0424001_S_8009452225384"]


for url in item_urls:
    print(get_item_price(url))
