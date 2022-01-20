import streamlit as st
import requests
import pandas as pd
from playwright.sync_api import sync_playwright
from pathlib import Path


BASE_DIR = Path(__file__).parent
print(BASE_DIR)
s = requests.Session()


def layout():
    st.header('Check Access Domain...')
    uploaded_file = st.file_uploader('Select A File with *.TXT', type=['txt'])
    if uploaded_file is None:
        st.warning('Please select valid file')

    elif st.button('Process') and uploaded_file is not None:
        with st.spinner('Please wait. Checking...'):
            data = uploaded_file.readlines()
            # st.write(data)
            # st.text(data)
            my_table = []
            for item in data:
                item = item.decode('utf-8')
                if 'http' not in item:
                    item = 'http://' + item
                my_table = check_broken_links(item)

            if my_table is []:
                st.write('There no data to check.')

            elif my_table is not None:
                print(my_table)
                df = pd.DataFrame(my_table)
                print(df.columns)
                df.columns=('Domain', 'Status')
                # df.style.set_properties(subset=['Status'], **{'width': '500px'})
                # df.set_index('Domain', inplace=True)
                st.write(df)

                st.info('Process completed.')

# @st.cache(suppress_st_warning=True, show_spinner=False)
def check_broken_links():
    url = 'https://nbet.win/'
    total_urls = []
    my_result = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        page = br.new_page()
        try:
            page.goto(url)
        except:
            content = url, 'This site can not be reached.'
            my_result.append(content)
        else:
            pages = page.query_selector_all('xpath=//a[@href]')
            print(pages)
            for item in pages:
                my_page = item.get_attribute('href')
                if 'https://' in my_page:
                    # print(href)
                    total_urls.append(my_page)
            images = page.query_selector_all('xpath=//img[@src]')
            for item in images:
                src = item.get_attribute('src')
                print(src)
                if 'https://' in src:
                    total_urls.append(src)

            headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
            
            for url in list(set(total_urls)):
                try:
                    r = s.get(url, headers=headers, timeout=5)
                    print('Checking...', r.url, r.status_code)
                except:
                    pass
                else:
                    if not r.ok:
                        print('Failed...', r.url, r.status_code)

                    content = r.url, r.status_code
                    my_result.append(content)
        br.close()

    return my_result

def main():
    try:
        # layout()
        check_broken_links()
    finally:
        print('Closed Browsers Completed.')



if __name__ == '__main__':
    main()