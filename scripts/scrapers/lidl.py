import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# TODO: refactor, this is a mess; retrieve leaflet details, product and price extraction

LIDL_URL = "https://www.lidl.pl/c/nasze-gazetki/s10008614"

def extract_date_range(text):
    """Extracts the start and end dates from a string."""
    matches = re.findall(r"(\d{2}\.\d{2})", text)
    if len(matches) == 1:
        return matches[0], None
    elif len(matches) == 2:
        return matches[0], matches[1]
    return None, None

def is_current(start_str, end_str):
    """Check if the leaflet is currently active based on start and end dates."""
    today = datetime.today().date()
    start = datetime.strptime(start_str + f".{today.year}", "%d.%m.%Y").date()
    if end_str:
        end = datetime.strptime(end_str + f".{today.year}", "%d.%m.%Y").date()
        return start <= today <= end
    return start <= today

def get_active_leaflets():
    """Fetches active leaflets from Lidl's website."""
    res = requests.get(LIDL_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    flyers = soup.find_all("a", class_="flyer")

    active_leaflets = []

    for flyer in flyers:
        title_tag = flyer.select_one("h2.flyer__name")
        subtitle_tag = flyer.select_one("h4.flyer__title")
        link = flyer["href"]

        title = title_tag.get_text(strip=True) if title_tag else ""
        subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else ""

        start, end = extract_date_range(title)

        if start and is_current(start, end):
            active_leaflets.append({
                "title": title,
                "subtitle": subtitle,
                "link": link,
                "start": start,
                "end": end
            })

    return active_leaflets

def get_product_pages(leaflet_page_url):
    """Extracts product pages from a Lidl leaflet page."""
    resp = requests.get(leaflet_page_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    return [
        f"https://www.lidl.pl/{iframe['src']}"
        for iframe in soup.find_all("iframe", src=lambda s: 'layout=flyer' in s)
    ]

def extract_products(url):
    """Extract product information from a Lidl product page."""
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    
    product_names = [h1.get_text(strip=True) for h1 in soup.find_all("h1", class_="heading__title")]
    product_prices = [div.get_text(strip=True) for div in soup.find_all("div", class_="ods-price__value")]

    products = []
    for name, price in zip(product_names, product_prices):
        products.append({
            "name": name,
            "price": price
        })

    return products

if __name__ == "__main__":
    leaflets = get_active_leaflets()
    for l in leaflets:
        print(f"{l['subtitle']} ({l['title']}) → {l['link']}")

    product_pages = get_product_pages("https://www.lidl.pl/l/pl/gazetki/oferta-wazna-od-16-06-katalog-kw25/view/product/100390133/page/6")
    for page in product_pages:
        print(f"Extracting products from: {page}")
        products = extract_products(page)
        for product in products:
            print(f"{product['name']} - {product['price']}")