import fitbit
import datetime
import json
from auth import main
import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/<calories>')
def index(calories: int):
    try:
        int(calories)
    except ValueError:
        return "Calories must be an integer", 400
    log_calories(calories)
    return "Success!", 200


# Your Fitbit API credentials
CLIENT_ID = os.environ.get('FITBIT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('FITBIT_CLIENT_SECRET')

def get_client():
    # Get the access and refresh tokens
    with open('data/fitbit_token.json', 'r') as f:
        data = json.load(f)
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET,
                            access_token=access_token,
                            refresh_token=refresh_token)
        return client

# Function to log calories
def log_calories(calories, date=None):
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    client = get_client()

    try:
        url = "{0}/{1}/user/-/{resource}/{log_id}.json".format(
            *client._get_common_args(),
            resource='foods',
            log_id="log"
        )
        response = client.make_request(url, data={
            "mealTypeId": 7,  # 7 is the mealTypeId for Quick Calories
            "foodName": "Quick Calories",
            "unitId": 304,  # 304 is the unitId for 'calories'
            "calories": calories,
            "amount": 1,
            "date": datetime.datetime.now().strftime("%Y-%m-%d")
        })
        print(response)
        print(f"Successfully logged {calories} calories for {date}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    Thread(target=main, daemon=True).start()
    app.run("0.0.0.0", debug=True, threaded=False)