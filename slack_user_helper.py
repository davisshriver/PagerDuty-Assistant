import datetime
import requests
import pytz
from slack_sdk import WebClient

class SlackUserHelper:
    def __init__(self, slack_token, pgd_token, schedule_id):
        self._slack_client = WebClient(token=slack_token)
        self._pagerduty_token = pgd_token
        self._schedule_id = schedule_id
        self._headers = {
            'Authorization': f'Token token={self._pagerduty_token}',
            'Content-Type': 'application/json',
        }

    def get_pagerduty_id(self, slack_id):
        
        pagerduty_users_url = 'https://api.pagerduty.com/users'
        
        try:
            # Call the users.info API to retrieve user information, including email
            user_info = self._slack_client.users_profile_get(user=slack_id)
            
            email = user_info['profile']['email']
            
            # Get pagerduty id by using slack email
            response = requests.get(pagerduty_users_url, headers=self._headers)
            response.raise_for_status()
            pagerduty_users = response.json()['users']
            
            # Check for a user with a matching id
            matching_pagerduty_user = next((user for user in pagerduty_users if user['email'] == email), None)
            
            if matching_pagerduty_user:
                pagerduty_user_id = matching_pagerduty_user['id']
                return pagerduty_user_id
            else:
                print(f"No matching PagerDuty user found for Slack user's email {email}")
                return None
            
        except Exception as e:
            print(f"Error retrieving Pagerduty Id: {str(e)}")
            return None
          
    def get_oncall_schedules(self):
        today = datetime.datetime.today()
        three_months_later = today + datetime.timedelta(days=90)

        start_date = today.strftime('%Y-%m-%dT00:00:00Z')
        end_date = three_months_later.strftime('%Y-%m-%dT23:59:59Z')

        params = {
            'schedule_ids[]': self._schedule_id,
            'since': start_date,
            'until': end_date
        }

        try:
            response = requests.get('https://api.pagerduty.com/oncalls', params=params, headers=self._headers)
            response.raise_for_status()
            oncall_data = response.json()

            # Extract and process on-call data for this period
            user_schedules = []

            for oncall_entry in oncall_data['oncalls']:
                user_info = oncall_entry['user']
                user_id = user_info['id']  
                user_name = user_info['summary']  
                user_start_date = oncall_entry['start']
                user_end_date = oncall_entry['end']

                user_schedules.append({
                    'id' : user_id,
                    'user_name': user_name,
                    'start_date': user_start_date,
                    'end_date': user_end_date
                })

            return user_schedules

        except requests.exceptions.RequestException as e:
            return None
        
    def get_users_on_call_schedule(self, userId):
        today = datetime.datetime.today()
        three_months_later = today + datetime.timedelta(days=90)

        start_date = today.strftime('%Y-%m-%dT00:00:00Z')
        end_date = three_months_later.strftime('%Y-%m-%dT23:59:59Z')

        params = {
            'schedule_ids[]': self._schedule_id,
            'user_ids[]': userId,
            'since': start_date,
            'until': end_date
        }

        try:
            response = requests.get('https://api.pagerduty.com/oncalls', params=params, headers=self._headers)
            response.raise_for_status()
            oncall_data = response.json()

            # Extract and process on-call data for this period
            user_schedules = []

            for oncall_entry in oncall_data['oncalls']:
                user_info = oncall_entry['user']
                user_name = user_info['summary']  
                user_start_date = oncall_entry['start']
                user_end_date = oncall_entry['end']

                user_schedules.append({
                    'user_name': user_name,
                    'start_date': user_start_date,
                    'end_date': user_end_date
                })

            return user_schedules if user_schedules else None

        except requests.exceptions.RequestException as e:
            return None
        
    @staticmethod    
    def format_schedule_message(schedules):
    # Format the schedules into a Slack message
        formatted_message = ""

        for schedule in schedules:
            start_date = schedule['start_date'].split('T')[0]  
            end_date = schedule['end_date'].split('T')[0]  
            user_name = schedule['user_name']

            formatted_message += f"• {user_name}: ({start_date}) - ({end_date}) \n"

        return formatted_message
    
    @staticmethod  
    def validate_origin(validation_token, request_token):
        if validation_token == request_token:
            return True
        else:
            return False
        
    @staticmethod    
    def validate_schedule(self, schedule_data):
        user_schedule = self.get_oncall_schedules()

        for entry in schedule_data:
            user_id, start_time, end_time = entry

            # Check if the provided date and time range is valid in the user's schedule
            valid_date_time_range = self.validate_date_time_range(user_id, start_time, end_time, user_schedule)

            # If any date and time range or user ID is not valid, return False
            if not valid_date_time_range:
                return False

        # All date and time ranges and user IDs are valid
        return True
    
    @staticmethod  
    def validate_date_time_range(user_id, start_datetime, end_datetime, user_schedule):
        start_datetime = datetime.datetime.fromisoformat(start_datetime)
        end_datetime = datetime.datetime.fromisoformat(end_datetime)
        
        # Set to UTC
        utc = pytz.UTC
        start_datetime = start_datetime.astimezone(utc)
        end_datetime = start_datetime.astimezone(utc)

        for schedule_entry in user_schedule:
            if (
                schedule_entry['id'] == user_id
                and datetime.datetime.fromisoformat(schedule_entry['start_date']) <= start_datetime
                and datetime.datetime.fromisoformat(schedule_entry['end_date']) >= end_datetime
            ):
                return True

        # The date and time range is not valid or doesn't match the user_id in the user's schedule
        return False
        
    
