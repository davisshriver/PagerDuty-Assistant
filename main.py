from slack_sdk import WebClient
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slack_user_helper import SlackUserHelper

app = Flask(__name__)

env_path = Path('.') / '.env' 
load_dotenv(dotenv_path=env_path)

slack_token = os.environ['SLACK_TOKEN']
client = WebClient(slack_token)

pagerduty_api_token = os.environ['PAGERDUTY_TOKEN']
schedule_id = os.environ['SCHEDULE_ID']

_userHelper = SlackUserHelper(slack_token, pagerduty_api_token, schedule_id)

# @app.route('/my-email', methods=['POST'])
# def my_email():
#     data = request.form
#     user_id = data.get('user_id')
#     channel_id = data.get('channel_id')
    
#     userEmail = _userHelper.get_user_email(user_id)

#     if userEmail is not None:
#         message_text = "Your email is " + userEmail
#         client.chat_postEphemeral(channel= channel_id, user=user_id, text=message_text)
#         return Response(), 200
#     else:
#         message_text = "Unable to retrieve the user's email."
#         client.chat_postEphemeral(channel= channel_id, user=user_id, text=message_text)
#         return Response(), 500
    
@app.route('/my-id', methods=['POST'])
def my_id():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    pg_id = _userHelper.get_pagerduty_id(user_id)
    
    if pg_id != None:
        message_text = "Your PgId is " + pg_id
        client.chat_postEphemeral(channel= channel_id, user=user_id, text=message_text)
        return Response(), 200
    else:
        message_text = "Failed to find a PagerDuty Id for your slack account!"
        client.chat_postEphemeral(channel= channel_id, user=user_id, text=message_text)
        return Response(), 500
    
@app.route('/my-next-shift', methods=['POST'])
def my_next_shift():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    pg_id = _userHelper.get_pagerduty_id(user_id)
    

    
    return Response(), 200

@app.route('/pagerduty-list', methods=['POST'])
def pagerduty_list():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    
    schedules = _userHelper.get_oncall_schedules()
    
    header = "Here is the on-call schedule for the next 3 months:\n"

    formatted_message = _userHelper.format_schedule_message(schedules)
    
    client.chat_postEphemeral(channel= channel_id, user=user_id, text=header + "\n" + formatted_message)

    return Response(), 200
    
if __name__ == "__main__":
    # print(_userHelper.get_oncall_schedules())
    app.run(debug=True, port=80)
    