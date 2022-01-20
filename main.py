import streamlit as st
import pandas as pd
from requests_html import HTMLSession
from pathlib import Path
from time import perf_counter
import speedtest
from datetime import datetime


BASE_DIR = Path(__file__).parent

date_object = datetime.now().strftime("%d_%B_%Y_%H_%M_%S")
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
s = HTMLSession()


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
    st.title('Free Broken Link Checker.')
    input_text = st.text_input(
        label='Check your site for broken links in seconds.', placeholder='Enter domain or URL', max_chars=255)
    if not input_text.startswith('http') or len(input_text) >= 255:
        st.warning('Please enter valid Domain or URL or <= 255 Characters.')

    elif st.button('Check broken links') and input_text.startswith('http') and len(input_text) < 255:
        with st.spinner('Please wait. Checking...'):
            start = perf_counter()
            data = input_text.strip()

            my_table = []
            if 'http' not in data:
                data = 'http://' + data
            my_table, URLs = check_broken_links(data)

            if my_table == []:
                st.warning('No broken link found.')

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

                df.index += 1
                st.write(df)
                end = perf_counter() - start
                st.success(f'Process completed in {end:.2f} seconds.')


# @st.cache(suppress_st_warning=True, show_spinner=False)
# def convert_df(df):
#     return df.to_csv(index=False).encode('utf-8')


@st.cache(suppress_st_warning=True, show_spinner=False)
def check_broken_links(url):
    # url = 'https://nbet.win/'
    total_urls = []
    my_result = []
    try:
        r = s.get(url)
    except:
        content = url, 'This site can not be reached.'
        my_result.append(content)
    else:
        if r.ok:
            pages = r.html.find('[href]')
            print(pages)
            for link in pages:
                print(link.attrs['href'])
                total_urls.append(link.attrs['href'])

            pages = r.html.find('[src]')
            for link in pages:
                print(link.attrs['src'])
                total_urls.append(link.attrs['src'])
        else:
            content = r.url, str(r.status_code) + ' ' + r.reason
            my_result.append(content)

    for url in list(set(total_urls)):
        try:
            r = s.get(url)
            print('Checking...', r.url, r.status_code)
        except:
            pass
        else:
            if not r.ok:
                print('Failed...', r.url, r.status_code)
                content = r.url, str(
                    r.status_code) + ' ' + r.reason
                my_result.append(content)


    return my_result, len(total_urls)


def main():
    st.set_page_config(
        page_title="Demo Free SEO Tools"
    )
    try:
        layout()
    finally:
        print('Process Completed.')


if __name__ == '__main__':
    main()
