mkdir -p ~/.streamlit/

echo "\
[theme]\n\
primaryColor='#E694FF'\n\
backgroundColor='#00172B'\n\
secondaryBackgroundColor = '#0083B8'\n\
textColor='#FFF'\n\
font='sans serif'\n\

[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml

