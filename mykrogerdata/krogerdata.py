import requests, json,sys, os, glob, time, datetime
import urllib.request
import pandas as pd
from pandas.io.json import json_normalize
import getpass
import krogeruseragents as ua
import datatransformations as dt
import config as cfg
import random as rand


#add python notebook to main dir

def get_nutrition_info(item_upcs):
    nutrition_info = []
    macro_n = []
    micro_n = []
    with requests.Session() as sess:
        for upc in item_upcs:
            try:
                nutrition_url = f"https://www.kroger.com/products/api/nutrition/details/{upc}"
                nutrition_request = sess.get(nutrition_url, headers=ua.headers)
                nutrition_json = nutrition_request.json()
                macro_nutrients = json_normalize(nutrition_json[0],record_path=[['nutritionFacts','macronutrients']], meta=['upc'],errors='ignore')
                micro_nutrients = json_normalize(nutrition_json[0],record_path=[['nutritionFacts','micronutrients']], meta=['upc'],errors='ignore')
                nutrition_info.append(nutrition_json[0])
                macro_n.append(macro_nutrients)
                micro_n.append(micro_nutrients)
            except:
                pass

    nutrition_df = pd.DataFrame(nutrition_info)
    macro_df = pd.DataFrame(macro_n)
    micro_df = pd.DataFrame(micro_n)



    return nutrition_df

def get_upcs(item_upcs):
    
    
    return upc_list

def get_coupons(div=cfg.division['division_num'], store=cfg.store_number['store_num']):
    coupons_url = f"https://www.kroger.com/cl/api/coupons?couponsCountPerLoad=1000&sortType=relevance&newCoupons=false&hideClickListOnlyOffer=false&divisionId={div}&storeId={store}"
    store_header = ua.headers
    store_header['store-id'] = store
    store_header['division-id'] = div
    with requests.Session() as sess:
        coupon_request = sess.get(coupons_url,headers=ua.headers)
        coupon_json = coupon_request.json()
        coupon_df = pd.DataFrame(coupon_json['data']['coupons'])
        coupon_df = coupon_df.transpose()
    return coupon_df

def load_coupons():
    available_coupons = get_coupons()
    login_session = single_login()

    try:
        #try to get all items previously purchased
        all_items = concat_all_csv()
    except:
        #if items can't be found, run script to get most recent products
        get_prices_of_most_frequent_products()
        all_items = concat_all_csv()


    brand_names = list(set(available_coupons['brandName']).intersection(set(all_items['brandName'])))
    coupon_count = 0

    try:
        for index, row in available_coupons[available_coupons['brandName'].isin(brand_names)].iterrows():
            coupon_number = row['krogerCouponNumber']
            coupon_id = row['id']
            slug = row['slug']
            post_url = f'https://www.kroger.com/cl/api/myLoyaltyCard/coupons?couponId={coupon_id}&krogerCouponNumber={coupon_number}&slug={slug}'
            payl = json.dumps({'couponId' : coupon_id})
            login_session.post(post_url, headers=ua.headers,data=payl.encode('UTF-8'))
            coupon_count += 1
    except:
        pass

    
    print(f"Number of coupons loaded to card successfully: {coupon_count}")

    #search for most recent item extract in folder 
    #Compare available coupons against previously purchased items and autoload those coupons to the customers 
def get_coupons_loaded_to_card():
    #sort values by coupons that are going to expire soon 
    return coupons_loaded_to_card

def get_item_locations(item_upcs, div=cfg.division['division_num'], store=cfg.store_number['store_num']):
    #build configuartion file automatically that stores division and store data
    #return closest location when browsing otherwise pass parameters
    #Return csv file of all locations for recently bought products
    #https://www.kroger.com/products/api/locations/0000000004011
    locations_data = []
    store_header = ua.headers
    store_header['store-id'] = store
    store_header['division-id'] = div
    with requests.Session() as sess:
        for upc in item_upcs:
            try:
                location_url = f'https://www.kroger.com/products/api/locations/{upc}'
                location_request = sess.get(location_url, headers=ua.headers)
                location_json = location_request.json()
                print(location_json)
                locations_data.append(location_json)
            except:
                pass
        
        locations_df = pd.DataFrame(locations_data)

    return locations_df

def get_prices_of_most_frequent_products(div=cfg.division['division_num'], store=cfg.store_number['store_num']):
    #function to return the prices of the most frequently purchased items...
    product_api = 'https://www.kroger.com/products/api/products/details'
    item_prices = []
    item_files = glob.glob('items_dataframe*.csv')
    dfs = [pd.read_csv(f,sep=",",dtype=({'baseupc':str})) for f in item_files]
    item_upcs = pd.concat(dfs,ignore_index=True)
    store_header = ua.headers
    store_header['store-id'] = store
    store_header['division-id'] = div
    list_of_upcs = item_upcs['baseupc'].unique()
    extract_date_time = datetime.datetime.now().replace(microsecond=0)

    with requests.Session() as sess:
        print("Pulling the latest prices for the products in your most visited store!")
        for upc in list_of_upcs:
            try:
                price_payload = json.dumps({'upcs':[upc], 'filterBadProducts':False})
                price_request = sess.post(product_api, headers=store_header,data=price_payload.encode('UTF-8'),timeout=20)
                price = price_request.json()
                print(price)
                item_prices.append(price)
            except:
                pass
    single_products = []
    for product in item_prices:
        one_product = product['products']
        if one_product == None:
            pass
        else:
            single_products.extend(one_product)



    
    recent_df_prices = pd.DataFrame(single_products)
    recent_df_prices['extractdate'] = extract_date_time
    recent_df_prices.to_csv('all_item_prices_'+ str(extract_date_time) + '.csv')



    return recent_df_prices


def load_most_recent_receipt_csv():
    path = os.getcwd()
    extension = 'csv'
    file_name = 'receipt_dataframe'
    os.chdir(path)
    all_files = [i for i in glob.glob('*.{}'.format(extension))]
    wanted_files = [file for file in all_files if file_name in file]
    
    date_list = []
    for x in wanted_files:
        date = x.split('_')[-1].split('.')[0]
        date_list.append(date)
    sorted_date = sorted(date_list)
    max_file = sorted_date[-1]
    
    
    recent_df = pd.read_csv(file_name + '_' + max_file + '.csv')
    recent_df[['divisionnumber', 'storenumber', 'terminalnumber', 'transactionid', 'transactiondate']] = recent_df[['divisionnumber', 'storenumber', 'terminalnumber', 'transactionid', 'transactiondate']].astype(str)
    recent_df['loadmergekey'] = recent_df['divisionnumber'] + '_' +  recent_df['storenumber'] + '_' + recent_df['terminalnumber'] + '_' + recent_df['transactionid'] + '_' + recent_df['transactiondate']
    recent_df.sort_values(by='transactiontime',ascending=False,inplace=True)
    max_load_key = recent_df.loc[0]['loadmergekey']
    
    return max_load_key


def single_login():
    kroger_login_url = "https://www.kroger.com/signin?redirectUrl=/"
    sign_in = 'https://www.kroger.com/auth/api/sign-in' #sign-in API


    with requests.Session() as sess:
        sess.get('https://www.kroger.com',headers=ua.headers)
        time.sleep(round(rand.uniform(10.5,15.5),3))
        sess.get(kroger_login_url,headers=ua.headers)
        time.sleep(round(rand.uniform(10.5,15.5),3))
        login_response = {'statusCode':000}
        login_attempts = 3
        while login_response['statusCode'] != 200 and login_attempts > 0:
            try:
                username= input('What is your email address for your Kroger account? ')
                password = getpass.getpass('What is your password? (Note: password will not appear in the console...) ')
                login_payload = json.dumps({"email": username,"password": password, "rememberMe":False})
                ua.headers['cookie'] = sess.cookies()
                print(ua.headers)
                login_post = sess.post(sign_in, headers=ua.headers, data=login_payload.encode('UTF-8'))
                login_response = login_post.json()
            except:
                while login_attempts > 0:
                    login_post = sess.post(sign_in, headers=ua.headers, data=login_payload.encode('UTF-8'))
                    login_attempts -= 1
                    print(ua.headers)
                    print("Post request failed...please try again \n")
                
            if login_response['statusCode'] != 200:
                if login_attempts == 1:
                    print("Exiting program...")
                    sys.exit()
                else:
                    login_attempts -= 1
                    try:
                        print(f"{login_response['statusCode']} - {login_response['statusMessage']}")
                        print(f"{login_attempts} login attempt(s) left!")
                    except:
                        print("Exiting program. Please try again later.")
            else:
                print("Login successful!")
    return sess


def concat_all_csv():

    item_files = glob.glob('all_item_prices_*.csv')
    dfs = [pd.read_csv(f,sep=",",dtype=({'baseupc':str})) for f in item_files]
    concat_df = pd.concat(dfs,ignore_index=True)
    return concat_df


def items_csv_concat():
    item_list = glob.glob('items_dataframe_*.csv')
    dfs = [pd.read_csv(f,sep=",", dtype=({'baseupc':str})) for f in item_list]
    items_df = pd.concat(dfs,ignore_index=True)

    return items_df

def receipts_csv_concat():
    receipts_csv = glob.glob('receipt_dataframe_*.csv')
    dfs = [pd.read_csv(f,sep=",",dtype=({'baseupc':str})) for f in receipts_csv]
    receipts_df = pd.concat(dfs,ignore_index=True)

    return receipts_df