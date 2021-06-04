import json, time, requests, conf # importing all the required packages

from boltiot import Bolt, Email, Sms # importing all the required packages

print ("Please enter the cryptocurrency you want to get updates for : ")
print ("Please note that we are using symbols as mentioned on cryptocompare Ex BTC, ETH, DOGE, etc. Uppercases only.")
cry = input () # stores the type of crypto currency the user wants to be updated on
print ()

print ("Please enter the currency you want the values in : ")
print ("Please note that we are using symbols as mentioned on cryptocompare Ex USD, JPY, EUR, INR, etc. Uppercases only.")
cur = input () # stores the currency the user makes his transactions in
print ()

def crypto_price(): # function to get the current price of 'cry' in 'cur' from cryptocompare
    URL = "https://min-api.cryptocompare.com/data/price?fsym="+cry+"&tsyms="+cur
    response = requests.request("GET", URL)
    response = json.loads(response.text)
    current_price = response[cur]
    return current_price

starting_price = crypto_price() # initial when the function is called for the very first time
print ("Starting price is " + str(starting_price))
print ()

min_selling_price = input ("Enter the min value you would want to be alerted at : ")
max_selling_price = input ("Enter the max value you would want to be alerted at : ")
print ()

print ("How would you like to be alerted? Please enter 1 for yes and 0 for no.")
tel = input ("Using telegram?")
em = input ("Using email?")
mes = input ("Using message?")
print ("Remember these alerts will be sent to details mentioned in the conf.py")
print ()

mybolt = Bolt(conf.API_KEY, conf.DEVICE_ID) # creating an object to access bolt

alert = 0 # to store which type of alert
m="" # helps in printing appropriate messages

while True: # infinite loop
    current_value = crypto_price() # function call
    print ("Current value of "+cry+" in "+cur+" is: " + str(current_value))
    print ("Note: Left(1) LED signify value is currently greater than the starting value and Right(2) vice versa. Both ON means the value remains unchanged")
    print ()

    if current_value > starting_price: # BULL
        print ("Value is increasing")
        mybolt.digitalWrite('1', 'HIGH') # LED1 ON
        mybolt.digitalWrite('2', 'LOW') # LED2 OFF
    elif current_value < starting_price: # BEAR
        print ("Value is decreasing")
        mybolt.digitalWrite('2', 'HIGH') # LED2 OFF
        mybolt.digitalWrite('1', 'LOW') # LED1 ON
    else :
        print ("Value is stable")
        mybolt.digitalWrite('1', 'HIGH') # LED1 ON
        mybolt.digitalWrite('2', 'HIGH') # LED2 ON
    print ()

    if current_value > float(max_selling_price): # Upper bound check
        alert = 1
        m= "greater"
        print ("Greater than max value ")
        mybolt.digitalWrite('0', 'HIGH') # buzzer on
    elif current_value < float(min_selling_price): # Lower bound check
        alert = 2
        m="lesser"
        print ("Lesser than min value")
        mybolt.digitalWrite('0', 'HIGH') #buzzer on
    print ()
    time.sleep(5)
    mybolt.digitalWrite("0","LOW") # buzzer of after 5s

    if float(tel) > 0 and alert > 0: # if telegram alert is on
        
        def send_telegram_message(message): # function to call the bot to send a message to the channel
            url = "https://api.telegram.org/" + conf.telegram_bot_id + "/sendMessage" # command to the bot
            data = {"chat_id": conf.telegram_chat_id,"text": message} # data of the channel and the message to send
            try:
                response = requests.request("POST",url,params=data) 
                print ("This is the Telegram URL")
                print (url)
                print ("This is the Telegram response")
                print (response.text)
                telegram_data = json.loads(response.text)
                return telegram_data["ok"]
            except Exception as e:
                print ("An error occurred in sending the alert message via Telegram")
                print (e)
            return False

        message = "Alert! Current value of "+cry+" is "+m+" than the defined range. The current value of "+cry+" is " + str(current_value)+" "+cur # message to be posted by the bot
        telegram_status = send_telegram_message(message)
        print ("This is the Telegram status:", telegram_status)
        print ()

    if float(mes) > 0 and float(alert) > 0: # if sms alert is on

        sms = Sms(conf.SID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER) # object creation, takes data from the conf.py

        try: 
            print ("Making request to Twilio to send a SMS")
            response = sms.send_sms("Alert! Current value of "+cry+" is "+m+" than the range defined. The current value of" +cry+" is " + str(current_value)+" "+cur) # sms message
            print ("Response received from Twilio is: " + str(response))
            print ("Status of SMS at Twilio is :" + str(response.status))
        except Exception as e: 
            print ("Error occured: Below are the details")
            print (e)
        print ()

    if float(em) > 0 and float(alert) > 0: # if email alert is on
       
        mailer = Email(conf.MAILGUN_API_KEY, conf.SANDBOX_URL, conf.SENDER_EMAIL, conf.RECIPIENT_EMAIL) # object creation, takes data from the conf.py
       
        try: 
            print ("Making request to Mailgun to send an email")
            response = mailer.send_email("Alert", "Current value of "+cry+" is "+m+" than the range defined. The current value of "+cry+" is " + str(current_value)+" "+cur) # email message (title, content)
            response_text = json.loads(response.text)
            print ("Response received from Mailgun is: " + str(response_text['message']))
        except Exception as e: 
            print ("Error occured: Below are the details")
            print (e)
        print ()

    time.sleep(30) # repeats the infinite while loop after 30s
    print ()
    mybolt.digitalWrite('1', 'LOW') # LED1 OFF
    mybolt.digitalWrite('2', 'LOW') # LED2 OFF

