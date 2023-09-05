import json
import asyncio
import requests
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
verification_token = os.environ['VERIFICATION_TOKEN']
client = WebClient(slack_token)

pagerduty_api_token = os.environ['PAGERDUTY_TOKEN']
schedule_id = os.environ['SCHEDULE_ID']

_helper = SlackUserHelper(slack_token, pagerduty_api_token, schedule_id)

modal_payload = {
    "type": "modal",
    "callback_id": "modal-identifier",
    "title": {
        "type": "plain_text",
        "text": "Schedule Swap"
    },
    "blocks": [
        {
            "type": "section",
            "block_id": "section-identifier-1",
            "text": {
                "type": "mrkdwn",
                "text": "Current Schedule Start Date"
            },
            "accessory": {
                "type": "datepicker",
                "initial_date": "2023-09-01",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date"
                },
                "action_id": "start_date_1"
            }
        },
        {
            "type": "section",
            "block_id": "section-identifier-8",
            "text": {
                "type": "mrkdwn",
                "text": "Current Schedule Start Time"
            },
            "accessory": {
                "type": "timepicker",
                "initial_time": "08:00",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a time"
                },
                "action_id": "start_time_1"
            }
        },
        {
            "type": "section",
            "block_id": "section-identifier-2",
            "text": {
                "type": "mrkdwn",
                "text": "Current Schedule End Date"
            },
            "accessory": {
                "type": "datepicker",
                "initial_date": "2023-09-30",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date"
                },
                "action_id": "end_date_1"
            }
        },
        {
            "type": "section",
            "block_id": "section-identifier-9",
            "text": {
                "type": "mrkdwn",
                "text": "Current Schedule End Time"
            },
            "accessory": {
                "type": "timepicker",
                "initial_time": "17:00",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a time"
                },
                "action_id": "end_time_1"
            }
        },
        {
            "type": "section",
            "block_id": "section-identifier-6",
            "text": {
                "type": "mrkdwn",
                "text": "User to Swap With"
            },
            "accessory": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a user"
                },
                "action_id": "selected_user_2"
            }
        },
        {
            "type": "section",
            "block_id": "section-identifier-4",
            "text": {
                "type": "mrkdwn",
                "text": "Desired Schedule Start Date"
            },
            "accessory": {
                "type": "datepicker",
                "initial_date": "2023-09-01",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date"
                },
                "action_id": "start_date_2"
            }
        },
        {
            "type": "section",
            "block_id": "section-identifier-10",
            "text": {
                "type": "mrkdwn",
                "text": "Desired Schedule Start Time"
            },
            "accessory": {
                "type": "timepicker",
                "initial_time": "08:00",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a time"
                },
                "action_id": "start_time_2"
            }
        },
        {
            "type": "section",
            "block_id": "section-identifier-5",
            "text": {
                "type": "mrkdwn",
                "text": "Desired Schedule End Date"
            },
            "accessory": {
                "type": "datepicker",
                "initial_date": "2023-09-30",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date"
                },
                "action_id": "end_date_2"
            }
        },
        {
            "type": "section",
            "block_id": "section-identifier-11",
            "text": {
                "type": "mrkdwn",
                "text": "Desired Schedule End Time"
            },
            "accessory": {
                "type": "timepicker",
                "initial_time": "17:00",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a time"
                },
                "action_id": "end_time_2"
            }
        },
    ],
    "close": {
        "type": "plain_text",
        "text": "Cancel"
    },
    "submit": {
        "type": "plain_text",
        "text": "Submit"
    }
    
}

@app.route('/pagerduty-id', methods=['POST'])
def my_id():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    token = data.get('token')
    pg_id = _helper.get_pagerduty_id(user_id)
    
    # Authorization Check
    if not _helper.ValidateOrigin(token, verification_token):
        message_text = "Failed to validate request, talk to system administrator!"
        client.chat_postEphemeral(channel= channel_id, user=user_id, text=message_text)
        return Response(), 401
    
    if pg_id != None:
        message_text = "Your Pagerduty Id is: " + pg_id
        client.chat_postEphemeral(channel= channel_id, user=user_id, text=message_text)
        return Response(), 200
    else:
        message_text = "Failed to find a PagerDuty Id for your slack account!"
        client.chat_postEphemeral(channel= channel_id, user=user_id, text=message_text)
        return Response(), 500
    
@app.route('/pagerduty-me', methods=['POST'])
def my_next_shift():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    token = data.get('token')
    pg_id = _helper.get_pagerduty_id(user_id)
    
    # Authorization Check
    if not _helper.ValidateOrigin(token, verification_token):
        message_text = "Failed to validate request, talk to system administrator!"
        client.chat_postEphemeral(channel= channel_id, user=user_id, text=message_text)
        return Response(), 401
    
    schedule =_helper.get_users_on_call_schedule(pg_id)
    
    header = "Here is your on call schedule for the next 3 months:\n"
    formatted_message = _helper.format_schedule_message(schedule)
    
    client.chat_postEphemeral(channel= channel_id, user=user_id, text=header + "\n" + formatted_message)
    
    return Response(), 200

@app.route('/pagerduty-list', methods=['POST'])
def pagerduty_list():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    token = data.get('token')
    
    # Authorization Check
    if not _helper.ValidateOrigin(token, verification_token):
        message_text = "Failed to validate request, talk to system administrator!"
        client.chat_postEphemeral(channel= channel_id, user=user_id, text=message_text)
        return Response(), 401
    
    schedules = _helper.get_oncall_schedules()
    
    header = "Here is the on-call schedule for the next 3 months:\n"
    formatted_message = _helper.format_schedule_message(schedules)
    
    client.chat_postEphemeral(channel= channel_id, user=user_id, text=header + "\n" + formatted_message)

    return Response(), 200

@app.route('/pagerduty-swap', methods=['POST'])
def open_advanced_menu():
    data = request.form
    user_id = data.get('user_id')
    trigger_id = data.get('trigger_id')

    channel_id = data.get('channel_id')
    # users_in_channel = _helper.get_users_in_channel(channel_id)

    try:
        client.views_open(
            trigger_id=trigger_id,
            view=modal_payload
        )

    except Exception as e:
        print(f"Error opening advanced modal: {str(e)}")

    return Response(), 200

@app.route('/submit-swap', methods=['POST'])
def submit_swap():
    try:
        payload = json.loads(request.form.get('payload'))

        if 'type' in payload and payload['type'] == 'view_submission':
            # The payload is from a view submission, meaning the "Submit" button was clicked
            process_submission(payload)
            return Response(), 200

    except Exception as e:
        print(f"Error while processing submission: {str(e)}")
        return Response(), 500

    return Response(), 200

def process_submission(payload):
    try:
        # The payload is from a view submission, meaning the "Submit" button was clicked
        user_id = payload['user']['id']
        #channel_id = payload['channel']['id']
        submission_values = payload['view']['state']['values']

        # Extract values from the submission
        start_date_1 = submission_values['section-identifier-1']['start_date_1']['selected_date']
        start_time_1 = submission_values['section-identifier-8']['start_time_1']['selected_time']
        end_date_1 = submission_values['section-identifier-2']['end_date_1']['selected_date']
        end_time_1 = submission_values['section-identifier-9']['end_time_1']['selected_time']
        target_user_id = submission_values['section-identifier-6']['selected_user_2']['selected_user']
        start_date_2 = submission_values['section-identifier-4']['start_date_2']['selected_date']
        start_time_2 = submission_values['section-identifier-10']['start_time_2']['selected_time']
        end_date_2 = submission_values['section-identifier-5']['end_date_2']['selected_date']
        end_time_2 = submission_values['section-identifier-11']['end_time_2']['selected_time']
        
        author_id = _helper.get_pagerduty_id(user_id)
        target_id = _helper.get_pagerduty_id(target_user_id)

        # Create overrides for both the author and the target users
        overrides_data = {
            "overrides": [
                {
                    "start": f"{start_date_2}T{start_time_2}:00",
                    "end": f"{end_date_2}T{end_time_2}:00",
                    "user": {
                        "id": author_id,
                        "type": "user_reference"
                    },
                    "time_zone": "UTC"
                },
                {
                    "start": f"{start_date_1}T{start_time_1}:00",
                    "end": f"{end_date_1}T{end_time_1}:00",
                    "user": {
                        "id": target_id,
                        "type": "user_reference"
                    },
                    "time_zone": "UTC"
                }
            ]
        }


        # Make a single POST request to create both overrides
        response = requests.post(
            f"https://api.pagerduty.com/schedules/{schedule_id}/overrides",
            json=overrides_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token token={pagerduty_api_token}"
            }
        )

        if response.status_code == 201 or response.status_code == 200:
            # Overrides creation successful
            message_text = "Successfully created override!"
            #client.chat_postEphemeral(channel=channel_id, user=user_id, text=message_text)
        else:
            # Handle any errors or validation issues with creating the overrides
            error_message = "Failed to create overrides. Please check the dates and try again."
            return Response(error_message, status=400)

    except Exception as e:
        # Handle exceptions here, e.g., log the error
        print(f"Error while creating override: {str(e)}")
        return Response(), 500

    # Return a 200 response for other cases
    return Response(), 200


    
if __name__ == "__main__":
    app.run(debug=True, port=80)
    