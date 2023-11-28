import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# File path for the CSV file
csv_file_path_model = "project11.csv"

csv_file_path = "project12.csv"

# Initialize global variable for the CSV file
global csv_file
csv_file_model = open(csv_file_path_model, mode='w', newline='')
csv_file = open(csv_file_path, mode='w', newline='')

csv_writer_model = csv.writer(csv_file_model)
csv_writer = csv.writer(csv_file)
def write_to_csv_model(row):
    global csv_writer_model

    # Write a row to the CSV file
    csv_writer_model.writerow(row)
def write_to_csv(row):
    global csv_writer

    # Write a row to the CSV file
    csv_writer.writerow(row)

url = 'https://www.babbittsonline.com'
def getDetailOEMData(paramurl):
    response = requests.get(paramurl)

    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'lxml')
        # Find all <span> tags within <li> tags with itemprop "name"
        span_tags = soup.select('li[itemprop="itemListElement"] span[itemprop="name"]')

        span_contents = []
        # Extract and print the content of each <span> tag
        for span_tag in span_tags:
            span_content = span_tag.get_text(strip=True)
            span_contents.append(span_content)
            # print(span_content)
        # Find the <h2> tag
        h2_tag = soup.find('h2')

        # Get the text content of the <h2> tag
        h2_text = h2_tag.text
        span_contents.append(h2_text)

        # Find all div elements with class partlistrow
        partlistrows = soup.find_all('div', class_='partlistrow')

        # Loop through each partlistrow
        for partlistrow in partlistrows:
            # Get the span content within the c0 div
            span_c0 = partlistrow.find('div', class_='c0').span.text
            
            # Get the span content within the c1a div
            span_c1a = partlistrow.find('div', class_='c1a').span.text
            
            # Get the text content of each span within the c1b div
            spans_c1b = partlistrow.find('div', class_='c1b').find_all('span')
            
            # Extract text content from the spans within c1b div
            span_texts_c1b = [span.text for span in spans_c1b]
            if len(span_texts_c1b) == 2:
                # Process the spans if there are exactly 2
                # Extract information from span_texts_c1b[0] and span_texts_c1b[1]
                span1, span2 = span_texts_c1b
                # Option 1: Write the first order
                
                all_span_contents = []
                all_span_contents.extend(span_contents)
                all_span_contents.extend([span_c0, span_c1a, span1, paramurl, "", span2])
                write_to_csv(all_span_contents)

                # Option 2: Write the second order (with modified order)
                all_span_contents = []
                all_span_contents.extend(span_contents)
                all_span_contents.extend([span_c0, span_c1a, span2, paramurl, "", span1])
                write_to_csv(all_span_contents)
            else:
                # Handle the case where the length is not 2
                all_span_contents = []
                all_span_contents.extend(span_contents)
                all_span_contents.extend([span_c0, span_c1a, span_texts_c1b[0], paramurl, "", ""])
                write_to_csv(all_span_contents)

        
def getOEMData(paramurl):
    response = requests.get(paramurl)

    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'lxml')
        # Find the div with id 'partassemthumblist'
        partassemthumblist_div = soup.find('div', {'id': 'partassemthumblist'})

        # Find all the <a> tags within the div
        a_tags = partassemthumblist_div.find_all('a')

        # Extract and print the href attribute from each <a> tag
        for a_tag in a_tags:
            href_value = a_tag.get('href')
            getDetailOEMData(url + href_value)
            # print(href_value)

def getOEMYear(paramurl):
    response = requests.get(paramurl)

    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'lxml')
        span_tags = soup.select('li[itemprop="itemListElement"] span[itemprop="name"]')

        span_contents = []
        # Extract and print the content of each <span> tag
        for span_tag in span_tags:
            span_content = span_tag.get_text(strip=True)
            span_contents.append(span_content)


        # Find the <ul> with class "partsubselect columnlist columnlist_33"
        a_tags = soup.select('.partsubselect.columnlist.columnlist_33 li a')
        # Extract hrefs and text from <a> tags
        hrefs = [a['href'] for a in a_tags]
        texts = [a.text for a in a_tags]
        # Print the results
        for href, text in zip(hrefs, texts):
            # print(f"Href: {href}, Text: {text}")
            all_span_contents = []
            all_span_contents.extend(span_contents)
            all_span_contents.extend([text,url + href])
            #write_to_csv_model(all_span_contents)
            getOEMData(url + href)
        # Extract the href attributes from all <a> tags within the <ul>
def getOEMParts(paramurl):
    response = requests.get(paramurl)

    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'lxml')
        # Find the <ul> with class "partsubselect columnlist"
        ul_element = soup.find('ul', class_='partsubselect columnlist')

        # Extract the href attributes from all <a> tags within the <ul>
        if ul_element:
            a_tags = ul_element.find_all('a')
            href_attributes = [a.get('href', '') for a in a_tags]
            for hrefitem in href_attributes:
                getOEMYear(url + hrefitem)
                # print(f"Href Attributes: {url + hrefitem}")
        else:
            print(f"Href Attributes: {url + hrefitem}")
            print("Ul element not found.")



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
        csv_file_path = 'title.csv'
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