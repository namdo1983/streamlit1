import streamlit as st
import requests
import pandas as pd
from time import perf_counter

s = requests.Session()

# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def layout():
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

    st.header('Check Access Domain...')
    uploaded_file = st.file_uploader('Select A File with *.TXT', type=['txt'])
    if uploaded_file is None:
        st.warning('Please select valid file')
    # st.warning('Please select a valid file before process')
    elif st.button('Process') and uploaded_file is not None:
        # To read file as bytes:
        
        data = uploaded_file.readlines()
        my_table = check_url(data)
        df = pd.DataFrame(my_table)
        print(df.columns)
        df.columns=('No.', 'Domain', 'Status', 'Reason')
        # df.style.set_properties(subset=['Status'], **{'width': '500px'})
        df.set_index('No.', inplace=True)
        st.write(df)

@st.cache(suppress_st_warning=True)
def check_url(data):
    start = perf_counter()
    my_table = []
    for idx, item in enumerate(data, start=1):
        if b'http' not in item:
            item = b'http://' + item
        with st.spinner('Sếp chờ e xíu...'):
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
    end = perf_counter() - start
    st.success(f'Process completed in {end:.2f} seconds.')
    return my_table

def main():
    layout()


if __name__ == '__main__':
    main()