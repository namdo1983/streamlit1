from email import header
from tkinter.messagebox import NO
import streamlit as st
import requests
import pandas as pd
from playwright.sync_api import sync_playwright
from pathlib import Path
from time import perf_counter
import speedtest
from datetime import datetime


BASE_DIR = Path(__file__).parent
print(BASE_DIR)
date_object = datetime.now().strftime("%d_%B_%Y_%H_%M_%S")
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
s = requests.Session()


def get_network_name():
    try:
        s = speedtest.Speedtest()
        res = s.get_config()
        ip_nm = res["client"]["ip"]
        ten_nm = res["client"]["isp"]
        return ip_nm, ten_nm
    except Exception as err:
        print(err)


def layout():
    ip, my_isp = get_network_name()
    print(my_isp)
    st.subheader('Free Broken Link Checker.')
    input_text = st.text_input(
        label='Check your site for broken inbound and outbound links in seconds.', placeholder='Enter domain or URL')
    if 'https://' not in input_text and input_text is not None:
        st.warning('Please enter valid URLs')

    elif st.button('Check broken links') and 'https://' in input_text:
        with st.spinner('Please wait. Checking...'):
            start = perf_counter()
            data = input_text.strip()

            my_table = []
            # for item in data:
            # data = data.decode('utf-8')
            if 'http' not in data:
                data = 'http://' + data
            my_table, URLs = check_broken_links(data)

            if my_table == []:
                st.warning('There no data to check.')

            elif my_table is not None:
                print(my_table)
                if URLs == 0:
                    st.warning('Something Went Wrong.')
                else:
                    st.info(f'100% scanned - {URLs}/{URLs} URLs checked.')

                df = pd.DataFrame(my_table)
                print(df.columns)
                df.columns = ('URL', 'STATUS')
                df['ISP'] = my_isp
                if ':' not in ip:
                    df['IPv4'] = ip
                else:
                    df['IPv6'] = ip
                st.write(df)
                end = perf_counter() - start
                st.success(f'Process completed in {end:.2f} seconds.')


@st.cache(suppress_st_warning=True, show_spinner=False)
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


@st.cache(suppress_st_warning=True, show_spinner=False)
def check_broken_links(url):
    # url = 'https://nbet.win/'
    total_urls = []
    my_result = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        page = br.new_page()
        try:
            r = s.get(url, headers=headers, timeout=5)

        except:
            content = url, 'This site can not be reached.'
            my_result.append(content)
        else:
            if r.ok:
                page.goto(url)
                pages = page.query_selector_all('[href]')

                for item in pages:
                    my_page = item.get_attribute('href')
                    print(my_page)
                    total_urls.append(my_page)
                images = page.query_selector_all('[src]')
                for item in images:
                    src = item.get_attribute('src')
                    # print(src)
                    if 'https://' in src:
                        total_urls.append(src)

                for url in list(set(total_urls)):
                    try:
                        r = s.get(url, headers=headers, timeout=5)
                        print('Checking...', r.url, r.status_code)
                    except requests.exceptions.RequestException as e:
                        print(url, ' ===> ', e)
                    else:
                        if not r.ok:
                            print('Failed...', r.url, r.status_code)
                            content = r.url, str(
                                r.status_code) + ' ' + r.reason
                            my_result.append(content)
            else:
                content = r.url, str(r.status_code) + ' ' + r.reason
                my_result.append(content)
        br.close()

    print(total_urls)
    return my_result, len(total_urls)


def main():
    st.set_page_config(
        page_title="Free Broken Link Tools"
    )
    try:
        layout()
    finally:
        print('Closed Browsers Completed.')


if __name__ == '__main__':
    main()
