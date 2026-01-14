from flask import Flask,request, url_for, redirect, render_template
import pickle
import numpy as np
import pandas as pd
# import mysql.connector as connector
import psycopg2
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

# def load_model():
#     with open("finalized_model.sav", "rb") as f:
#         return pickle.load(f)  # Model loads only per request

def load_model():
    from keras.models import load_model
    model = load_model("model1.keras")
    return model

def strategy(predicted, original):
    if original < predicted:
        return 'BUY'
    else:
        return 'SELL'

with open("minmax_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

#model=pickle.load(open('finalized_model.sav','rb'))

db = 'postgresql://stock_price_g9q6_user:NxjC5lOyzg5HJftmjj49JUpYxLquARBl@dpg-d59ul99r0fns7381saug-a.singapore-postgres.render.com/stock_price_g9q6'

@app.route('/')
def home():
    conn = psycopg2.connect(db)
    conn.autocommit = True
    my_cursor = conn.cursor()
    my_cursor.execute('Select * from price_sentiment')
    result = my_cursor.fetchall()
    data = pd.DataFrame(result, columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock_Splits', 'Score', 'Positive' , 'Negative', 'Neutral', 'Total_Sentiment'])
    data.set_index('Date', drop=True,inplace=True)
    data.sort_index(inplace=True)
    data_model = data.drop(['Open', 'High', 'Low', 'Dividends', 'Stock_Splits', 'Score', 'Positive' , 'Negative', 'Neutral'], axis=1)
    #scaler = MinMaxScaler(feature_range=(0,1))
    data_scaled = scaler.fit_transform(data_model.iloc[-14:,])
    input_data = data_scaled[-14: ,].reshape(1,14,3)
    model = load_model()
    prediction = model.predict(input_data)

    arr = [prediction.flatten()[0],  prediction.flatten()[0], prediction.flatten()[0]]

    arr = np.array(arr).reshape(1,-1)

    y_pred_future = scaler.inverse_transform(arr)[0][0]
    ori = data['Close'][-1]
    conn.close()
    my_cursor.close()

    labels = data.index[-14:].tolist()
    values = data['Close'][-14:].tolist()

    values_pos = int(data['Positive'][-14:].sum())
    values_neg = int(data['Negative'][-14:].sum())
    values_neu = int(data['Neutral'][-14:].sum())

    n_past = 14

    traindata = []

    for i in range(len(data_model)-n_past*2+1 , len(data_model)-n_past+1):
        traindata.append(scaler.transform(data_model.iloc[i:i+n_past,:]))

    prediction1 = model.predict(np.array(traindata).reshape(14,14,3))
    prediction1 = prediction1.flatten()

    arr= []
    for i in range(0, len(prediction1)):
        arr.append([prediction1[i], prediction1[i], prediction1[i]])

    predicted_price = scaler.inverse_transform(np.array(arr).reshape( 14,3))
    predicted_price = predicted_price[:,0].tolist()

    strat = strategy(y_pred_future, ori)

    return render_template("app.html", prediction_value = round(y_pred_future,2), original_value = ori, labels_price = labels , values_price = values, 
                           predicted_price = predicted_price, strat = strat, values_sentiment = [values_pos,values_neg,values_neu])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')