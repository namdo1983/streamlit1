import streamlit as st
import requests
import pandas as pd
import speedtest
from time import perf_counter

s = requests.Session()
my_headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
s.headers.update(my_headers)

#Page Title
st.set_page_config(
        page_title="Check Access Domain", layout='wide'
)

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

def layout():
    ip, my_isp = get_network_name()
    print(my_isp)
    st.header('Please import a file...')
    uploaded_file = st.file_uploader('Select A File with *.TXT', type=['txt'])
    if uploaded_file is None:
        st.warning('Please select valid file')
    # st.warning('Please select a valid file before process')
    elif st.button('Process') and uploaded_file is not None:
        # To read file as bytes:
        with st.spinner('Please wait...'):
            start = perf_counter()
            data = uploaded_file.readlines()
            my_table = check_url(data)
            df = pd.DataFrame(my_table)
            df.columns=('No.', 'Domain', 'Result')
            df['Your ISP'] = my_isp
            if '::' not in ip:
                df['Your IP v4'] = ip
            else:
                df['Your IP v6'] = ip
            df.set_index('No.', inplace=True)
            st.write(df)
            # Download result as excel file
            # st.download_button('Export To Excel', data=df, file_name='rp.xlsx')
            end = perf_counter() - start
            st.success(f'Process completed in {end:.2f} seconds.')


@st.cache(suppress_st_warning=True, show_spinner=False)
def check_url(data):
    my_table = []
    for idx, item in enumerate(data, start=1):
        if b'http' not in item:
            item = b'http://' + item
        try:
            r = s.get(item.strip(), timeout=2)
        except Exception as e:
            print(e)
            new_e = str(e)
            new_e = new_e.split(':')[0]
            # err = {f'{idx}. {item.decode("utf-8").strip()}': str(e)}
            err = idx, str(item.decode("utf-8").strip()), str(new_e)
            # st.error(err)
            my_table.append(err)
        else:
            if r.ok:
                print('OK')
            else:
                print(item, r.status_code, r.reason)
            content = idx, r.url, r.reason
            my_table.append(content)
    return my_table


def main():
    try:
        load_snow_animate()
        layout()
    finally:
        print('Done')


if __name__ == '__main__':
    main()


