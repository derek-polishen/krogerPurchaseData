import requests, json,sys
import urllib.request
import time, datetime
import pandas as pd
from pandas.io.json import json_normalize
import getpass
import krogeruseragents as ua
import krogerdata as kd
import datatransformations as dt
from requests_html import HTMLSession


url = "https://www.kroger.com"
kroger_login_url = "https://www.kroger.com/signin?redirectUrl=/"
sign_in = 'https://www.kroger.com/auth/api/sign-in' #sign-in API
purchases_summary_url = 'https://www.kroger.com/mypurchases/api/v1/receipt/summary/by-user-id/' #purchases summary level
detail_purchases = 'https://www.kroger.com/mypurchases/api/v1/receipt/detail'
account_url = 'https://www.kroger.com/accountmanagement/api/profile'

def kroger_sign_in():
            
    with requests.Session() as sess:
        sess.cookies.clear()
        sess.get('https://www.kroger.com',headers=ua.headers)
        time.sleep(20)
        b = sess.get(kroger_login_url,headers=ua.headers)
        print(b.request.headers)
        time.sleep(20)
        login_response = {'statusCode': '000'}
        login_attempts = 3
        while login_response['statusCode'] != 200 and login_attempts > 0:
            try:
                username= input('What is your email address for your Kroger account? ')
                password = getpass.getpass('What is your password? (Note: password will not appear if running in terminal..) ')
                login_payload = json.dumps({"email": username,"password": password, "rememberMe":False})
                login_post = sess.post(sign_in, headers=ua.headers, data=login_payload.encode('UTF-8'))
                login_response = login_post.json()
            except:
                while login_attempts > 0:
                    login_post = sess.post(sign_in, headers=ua.headers, data=login_payload.encode('UTF-8'))
                    login_attempts -= 1
                    print("Post request failed...please try again \n")
                
            if login_response['statusCode'] != 200:
                if login_attempts == 1:
                    print("Exiting program...")
                    sys.exit()
                else:
                    login_attempts -= 1
                    print(f"{login_response['statusCode']} - {login_response['statusMessage']}")
                    print(f"{login_attempts} login attempt(s) left!")
            else:
                print("Login successful! Please wait while your data is downloaded...")

        
        account_info = sess.get(account_url,headers=ua.headers,timeout=20)
        account_json = account_info.json()

        with open('config.py', "w") as config_file:
            config_file.write('banner_name = ' + json.dumps({'banner' : account_json['bannerSpecificDetails'][0]['banner']}))
            config_file.write('\n')
            config_file.write('store_number = ' + json.dumps({'store_num' : account_json['bannerSpecificDetails'][0]['preferredStoreNumber']}))
            config_file.write('\n')
            config_file.write('division = ' + json.dumps({'division_num' : account_json['bannerSpecificDetails'][0]['preferredStoreDivisionNumber']}))
            


        summary_transactions = sess.get(purchases_summary_url, headers=ua.purchase_headers)




        summary_data = summary_transactions.json()
        print("Total of " + str(len(summary_data)) + " transactions found!")

        receipt_data_list = []
        all_detailed_transactions = []

        for receipt in summary_data: #get summary json and parse into list 
            divNum = receipt['receiptId']['divisionNumber']
            storeNum = receipt['receiptId']['storeNumber']
            termNum = receipt['receiptId']['terminalNumber']
            transDate = receipt['receiptId']['transactionDate']
            transId = receipt['receiptId']['transactionId']
            new_json_data = {"divisionNumber" : divNum, "storeNumber" : storeNum, "terminalNumber" : termNum, "transactionDate": transDate, "transactionId": transId}
            receipt_data_list.append(new_json_data)


        try:
            #Load the most recent extract and find most recent purchase
            max_receipt_id = kd.load_most_recent_receipt_csv()
            all_receipts_df = dt.get_receipt_ids(receipt_data_list)
            stop_receipts = all_receipts_df.index(max_receipt_id)

            if stop_receipts == 0:
                print("No new transactions have been found. Exiting program...")
                exit()
            else:
                print(f"{stop_receipts-1} new transactions have been found! Pulling data now!")

                for receipt in receipt_data_list[0:stop_receipts]:
                    detailed_transaction = sess.post(detail_purchases, headers=ua.headers, json=receipt)
                    detailed_json = detailed_transaction.json()
                    all_detailed_transactions.append(detailed_json)
        except:
            print("No previous files found...Pulling all of your data!")
            total_trans = len(receipt_data_list)
            for detail in receipt_data_list:
                detailed_transaction = sess.post(detail_purchases, headers=ua.headers, json=detail)
                detailed_json = detailed_transaction.json()
                all_detailed_transactions.append(detailed_json)

        


    print("Data was successfully retrieved!")

    return all_detailed_transactions



def session_sign_in():
    
    new_session = HTMLSession()
    new_session.cookies.clear()
    time.sleep(1)
    sign_in = 'https://www.kroger.com/auth/api/sign-in' #sign-in API
    a = new_session.get('https://www.kroger.com')
    a.html.render()
    print(a.request.headers)
    time.sleep(5)
    n = new_session.get('https://www.kroger.com/signin?redirectUrl=/account/dashboard', headers=a.request.headers)
    n.html.render()
    time.sleep(8)
    print('*********** new headers **********')
    print(n.request.headers)
    username= input('What is your email address for your Kroger account? ')
    password = getpass.getpass('What is your password? (Note: password will not appear in the console...) ')
    login_payload = json.dumps({"email": username,"password": password, "rememberMe":False})
    login_post = new_session.post(sign_in, headers=n.request.headers,data=login_payload.encode('UTF-8'))
    print(login_post)


    if login_post.json()['authenticationState']['authenticated'] == True:
        print("Success!")

    else:
        print("Something went wrong...Exiting program...")
        sys.exit()


    account_info = new_session.get(account_url,headers=ua.headers,timeout=20)
    account_json = account_info.json()

    with open('config.py', "w") as config_file:
        config_file.write('banner_name = ' + json.dumps({'banner' : account_json['bannerSpecificDetails'][0]['banner']}))
        config_file.write('\n')
        config_file.write('store_number = ' + json.dumps({'store_num' : account_json['bannerSpecificDetails'][0]['preferredStoreNumber']}))
        config_file.write('\n')
        config_file.write('division = ' + json.dumps({'division_num' : account_json['bannerSpecificDetails'][0]['preferredStoreDivisionNumber']}))
            


    summary_transactions = new_session.get(purchases_summary_url, headers=ua.purchase_headers)




    summary_data = summary_transactions.json()
    print("Total of " + str(len(summary_data)) + " transactions found!")

    receipt_data_list = []
    all_detailed_transactions = []

    for receipt in summary_data: #get summary json and parse into list 
        divNum = receipt['receiptId']['divisionNumber']
        storeNum = receipt['receiptId']['storeNumber']
        termNum = receipt['receiptId']['terminalNumber']
        transDate = receipt['receiptId']['transactionDate']
        transId = receipt['receiptId']['transactionId']
        new_json_data = {"divisionNumber" : divNum, "storeNumber" : storeNum, "terminalNumber" : termNum, "transactionDate": transDate, "transactionId": transId}
        receipt_data_list.append(new_json_data)


    try:
        #Load the most recent extract and find most recent purchase
        max_receipt_id = kd.load_most_recent_receipt_csv()
        all_receipts_df = dt.get_receipt_ids(receipt_data_list)
        stop_receipts = all_receipts_df.index(max_receipt_id)

        if stop_receipts == 0:
            print("No new transactions have been found. Exiting program...")
            exit()
        else:
            print(f"{stop_receipts-1} new transactions have been found! Pulling data now!")

            for receipt in receipt_data_list[0:stop_receipts]:
                detailed_transaction = new_session.post(detail_purchases, headers=ua.headers, json=receipt)
                detailed_json = detailed_transaction.json()
                all_detailed_transactions.append(detailed_json)
    except:
        print("No previous files found...Pulling all of your data!")
        total_trans = len(receipt_data_list)
        for detail in receipt_data_list:
            detailed_transaction = new_session.post(detail_purchases, headers=ua.headers, json=detail)
            detailed_json = detailed_transaction.json()
            all_detailed_transactions.append(detailed_json)

        


    print("Data was successfully retrieved!")

    return all_detailed_transactions