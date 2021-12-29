import streamlit as st
import requests

s = requests.Session()


def layout():
    st.write('Check Access Domain...')
    uploaded_file = st.file_uploader('Browser A File', type=['txt'])
    # print(dir(uploaded_file))
    if st.button('Process') and uploaded_file is not None:
        # To read file as bytes:
        data = uploaded_file.readlines()
        # st.write(data)
        # st.text(data)

        for idx, item in enumerate(data, start=1):
            try:
                r = s.get(item.strip(), timeout=5)
            except Exception as e:
                print(e)
                err = {f'{idx}. {item.decode("utf-8").strip()}': str(e)}
                # err = f'{idx}. {item.decode("utf-8").strip()}' + str(e)
                st.write(err)
            else:
                if r.ok:
                    print('OK')
                else:
                    print(item, r.status_code, r.reason)
                st.write(idx, r.url, r.status_code, r.reason)



def main():
    layout()


if __name__ == '__main__':
    main()