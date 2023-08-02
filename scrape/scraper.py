# http://github.com/eraviart/drugs-harvesters


"""Crawl drugs pages from http://base-donnees-publique.medicaments.gouv.fr"""


import os
import shutil
import urllib.parse
from string import ascii_lowercase

import lxml.html
import requests


def scrape_data(url, save_directory):

    # Check if save_directory exists
    if os.path.exists(save_directory):
        shutil.rmtree(save_directory)
    os.makedirs(save_directory)

    # Start scraping
    drug_name_by_url_path = {}
    for letter in ascii_lowercase:

        url_letter = urllib.parse.urljoin(url, f"liste-medicaments-{letter}.php")
        print(f"Scraping url : {url_letter}")
        response = requests.get(
            url_letter
        )
        html_element = lxml.html.fromstring(response.content)
        a_element_list = html_element.xpath(
            '//table[@class="result"]//a[@class="standart"]'
        )

        if not a_element_list:
            break
        for a_element in a_element_list:

            title = a_element.text.strip()
            file_name = title.replace("/", "").replace(" ", "_")
            file_name += ".txt"

            try:
                med_page = requests.get(
                    urllib.parse.urljoin(url, a_element.get("href"))
                )
                med_element = lxml.html.fromstring(med_page.content)
                lien_rcp = med_element.xpath('//a[@id="lien_rcp"]/@href')[0]
                rcp_page = requests.get(urllib.parse.urljoin(url, lien_rcp))
                rcp_element = lxml.html.fromstring(rcp_page.content)
                text = rcp_element.xpath(
                    '//div[@id="textDocument"]/p//text()'
                )
                text = "\n".join(text)

                drug_name_by_url_path[a_element.get("href")] = a_element.text.strip()
                with open(os.path.join(save_path, file_name), "w", encoding="utf-8") as save_file:
                    save_file.write(text)

            except IndexError:
                pass


if __name__ == "__main__":
    url = "https://base-donnees-publique.medicaments.gouv.fr/"
    save_path = "../data/"
    scrape_data(url, save_path)