client=''

curl -X POST \
     --header 'Authorization: Basic ${client}' \
     --header "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials" \
     'https://accounts.spotify.com/api/token' 
