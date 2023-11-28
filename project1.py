import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# File path for the CSV files
csv_file_path_model = "project11.csv"
csv_file_path = "project12.csv"

# Initialize global variable for the CSV files
csv_file_model = open(csv_file_path_model, mode='w', newline='', encoding='utf-8')
csv_file = open(csv_file_path, mode='w', newline='', encoding='utf-8')

csv_writer_model = csv.writer(csv_file_model)
csv_writer = csv.writer(csv_file)

def write_to_csv_model(row):
    global csv_writer_model
    csv_writer_model.writerow(row)

def write_to_csv(row):
    global csv_writer
    csv_writer.writerow(row)

url = 'https://www.babbittsonline.com'

def getDetailOEMData(paramurl):
    try:
        with requests.Session() as session:
            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
            session.mount('https://', HTTPAdapter(max_retries=retries))

            response = session.get(paramurl)

        if response.status_code == 200:
            html_content = response.content
            soup = BeautifulSoup(html_content, 'lxml')
            
            span_tags = soup.select('li[itemprop="itemListElement"] span[itemprop="name"]')
            span_contents = [span_tag.get_text(strip=True) for span_tag in span_tags]

            h2_tag = soup.find('h2')
            h2_text = h2_tag.text
            span_contents.append(h2_text)

            partlistrows = soup.find_all('div', class_='partlistrow')

            for partlistrow in partlistrows:
                span_c0 = partlistrow.find('div', class_='c0').span.text
                span_c1a = partlistrow.find('div', class_='c1a').span.text

                spans_c1b = partlistrow.find('div', class_='c1b').find_all('span')
                span_texts_c1b = [span.text for span in spans_c1b]

                if len(span_texts_c1b) == 2:
                    span1, span2 = span_texts_c1b
                    all_span_contents = span_contents + [span_c0, span_c1a, span1, paramurl, "", span2]
                    write_to_csv(all_span_contents)

                    all_span_contents = span_contents + [span_c0, span_c1a, span2, paramurl, "", span1]
                    write_to_csv(all_span_contents)
                else:
                    all_span_contents = span_contents + [span_c0, span_c1a, span_texts_c1b[0], paramurl, "", ""]
                    write_to_csv(all_span_contents)
    except Exception as e:
        print(f"Error in getDetailOEMData: {e}")

def getOEMData(paramurl):
    try:
        with requests.Session() as session:
            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
            session.mount('https://', HTTPAdapter(max_retries=retries))
            response = session.get(paramurl)

        if response.status_code == 200:
            html_content = response.content
            soup = BeautifulSoup(html_content, 'lxml')

            partassemthumblist_div = soup.find('div', {'id': 'partassemthumblist'})
            a_tags = partassemthumblist_div.find_all('a')

            for a_tag in a_tags:
                href_value = a_tag.get('href')
                getDetailOEMData(url + href_value)
    except Exception as e:
        print(f"Error in getOEMData: {e}")

def getOEMYear(paramurl):
    try:
        with requests.Session() as session:
            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
            session.mount('https://', HTTPAdapter(max_retries=retries))
            response = session.get(paramurl)

        if response.status_code == 200:
            html_content = response.content
            soup = BeautifulSoup(html_content, 'lxml')

            span_tags = soup.select('li[itemprop="itemListElement"] span[itemprop="name"]')
            span_contents = [span_tag.get_text(strip=True) for span_tag in span_tags]

            a_tags = soup.select('.partsubselect.columnlist.columnlist_33 li a')
            hrefs = [a['href'] for a in a_tags]
            texts = [a.text for a in a_tags]

            for href, text in zip(hrefs, texts):
                all_span_contents = span_contents + [text, url + href]
                getOEMData(url + href)
    except Exception as e:
        print(f"Error in getOEMYear: {e}")

def getOEMParts(paramurl):
    try:
        with requests.Session() as session:
            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
            session.mount('https://', HTTPAdapter(max_retries=retries))

            response = session.get(paramurl)

        if response.status_code == 200:
            html_content = response.content
            soup = BeautifulSoup(html_content, 'lxml')

            ul_element = soup.find('ul', class_='partsubselect columnlist')

            if ul_element:
                a_tags = ul_element.find_all('a')
                href_attributes = [a.get('href', '') for a in a_tags]

                with ThreadPoolExecutor() as executor:
                    executor.map(getOEMYear, [url + hrefitem for hrefitem in href_attributes])

            else:
                print("Ul element not found.")
    except Exception as e:
        print(f"Error in getOEMParts: {e}")

response = requests.get(url + "/oemparts")

if response.status_code == 200:
    html_content = response.content
    soup = BeautifulSoup(html_content, 'lxml')
    oem_parts_links = soup.find('a', text='OEM Parts')
    first_oem_parts_link = oem_parts_links if oem_parts_links else None
    if first_oem_parts_link:
        href = first_oem_parts_link.get('href', '')
        # print(f"Href: {href}")

        ul_element = first_oem_parts_link.find_next('ul', class_='navlisthorz subnav')
        subnav_items = ul_element.find_all('li') if ul_element else []
        subnav_data = [{'text': item.text, 'href': url + item.find('a').get('href', '')} for item in subnav_items]
        # print(f"Subnav Items: {subnav_data}")

        df = pd.DataFrame(subnav_data)

        # Specify the file path
        for item in subnav_data:
            response = requests.get(item['href'])
            soup = BeautifulSoup(response.content, 'lxml')
            # Find all div elements with the specified structure
            target_divs = soup.select('.container_16 .grid_33 .contentwrapper > div[style=""] > p > a')

            # Extract and print the href attributes
            href_attributes = [div.get('href', '') for div in target_divs]
            for hrefitem in href_attributes:
                getOEMParts(url + hrefitem)
            # print(f"Href Attributes: {href_attributes}")

        # Write DataFrame to CSV file
        df.to_csv(csv_file_path, index=False)

    # print(soup)

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Close the CSV files
csv_file_model.close()
csv_file.close()
