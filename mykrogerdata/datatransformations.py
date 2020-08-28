import requests, json,sys
import urllib.request
import time, datetime
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize


extract_date_time = datetime.datetime.now().replace(microsecond=0)

def transform_receipt_data(receipt):

    

    for transaction in receipt:
        transaction['receiptId'] = [transaction['receiptId']]

    normalize_transactions = json_normalize(data=receipt,record_path=['receiptId'], meta=['loyaltyId', 'address', 'fulfillmentType', 'items', 'source', 'subtotal', 'tax','tenders', 'total', 'totalLineItems', 'totalSavings', 'totalTax', 'totalTender', 'totalTenderChange','transactionTime', 'transactionTimeWithTimeZone', 'version', 'receiptId'  ], errors='ignore')
    #perform data transformations to gather additional information from each transaction
    normalize_transactions['extractdate'] = extract_date_time
    normalize_transactions['transactionid'] = normalize_transactions['receiptId'].apply(lambda x:x.get('transactionId'))
    normalize_transactions['streetaddress1'] = normalize_transactions['address'].apply(lambda x:x.get('address1'))
    normalize_transactions['streetaddress2'] = normalize_transactions['address'].apply(lambda x:x.get('address2'))
    normalize_transactions['storenumber'] = normalize_transactions['receiptId'].apply(lambda x:x.get('storeNumber'))
    normalize_transactions['division'] = normalize_transactions['receiptId'].apply(lambda x:x.get('divisionNumber'))
    normalize_transactions['transdate'] = normalize_transactions['receiptId'].apply(lambda x:x.get('transactionDate'))
    normalize_transactions['transactiontime'] = pd.to_datetime(normalize_transactions['transactionTime'])
    normalize_transactions['transactionhour'] = normalize_transactions['transactiontime'].dt.hour
    normalize_transactions['transactionkey'] = normalize_transactions['transactionid']  + '_' + normalize_transactions['transactiontime'].apply(lambda x:x.strftime("%Y%m%d"))
    normalize_transactions['datekey'] = normalize_transactions['transactiontime'].apply(lambda x:x.strftime("%Y%m%d"))
    normalize_transactions['datetransformation'] = normalize_transactions['transactiontime'].apply(lambda x : (x-datetime.datetime(1970,1,1)).total_seconds()).astype(int)
    normalize_transactions['datetransformation'] = normalize_transactions['datetransformation'].apply(str)
    normalize_transactions['mergekey'] = normalize_transactions['transactionid'] + '_' + normalize_transactions['datetransformation']
    normalize_transactions.drop(columns=['address', 'items', 'tax', 'tenders','receiptId'],inplace=True)
    normalize_transactions.columns = map(str.lower, normalize_transactions.columns)

    #generate csv for user to upload to other reporting tools
    normalize_transactions.to_csv('receipt_dataframe_' + extract_date_time.strftime('%Y-%m-%d') + '.csv')

    return normalize_transactions



def transform_items(detailed_transactions):

    #Add logic to allow user to login to postgreSQL and load transactions to a table
    all_items = json_normalize(data=detailed_transactions, record_path=['items'], meta=['receiptId','transactionTime'],errors='ignore')

    all_items['productdescription'] = all_items['detail'].apply(lambda x: x.get('description'))
    all_items['extractdate'] = extract_date_time
    #update usedcoupon logic
    all_items['usedcoupon'] = np.where(all_items['priceModifiers'].str.len() > 1, True, False)
    all_items['transactionid'] = all_items['receiptId'].apply(lambda x:x.get('transactionId'))
    all_items['transdate'] = all_items['receiptId'].apply(lambda x:x.get('transactionDate'))
    all_items['transactiontime'] = pd.to_datetime(all_items['transactionTime'])
    all_items['transactionhour'] = all_items['transactiontime'].dt.hour
    all_items['datekey'] = all_items['transactiontime'].apply(lambda x:x.strftime("%Y%m%d"))
    all_items['baseupc'] = all_items['baseUpc'].apply(str)
    all_items['uniquekey'] = all_items['transactionid']  + '_' + all_items['datekey'] + '_' + all_items['baseUpc']
    all_items['datetranskey'] = all_items['transactiontime'].apply(lambda x : (x-datetime.datetime(1970,1,1)).total_seconds()).astype(int)
    all_items['datetranskey'] = all_items['datetranskey'].apply(str)
    all_items['mergekey'] = all_items['transactionid'] + '_' + all_items['datetranskey']

    all_items.columns = map(str.lower, all_items.columns)
    all_items.drop(columns=['detail', 'pricemodifiers','receiptid'],inplace=True)


    all_items.to_csv('items_dataframe_' + extract_date_time.strftime('%Y-%m-%d') + '.csv')

    return all_items


def join_dataframes(left_frame, right_frame):

    merged_df = pd.merge(left_frame, right_frame, how='inner', on='mergekey')
    merged_df.to_csv('merged_transactions_' + extract_date_time.strftime('%Y-%m-%d') + '.csv')


    return merged_df


def get_receipt_ids(receipt_json_list):
    receipt_df = pd.DataFrame(receipt_json_list)
    receipt_df[['divisionNumber', 'storeNumber', 'terminalNumber', 'transactionId']] = receipt_df[['divisionNumber', 'storeNumber', 'terminalNumber','transactionId']].astype(int)
    receipt_df[['divisionNumber', 'storeNumber', 'terminalNumber', 'transactionId']] = receipt_df[['divisionNumber', 'storeNumber', 'terminalNumber','transactionId']].astype(str)
    receipt_df['loadmergekey'] = receipt_df['divisionNumber'] + '_' + receipt_df['storeNumber'] + '_' + receipt_df['terminalNumber'] + '_' + receipt_df['transactionId'] + '_' + receipt_df['transactionDate']
    receipts = [receipt for receipt in receipt_df['loadmergekey']]

    return receipts

