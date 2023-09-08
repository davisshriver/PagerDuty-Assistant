# PagerDuty-Assitant
"PagerDuty Assistant" is a powerful and user-friendly web application designed to streamline the process of managing your PagerDuty schedule within Slack. With PagerDuty Assistant, accessing your on-call schedule, retrieving essential information from PagerDuty, and creating schedule overrides has never been easier or more efficient.

### Key Features:

Instant Schedule Access: PagerDuty Assistant provides instant access to your on-call schedule, allowing you to view your upcoming shifts for the next three months effortlessly. Say goodbye to the hassle of navigating through PagerDuty's interface.

PagerDuty Information at Your Fingertips: Quickly gather important information from PagerDuty, such as your PagerDuty ID, on-call schedule details, and team members' schedules, all from within your Slack workspace. No need to switch between platforms or perform lengthy searches.

Effortless Schedule Overrides: When unexpected situations arise that prevent you from being on call, PagerDuty Assistant simplifies the process of creating schedule overrides. Easily create schedule overrides with just a few clicks, ensuring seamless coverage and minimal disruption.

PagerDuty Assistant is your go-to solution for making PagerDuty management a breeze, saving you time and effort so you can focus on what matters most. Say hello to a more efficient on-call experience with PagerDuty Assistant!

## Prerequisites

Before using this bot, ensure that you have the following prerequisites set up:

- Python 3.x installed.
- The required Python packages installed using `pip install`:
  - asyncio
  - json
  - logging
  - os
  - pathlib
  - dotenv
  - aiohttp
  - slack_sdk
  - slack_user_helper (a custom module include in this repository)
- A Slack App configured with appropriate permissions and tokens.
- A PagerDuty account with an API token and the necessary schedule and user configurations.

## Configuration

To use the bot, you need to set up environment variables in a `.env` file. The following environment variables are required:

- `SLACK_TOKEN`: Slack Bot Token for your Slack App.
- `VERIFICATION_TOKEN`: Slack Verification Token for your Slack App.
- `PAGERDUTY_TOKEN`: PagerDuty API Token.
- `SCHEDULE_ID`: PagerDuty Schedule ID.
- `CHANNEL_ID`: Slack channel ID where the bot will operate.

### Running the Bot

To run the bot, execute the script:

```bash
python <script_name>.py
```
The bot will start an HTTP server listening on 0.0.0.0:80.
# Documentation
## Available Endpoints

- `/pagerduty-id`: Retrieves a user's PagerDuty ID and sends it as a response to the user in Slack.
- `/pagerduty-me`: Provides a user's next shift on the PagerDuty schedule.
- `/pagerduty-list`: Lists the on-call schedule for the next 3 months.
- `/pagerduty-swap`: Initiates the process of scheduling a swap with another user.
- `/submit-swap`: Handles the submission of a schedule swap request.

## Interactive Modals

- The `/pagerduty-swap` endpoint opens an interactive modal for scheduling swaps using data from `modal_payload.json`.

## SlackUserHelper Class

The **SlackUserHelper** class is designed to assist in integrating Slack with PagerDuty for managing on-call schedules and users. It includes several methods for retrieving information and validating data.

### Constructor: `__init__(self, slack_token, pgd_token, schedule_id)`

- **Description:** Initializes the **SlackUserHelper** object with the necessary credentials and settings for Slack and PagerDuty integration.
- **Parameters:**
  - `slack_token` (str): Slack API token.
  - `pgd_token` (str): PagerDuty API token.
  - `schedule_id` (str): The ID of the PagerDuty schedule to work with.

### Method: `get_pagerduty_id(self, slack_id)`

- **Description:** Retrieves the PagerDuty user ID corresponding to a Slack user's ID by matching their email addresses.
- **Parameters:**
  - `slack_id` (str): Slack user ID.
- **Returns:** PagerDuty user ID (str) or `None` if not found.

### Method: `get_oncall_schedules(self)`

- **Description:** Retrieves a list of on-call schedules for the specified PagerDuty schedule within the next 90 days.
- **Returns:** List of on-call schedules, where each schedule is a dictionary containing user information, start date, and end date.

### Method: `get_users_on_call_schedule(self, userId)`

- **Description:** Retrieves on-call schedules for a specific user within the next 90 days.
- **Parameters:**
  - `userId` (str): PagerDuty user ID.
- **Returns:** List of on-call schedules for the specified user, or `None` if not found.

### Method: `format_schedule_message(schedules)`

- **Description:** Formats a list of schedules into a Slack message format.
- **Parameters:**
  - `schedules` (list of dict): List of on-call schedules to format.
- **Returns:** Formatted message (str).

### Method: `validate_origin(validation_token, request_token)`

- **Description:** Validates the origin of a request by comparing a validation token with a token provided in the request.
- **Parameters:**
  - `validation_token` (str): The expected validation token.
  - `request_token` (str): The token received in the request.
- **Returns:** `True` if the tokens match, otherwise `False`.

### Method: `validate_schedule(self, schedule_data)`

- **Description:** Validates a set of schedules by checking if they are valid within the user's on-call schedule.
- **Parameters:**
  - `schedule_data` (list of tuple): List of schedule data, where each tuple contains user ID, start time, and end time.
- **Returns:** `True` if all schedules are valid, otherwise `False`.

### Method: `validate_date_time_range(user_id, start_datetime, end_datetime, user_schedule)`

- **Description:** Validates if a date and time range is valid within a user's on-call schedule.
- **Parameters:**
  - `user_id` (str): PagerDuty user ID.
  - `start_datetime` (str): Start date and time in ISO format.
  - `end_datetime` (str): End date and time in ISO format.
  - `user_schedule` (list of dict): List of on-call schedules for the user.
- **Returns:** `True` if the date and time range is valid, otherwise `False`.
