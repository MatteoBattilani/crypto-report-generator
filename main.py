import json
import datetime
import requests
import time


# Creo la classe che definirà l'oggetto Bot che eseguirà le varie operazioni
class Bot:

    def __init__(self):
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.params = {
            'start': '1',
            'limit': '5000',
            'convert': 'USD'
        }
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '39d8bd96-0d68-449e-a2d2-8c4147e76dd5'
        }

    # Metodo che fa partire la richiesta alle APIs di CoinMarketCap per ottenere dati aggiornati sulle criptovalute
    def fetchCurrenciesData(self):
        r = requests.get(url=self.url, headers=self.headers, params=self.params).json()
        return r['data']


# Genero l'oggetto della classe Bot
objectBot = Bot()

# Ciclo infinito per mantenere il programma avviato:
while(1):

    # Assegno ad una variabile i dati di tutte le criptovalute
    currencies = objectBot.fetchCurrenciesData()

    # Identifico la criptovaluta con il volume maggiore delle ultime 24 ore e la salvo dentro bestVolCurrency
    bestVolume = 0
    bestVolCurrency = {}
    for currency in currencies:
        if currency["quote"]["USD"]["volume_24h"] > bestVolume:
            bestVolume = currency["quote"]["USD"]["volume_24h"]
            bestVolCurrency = currency


    # Identifico le 10 migliori criptovalute per incremento in percentuale delle ultime 24 ore e le inserisco in listTopCurrencies
    listTopCurrencies = []
    bestPercentChange = 0
    bestPercentChangeCurrency = 0
    counter1 = 0
    while counter1 < 10:
        for currency in currencies:
            if currency in listTopCurrencies:
                continue
            if currency["quote"]["USD"]["percent_change_24h"] > bestPercentChange:
                bestPercentChange = currency["quote"]["USD"]["percent_change_24h"]
                bestPercentChangeCurrency = currency
        listTopCurrencies.append(bestPercentChangeCurrency)
        bestPercentChange = 0
        counter1 = counter1 + 1


    # Identifico le 10 peggiori criptovalute per incremento in percentuale delle ultime 24 ore e le inserisco in listWorstCurrencies
    listWorstCurrencies = []
    worstPercentChange = listTopCurrencies[0]["quote"]["USD"]["percent_change_24h"]
    worstPercentChangeCurrency = 0
    counter2 = 0
    while counter2 < 10:
        for currency in currencies:
            if currency in listWorstCurrencies:
                continue
            if currency["quote"]["USD"]["percent_change_24h"] < worstPercentChange:
                worstPercentChange = currency["quote"]["USD"]["percent_change_24h"]
                worstPercentChangeCurrency = currency
        listWorstCurrencies.append(worstPercentChangeCurrency)
        worstPercentChange = listTopCurrencies[0]["quote"]["USD"]["percent_change_24h"]
        counter2 = counter2 + 1


    #Calcolo la quantità di denaro necessaria per acquistare un'unità di ciascuna delle prime 20 criptovalute (ordinate per capitalizzazione):
    listTop20MarketCap = []
    requiredMoney = 0
    for currency in currencies:
        if currency["cmc_rank"] <= 20:
            listTop20MarketCap.append(currency)
            requiredMoney = requiredMoney + currency["quote"]["USD"]["price"]


    # Calcolo denaro necessario per acquistare una unità di tutte le criptovalute il cui volume delle ultime 24 ore sia superiore a 76.000.000$
    limit = 76000000
    requiredMoney2 = 0
    listCurrOverLimitName = []
    listCurrOverLimitPrice = []
    listCurrOverLimitVolume = []
    for currency in currencies:
        if currency["quote"]["USD"]["volume_24h"] > limit:
            listCurrOverLimitName.append(currency["name"])
            listCurrOverLimitPrice.append(currency["quote"]["USD"]["price"])
            listCurrOverLimitVolume.append(currency["quote"]["USD"]["volume_24h"])
            requiredMoney2 = requiredMoney2 + currency["quote"]["USD"]["price"]

    # Raccolgo le liste delle criptovalute in un unico dizionario per comodità e per rendere dinamico il numero delle criptovalute che vi apparterranno
    dictCurrenciesOverLimit = {'name': listCurrOverLimitName,
                               'volume': listCurrOverLimitVolume,
                               'price': listCurrOverLimitPrice}


    # Calcolo la percentuale di guadagno o perdita che avrei realizzato se avessi comprato una unità di ciascuna delle prime 20 criptovalute il giorno prima (ipotizzando che la classifca non sia cambiata)
    yesterdayBalance = 0
    # requiredMoney è la variabile che contiene il valore del denaro necessario a comprare le prime 20 criptovalute al PREZZO DI OGGI
    todayBalance = requiredMoney

    for currency in listTop20MarketCap:
        # Calcolo il valore in percentuale:
        percentage = (100 + (currency["quote"]["USD"]["percent_change_24h"]))
        yesterdayCurrencyPrice = (currency["quote"]["USD"]["price"] * 100) / percentage
        # La variabile "yesterdayBalance" conterrà il valore del denaro necessario a comprare le prime 20 criptovalute al PREZZO DI IERI
        yesterdayBalance = yesterdayBalance + (yesterdayCurrencyPrice)

    if yesterdayBalance < todayBalance:
        percentBalance = ((todayBalance - (yesterdayBalance)) / todayBalance) * 100
        totalBalance = "Se ieri avessi comprato un'unita' per ognuna delle prime 20 criptovalute per capitalizzazione di mercato, oggi avrei guadagnato il " + str(percentBalance) + "%, ovvero: " + str(todayBalance - yesterdayBalance) + "$. Avrei, quindi, in totale: " + str(todayBalance) + "$"
    else:
        percentBalance = ((yesterdayBalance - (todayBalance)) / yesterdayBalance) * 100
        totalBalance = "Se ieri avessi comprato un'unita' per ognuna delle prime 20 criptovalute per capitalizzazione di mercato, oggi avrei perso il " + str(percentBalance) + "%, ovvero: " + str(yesterdayBalance - todayBalance) + "$. Avrei, quindi, in totale: " + str(todayBalance) + "$"


   # Inserisco i dati per il report giornaliero all'interno del dizionario "data"

    data = {'point1': {'best_volume_currency': {
        'name': bestVolCurrency["name"],
        'symbol': bestVolCurrency["symbol"],
        'volume': bestVolCurrency["quote"]["USD"]["volume_24h"],
        'additional_currency_info': bestVolCurrency
                                                }
                      },
        'point2': {'top_currencies_last24h': listTopCurrencies,
                   'worst_currencies_last24h': listWorstCurrencies
                   },
        'point3': {'top_currencies_marketcap': listTop20MarketCap,
                   'required_money': requiredMoney
                   },
        'point4': {'curr_over_76million_volume': dictCurrenciesOverLimit,
                   'required_money': requiredMoney2},
        'point5': {'percent_balance': percentBalance,
                   'additional_info': totalBalance}
    }



    # Genero un file json (come nome avrà la data di oggi) e, al suo interno, inserisco i dati del dizionario "data"
    fileName = str(datetime.date.today())
    with open(fileName + ".json", "w") as outfile:
        json.dump(data, outfile, indent=4)

    print("Ho appena prodotto il report giornaliero. Il prossimo sarà prodotto tra 24 ore.")

    # Routine che permetterà che il ciclo while venga eseguito ogni 24 ore
    hours = 24
    minutes = 60 * hours
    seconds = 60 * minutes
    time.sleep(seconds)
