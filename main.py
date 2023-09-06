import asyncio
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from aiohttp import web, ClientSession
from slack_sdk import WebClient
from slack_user_helper import SlackUserHelper

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

_slack_token = os.environ['SLACK_TOKEN']
_verification_token = os.environ['VERIFICATION_TOKEN']
_pagerduty_api_token = os.environ['PAGERDUTY_TOKEN']
_schedule_id = os.environ['SCHEDULE_ID']
_channel_id = ""

app = web.Application()

client = WebClient(_slack_token)
_helper = SlackUserHelper(_slack_token, _pagerduty_api_token, _schedule_id)

# Configure logging
logging.basicConfig(
    level=logging.ERROR,  
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to the console
    ],
)


with open('modal_payload.json', 'r') as file:
     modal_payload = json.load(file)

async def my_id(request):
    data = await request.post()
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    token = data.get('token')
    pg_id = _helper.get_pagerduty_id(user_id)

    # Authorization Check
    if not _helper.ValidateOrigin(token, _verification_token):
        message_text = "Failed to validate request, talk to system administrator!"
        client.chat_postEphemeral(channel=channel_id, user=user_id, text=message_text)
        return web.Response(status=401)

    if pg_id is not None:
        message_text = "Your Pagerduty Id is: " + pg_id
        client.chat_postEphemeral(channel=channel_id, user=user_id, text=message_text)
        return web.Response(status=200)
    else:
        message_text = "Failed to find a PagerDuty Id for your Slack account!"
        client.chat_postEphemeral(channel=channel_id, user=user_id, text=message_text)
        return web.Response(status=500)

async def my_next_shift(request):
    data = await request.post()
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    token = data.get('token')
    pg_id = _helper.get_pagerduty_id(user_id)

    # Authorization Check
    if not _helper.ValidateOrigin(token, _verification_token):
        message_text = "Failed to validate request, talk to system administrator!"
        client.chat_postEphemeral(channel=channel_id, user=user_id, text=message_text)
        return web.Response(status=401)

    schedule = _helper.get_users_on_call_schedule(pg_id)

    header = "Here is your on-call schedule for the next 3 months:\n"
    formatted_message = _helper.format_schedule_message(schedule)

    client.chat_postEphemeral(channel=channel_id, user=user_id, text=header + "\n" + formatted_message)

    return web.Response(status=200)

async def pagerduty_list(request):
    data = await request.post()
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    token = data.get('token')

    # Authorization Check
    if not _helper.ValidateOrigin(token, _verification_token):
        message_text = "Failed to validate request, talk to system administrator!"
        client.chat_postEphemeral(channel=channel_id, user=user_id, text=message_text)
        return web.Response(status=401)

    schedules = _helper.get_oncall_schedules()

    header = "Here is the on-call schedule for the next 3 months:\n"
    formatted_message = _helper.format_schedule_message(schedules)

    client.chat_postEphemeral(channel=channel_id, user=user_id, text=header + "\n" + formatted_message)

    return web.Response(status=200)

async def open_advanced_menu(request):
    data = await request.post()
    trigger_id = data.get('trigger_id')
    channel_id = data.get('channel_id')
    
    global _channel_id 
    _channel_id = channel_id # Update channel ID for the response messages

    try:
        client.views_open(
            trigger_id=trigger_id,
            view=modal_payload
        )

    except Exception as e:
        logging.error(f"Error opening advanced modal: {str(e)}")

    return web.Response(text='', status=200)

async def submit_swap(request):
    try:
        data = await request.post()
        payload = json.loads(data.get('payload', {}))

        # The payload is from a view submission, meaning the "Submit" button was clicked
        if 'type' in payload and payload['type'] == 'view_submission':
            asyncio.create_task(process_submission(payload))
            return web.Response(status=200)

    except Exception as e:
        logging.error(f"Error while processing submission: {str(e)}")
        return web.Response(status=500)

    return web.Response()

async def process_submission(payload):
    try:
        user_id = payload['user']['id']
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

        if(author_id is None or target_id is None):
            message_text = "You or your target user are not on the on-call schedule!"
            client.chat_postEphemeral(channel=_channel_id, user=user_id, text=message_text)
            return None
        elif(author_id == target_id):
            message_text = "You cannot override yourself!"
            client.chat_postEphemeral(channel=_channel_id, user=user_id, text=message_text)
            return None
        
        start_time_str_1 = f"{start_date_1}T{start_time_1}:00-05:00"
        end_time_str_1 = f"{end_date_1}T{end_time_1}:00-05:00"
        start_time_str_2 = f"{start_date_2}T{start_time_2}:00-05:00"
        end_time_str_2 = f"{end_date_2}T{end_time_2}:00-05:00"

        # Create overrides for both the author and the target users
        overrides_data = {
            "overrides": [
                {
                    "start": start_time_str_2,
                    "end": end_time_str_2,
                    "user": {
                        "id": author_id,
                        "type": "user_reference"
                    },
                    "time_zone": "UTC"
                },
                {
                    "start": start_time_str_1,
                    "end": end_time_str_1,
                    "user": {
                        "id": target_id,
                        "type": "user_reference"
                    },
                    "time_zone": "UTC"
                }
            ]
        }

        # Create overrides asynchronously
        status_code = await create_overrides(overrides_data)

        if status_code == 201 or status_code == 200:
            # Overrides creation successful
            message_text = "Successfully created override!"
            client.chat_postEphemeral(channel=_channel_id, user=user_id, text=message_text)
        else:
            # Handle any errors or validation issues with creating the overrides
            message_text = "Failed to create overrides. Please check the dates and try again."
            client.chat_postEphemeral(channel=_channel_id, user=user_id, text=message_text)

    except Exception as e:
        # Handle exceptions here, e.g., log the error
        logging.error(f"Error while creating override: {str(e)}")
        return web.Response(status=500)

    # Return a 200 response for other cases
    return web.Response()

# Define a coroutine function to create overrides asynchronously
async def create_overrides(overrides_data):
    async with ClientSession() as session:
        async with session.post(
            f"https://api.pagerduty.com/schedules/{_schedule_id}/overrides",
            json=overrides_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token token={_pagerduty_api_token}"
            }
        ) as response:
            return response.status
        
# Set up routes
app.router.add_post('/pagerduty-id', my_id)
app.router.add_post('/pagerduty-me', my_next_shift)
app.router.add_post('/pagerduty-list', pagerduty_list)
app.router.add_post('/pagerduty-swap', open_advanced_menu)
app.router.add_post('/submit-swap', submit_swap)

# Start application
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=80)
