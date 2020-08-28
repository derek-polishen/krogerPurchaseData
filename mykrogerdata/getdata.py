import datatransformations as dts
import krogerlogin as kl 
import pandas as pd 
import seaborn as sns
import krogerdata as kd
import matplotlib.pyplot as plttrans
import matplotlib.pyplot as plt


get_data = kl.session_sign_in()
#get_data = kl.kroger_sign_in()
df1 = dts.transform_receipt_data(get_data)
df2 = dts.transform_items(get_data)
df3 = dts.join_dataframes(df1,df2)
#kd.load_coupons()

