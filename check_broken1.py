import streamlit as st
import requests
import pandas as pd
from RPA.Browser.Selenium import Selenium


s = requests.Session()
br = Selenium()

def layout():
    st.header('Check Access Domain...')
    uploaded_file = st.file_uploader('Select A File with *.TXT', type=['txt'])
    if uploaded_file is None:
        st.warning('Please select valid file')
        
    # st.warning('Please select a valid file before process')
    elif st.button('Process') and uploaded_file is not None:
        # To read file as bytes:
        data = uploaded_file.readlines()
        # st.write(data)
        # st.text(data)
        my_table = []
        for idx, item in enumerate(data, start=1):
            try:
                r = s.get(item.strip(), timeout=5)
            except Exception as e:
                print(e)
                new_e = str(e)
                new_e = new_e.split(':')[0]
                # err = {f'{idx}. {item.decode("utf-8").strip()}': str(e)}
                err = idx, str(item.decode("utf-8").strip()), str(new_e),' TOANG'
                # st.error(err)
                my_table.append(err)
            else:
                if r.ok:
                    print('OK')
                else:
                    print(item, r.status_code, r.reason)
                content = idx, r.url, str(r.status_code), r.reason
                my_table.append(content)
        print(type(my_table))
        df = pd.DataFrame(my_table)
        print(df.columns)
        df.columns=('No.', 'Domain', 'Status', 'Reason')
        # df.style.set_properties(subset=['Status'], **{'width': '500px'})
        df.set_index('No.', inplace=True)
        st.write(df)

        st.info('Process completed.')

def check_broken_links():
    url = 'https://nbet.win/'
    total_urls = []
    br.open_headless_chrome_browser(url)
    pages = br.get_webelements('css=[href]')
    for item in pages:
        page = br.get_element_attribute(item, 'href')
        if 'https://' in page:
            # print(href)
            total_urls.append(page)
    images = br.get_webelements('css=[src]')
    for item in images:
        src = br.get_element_attribute(item, 'src')
        # print(src)
        if 'https://' in src:
            total_urls.append(src)
    # images_set = br.get_webelements('css=[srcset]')
    # for item in images_set:
    #     src_set = br.get_element_attribute(item, 'srcset')
    #     # print(src)
    #     if 'https://' in src_set:
    #         total_urls.append(src_set)
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    print(len(list(set(total_urls))))
    for url in list(set(total_urls)):
        try:
            r = s.get(url, headers=headers, timeout=5)
            # print('Checking...', r.url, r.status_code)
        except:
            pass
        else:
            if not r.ok:
                print('Failed...', r.url, r.status_code)

def main():
    # layout()
    check_broken_links()


if __name__ == '__main__':
    main()