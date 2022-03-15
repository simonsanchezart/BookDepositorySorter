import argparse
from math import ceil
import bs4
import requests
import locale

class BookItem():
    def __init__(self, title, url, price):
        self.title = title
        self.url = url
        self.price = price

    def GetPrice(self):
        return self.price

    def __str__(self):
        return f"{self.title}: ${self.price}"

    def __repr__(self):
        return self.__str__()

parser = argparse.ArgumentParser(description="Crawls Book Depository and sorts by price")
parser.add_argument("url", metavar="url", type=str, help="Enter the category url")
parser.add_argument("-locale", metavar="locale", type=str, default="en", help="Enter 'es' if your decimal separator is ','. Default is 'en', where decimal separator is '.'")
parser.add_argument("-currency", metavar="currency", type=str, default="US$", help="Enter the currency that appears by default in BookDepository, default is 'US$'")
parser.add_argument("-pages", metavar="pages", type=int, default=10, help="Enter the amount of pages you want to search through")

args = parser.parse_args()
args.url += "?availability=1&searchSortBy=price_low_high"

locale.setlocale(locale.LC_ALL, args.locale)
locale_data = locale.localeconv()
decimal_pt = locale_data["mon_decimal_point"]
thousand_pt = locale_data["mon_thousands_sep"]

BASE_URL = "https://www.bookdepository.com"
ITEMS_PER_PAGE = 30
MAX_PAGES = 333

all_books = []
re = requests.get(args.url)
if re.status_code == 200:
    soup = bs4.BeautifulSoup(re.text, "html.parser")

    search_count = soup.find("span", {"class":"search-count"})
    search_count = search_count.text.replace('.', '')
    search_count = int(search_count)
    total_pages = ceil(search_count / ITEMS_PER_PAGE)
    total_pages = min(min(args.pages, total_pages), MAX_PAGES)

    for i in range(total_pages):
        current_url = args.url + f"&page={i+1}"
        current_req = requests.get(current_url)

        if re.status_code != 200:
            continue

        soup = bs4.BeautifulSoup(current_req.text, "html.parser")
        all_book_items = soup.find_all("div", {"class":"book-item"})
        try:
            for book_item in all_book_items:
                book_info = book_item.select_one(".item-info")

                book_name = book_info.select_one(".title")
                book_url = BASE_URL + book_name.find("a")['href']
                book_name = book_name.text.strip()

                book_author = book_info.select_one(".author")
                book_author = book_author.text.strip()

                complete_book_name = f"{book_name} - {book_author}"

                book_price = book_info.select_one(".price")
                # encoding and decoding removes weird unicode artifacts
                book_price = book_price.text.encode("ascii", "ignore").decode() 
                book_price = book_price.strip().replace(' ', '')
                book_price = book_price.replace(args.currency, '')
                book_price = book_price.split('\n')[0]
                book_price = locale.atof(book_price)

                book = BookItem(complete_book_name, book_url, book_price)
                all_books.append(book)
        except:
            continue

all_books.sort(key=BookItem.GetPrice)
for book in all_books:
    print(book)