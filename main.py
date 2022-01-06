import streamlit as st
import requests
import pandas as pd
import speedtest
from datetime import datetime
from time import perf_counter
import os


s = requests.Session()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

my_headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
s.headers.update(my_headers)

date_object = datetime.now().strftime("%d_%B_%Y_%H_%M_%S")


def get_network_name():
    try:
        s = speedtest.Speedtest()
        res = s.get_config()
        ip_nm = res["client"]["ip"]
        ten_nm = res["client"]["isp"]
        # Viettel LAN 115.78.231.117
        # Viettel 4G 125.235.185.199
        # print('Địa chỉ IP public:', ip_nm)
        # print('Tên nhà mạng:', ten_nm)
        return ip_nm, ten_nm
    except Exception as err:
        print(err)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def load_snow_animate():
    # Use local CSS
    local_css("style/style.css")
    # Load Animation
    animation_symbol = "❄"
    st.markdown(
        f"""
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        """,
        unsafe_allow_html=True,
    )
    return

@st.cache(suppress_st_warning=True, show_spinner=False)
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def layout():
    ip, my_isp = get_network_name()
    print(my_isp)
    st.title('Please import a file with valid domain to check access the page...')
    st.text('Example valid domain includes: https://google.com or google.com or www.google.com')
    uploaded_file = st.file_uploader('Select A File with *.TXT', type=['txt'])

    if uploaded_file is None:
        st.warning('Please select valid file')

    elif st.button('Process') and uploaded_file is not None:
        with st.spinner('Please wait. Checking...'):

            start = perf_counter()
            data = uploaded_file.readlines()
            my_table = check_url(data)
            df = pd.DataFrame(my_table)
            df.columns=('No.', 'Domain', 'Result')
            df['Your ISP'] = my_isp
            if ':' not in ip:
                df['Your IP Address is IPv4'] = ip
            else:
                df['Your IP Address is IPv6'] = ip
            df.set_index('No.', inplace=True)
            st.write(df)

            # Download result as excel file
            csv = convert_df(df)
            
            end = perf_counter() - start
            st.success(f'Process completed in {end:.2f} seconds.')

            st.download_button('Download Results As CSV', csv, f"{date_object}_file.csv", "text/csv",)

@st.cache(suppress_st_warning=True, show_spinner=False)
def check_url(data):
    my_table = []
    for idx, item in enumerate(data, start=1):
        if b'http' not in item:
            item = b'http://' + item
        try:
            r = s.get(item.strip(), headers=my_headers, timeout=5)
            r.encoding='utf-8'
            # print(r.text)
        except requests.exceptions.ConnectionError as e:
            # print(e)
            new_e = str(e)
            new_e = new_e.split(': ')[-1]
            # err = {f'{idx}. {item.decode("utf-8").strip()}': str(e)}
            err = idx, str(item.decode("utf-8").strip()), "This site can't be reached" # "This site can't be reached"
            my_table.append(err)
        except requests.exceptions.Timeout as ct:
            # print(e)
            new_e = str(ct)
            # new_e = new_e.split(': ')[-1]
            err = idx, str(item.decode("utf-8").strip()), new_e # "This site can't be reached"
            my_table.append(err)
        else:
            if r.ok:
                print(f'Checking domain -----> {r.url}')
                check_domain_results(my_table, idx, str(item.decode("utf-8").strip()), r)
            elif r.status_code == 503 and 'Checking your browser before accessing' in r.text:
                content = idx, r.url, "DDoS protection by Cloudflare"
                my_table.append(content)
            elif r.status_code == 500 and '{"status":false,"msg":"Internal Server Error"}' in r.text:
                content = idx, r.url, '{"status":false,"msg":"Internal Server Error"}'
                my_table.append(content)
            elif r.status_code == 522 and 'Connection timed out' in r.text:
                content = idx, r.url, 'Error 522'
                my_table.append(content)

            content = idx, r.url, r.reason
            my_table.append(content)

    return my_table

def check_domain_results(my_table, idx, item, r):
    if 'This domain has expired. Is this your domain?' in r.text:
        content = idx, item, 'This domain has expired. Is this your domain?'
        my_table.append(content)
    elif '404 Page' in r.text:
        content = idx, item, "404 Page"
        my_table.append(content)
    elif 'This premium domain has expired' in r.text:
        content = idx, item, "This premium domain has expired"
        my_table.append(content)
    elif "AN NINH" in r.text:
        content = idx, item, "BỘ CÔNG AN"
        my_table.append(content)
    elif "Why purchase this domain with Epik?" in r.text:
        content = idx, item, "Why purchase this domain with Epik?"
        my_table.append(content)
    elif "Registered at Namecheap.com" in r.text:
        content = idx, item, "Registered at Namecheap.com"
        my_table.append(content)
    elif "Domain parked by OnlyDomains" in r.text:
        content = idx, item, "Domain parked by OnlyDomains"
        my_table.append(content)
    elif "This domain is parked free of charge with NameSilo.com" in r.text:
        content = idx, item, "This domain is parked free of charge with NameSilo.com"
        my_table.append(content)
    elif "Get WordPress" in r.text:
        content = idx, item, "Domain WordPress"
        my_table.append(content)
    elif "mobifone.vn/typing-wrong" in r.text:
        content = idx, item, "404 mobifone"
        my_table.append(content)
    # elif len(r.history) >= 2:
    elif r.history:
        r_301 = idx, item, f'OK. Redirect to -----> {r.url}'
        my_table.append(r_301)


def main():
    #Page Title
    st.set_page_config(
            page_title="Check Access Domain", layout='wide'
    )
    
    try:
        load_snow_animate()
        layout()
    finally:
        print('Done')


if __name__ == '__main__':
    main()


