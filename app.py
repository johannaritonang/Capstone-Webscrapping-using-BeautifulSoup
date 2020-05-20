from flask import Flask, render_template
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import dateparser

app = Flask(__name__)

def scrap(url):
    url_get = requests.get('https://monexnews.com/kurs-valuta-asing.htm?kurs=JPY&searchdatefrom=01-01-2019&searchdateto=31-12-2019')
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    table = soup.find('table', attrs={'class':'table'})
    tr = table.find_all('tr')
    
    temp = [] #initiating a tuple
    
    for i in range(1, len(tr)):
        row = table.find_all('tr')[i]
        #use the key to take information here
        #name_of_object = row.find_all(...)[0].text
        
        #get date
        tanggal = row.find_all('td')[0].text
        tanggal = tanggal.strip() #for removing the excess whitespace
        
        #get ask
        jual = row.find_all('td')[1].text
        jual = jual.strip() #for removing the excess whitespace
        
        #get bid
        beli = row.find_all('td')[2].text
        beli = beli.strip() #for removing the excess whitespace
        
        temp.append((tanggal,jual,beli)) #append the needed information
    
        temp2 = temp[::-1] #remove the header
    
    jpy = pd.DataFrame(temp2, columns = ('tanggal','jual','beli'))#creating the dataframe
    #data wranggling -  try to change the data type to right data type
    jpy['jual'] = jpy['jual'].str.replace(',', '.')
    jpy['beli'] = jpy['beli'].str.replace(',', '.')
    jpy[['jual','beli']] = jpy[['jual','beli']].astype('float64')
    jpy['tanggal'] = jpy['tanggal'].apply(lambda x: dateparser.parse(x))
    jpy['period']= jpy['tanggal'].dt.to_period('M')
    jpymean = jpy[['period','jual','beli']].groupby(['period']).mean().round(2)
    #end of data wranggling

    return jpymean

@app.route("/")
def index():
    df = scrap('https://monexnews.com/kurs-valuta-asing.htm?kurs=JPY&searchdatefrom=01-01-2019&searchdateto=31-12-2019') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()