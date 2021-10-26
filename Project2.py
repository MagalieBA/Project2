#Import requests and BeautifulSoup
import requests
import re
import csv
from bs4 import BeautifulSoup

website_base_url = "https://books.toscrape.com/"

def book_extraction(link_book):        # FUNCTION TO EXTRACT FROM A BOOK PAGE
    #PARSER
    page = requests.get(link_book)
    soup = BeautifulSoup(page.content, 'html.parser')

    #BOOK EXTRACTION
    title = soup.h1.string #returns the title
    product_page_url  = page.url #returns the page url
    product_description = soup.find("div", id="product_description").findNext('p').string #returns the book description 
    product_information = soup.find("table", class_="table-striped")
    production_information_content = product_information.findAll("td")
    universal_product_code = production_information_content[0].string
    price_including_tax = production_information_content[2].string
    price_excluding_tax = production_information_content[3].string
    line_of_number_available = production_information_content[5].string
    number_available = ''.join(filter(str.isdigit,line_of_number_available))
    review_rating = soup.find("p", class_="star-rating").attrs["class"][1] #Extraire le nombre dans class après star-rating
    category = soup.find("ul", class_="breadcrumb").find_all("a")[-2].string #Extract the category
    image_tag = soup.find("img", alt=title).attrs["src"] #Extract the image url
    image_url = str(website_base_url) + str(image_tag[6:]) #Converts url link from relative to absolute 

    #Creating a dictionnary with the extracted informations of the book
    book_information = {
        "Page_url": product_page_url,
        "UPC": universal_product_code,
        "Title": title,
        "Price_with_tax": price_including_tax,
        "Price_without_taxout": price_excluding_tax,
        "Availabity": number_available,
        "Product_description": product_description,
        "Category": category,
        "Rating": review_rating,
        "Image": image_url,
    }
    return book_information

#EXTRACTING ALLS BOOKS IN A CATEGORY
def extract_books_url(input_category_url): 

    #PARSER
    category_page = requests.get(input_category_url)
    most_soup = BeautifulSoup(category_page.content, 'html.parser')

    #BROWSING ALL THE PAGE
    total_pages = most_soup.find("li", class_="current").string
    max_pages = int(total_pages.split()[-1]) + 1
    all_pages_url = [input_category_url,] # wrong link

    for i in range(2,max_pages) :
        next_page_url = str(input_category_url[:-11]) + str("page-") + str(i) + str(".html") #wrong link
        all_pages_url += next_page_url

    #EXTRACTING ALL THE BOOKS URLS
    for page in all_pages_url :
        #parser
        current_page = requests.get(page)
        book_soup = BeautifulSoup(current_page.content, 'html.parser')

        all_books_urls = []
        all_books = book_soup.find_all("article", class_="product_pod")

    #Creer mon fichier CSV
    with open ('BookInformations.csv','w',newline = '') as csvfile: # Example.csv gets created in the current working directory
        my_writer = csv.writer(csvfile, delimiter = ' ')
        for book in all_books:
            book_url_relative = book.find("h3").find("a").attrs["href"]
            book_url= str(category_url[:-11]) + str(book_url_relative[9:]) #converts relative link to absolute 
            all_books_urls.append(book_url)
            book_info = book_extraction(book_url)
            my_writer.writerows(book_info) #Test

#EXTRACTING ALL THE CATEGORY URLS
website = requests.get(website_base_url)
category_soup = BeautifulSoup(website.content, 'html.parser')

all_categories = category_soup.find("ul", class_="nav").find_all("a")
for category in all_categories:
    category_url_relative = category.attrs["href"]
    category_url= str(website_base_url) + str(category_url_relative) #converts relative link to absolute 
    extract_books_url(category_url)
