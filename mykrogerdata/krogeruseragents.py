
headers = {
        'Origin': "https://www.kroger.com",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
        'Content-Type': "application/json",
        'Accept': "application/json",
        'Referer': 'https://www.kroger.com/signin?redirectUrl=/account/update',
        'Sec-Fetch-Dest' : 'empty'
        }


purchase_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Content-Type': 'application/json','Referer' : 'https://www.kroger.com/mypurchases',
                'Accept': 'application/json', 
                'Origin': 'https://www.kroger.com'}





starting_headers = {
        'Origin': "https://www.kroger.com",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36",
        'Content-Type': "application/json;charset=UTF-8",
        'Accept': "application/json",
        'sec_req_type': "ajax",
        'Referer': 'https://www.kroger.com/signin?redirectUrl=/account/update'
        }


final_request_headers ={
'accept': 'application/json, text/plain, */*',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'en-US,en;q=0.9',
'content-type': 'application/json;charset=UTF-8',
'origin': 'https://www.kroger.com',
'referer': 'https://www.kroger.com/signin?redirectUrl=/',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-origin'
}