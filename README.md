# PagerDuty-Assitant
"PagerDuty Assistant" is a powerful and user-friendly web application designed to streamline the process of managing your PagerDuty schedule within Slack. With PagerDuty Assistant, accessing your on-call schedule, retrieving essential information from PagerDuty, and creating schedule overrides has never been easier or more efficient.

### Key Features:

Instant Schedule Access: PagerDuty Assistant provides instant access to your on-call schedule, allowing you to view your upcoming shifts for the next three months effortlessly. Say goodbye to the hassle of navigating through PagerDuty's interface.

PagerDuty Information at Your Fingertips: Quickly gather important information from PagerDuty, such as your PagerDuty ID, on-call schedule details, and team members' schedules, all from within your Slack workspace. No need to switch between platforms or perform lengthy searches.

Effortless Schedule Overrides: When unexpected situations arise that prevent you from being on call, PagerDuty Assistant simplifies the process of creating schedule overrides. Easily create schedule overrides with just a few clicks, ensuring seamless coverage and minimal disruption.

PagerDuty Assistant is your go-to solution for making PagerDuty management a breeze, saving you time and effort so you can focus on what matters most. Say hello to a more efficient on-call experience with PagerDuty Assistant!
# Helper Functions
## get_pagerduty_id(slack_id)
This function retrieves a PagerDuty ID for a Slack user based on their Slack user ID.

### Parameters:

slack_id (string): The Slack user ID.
### Returns:

pagerduty_id (string): The PagerDuty ID of the user, or None if not found.

## get_oncall_schedules()
This function retrieves the on-call schedule for all users for the next 3 months.

### Returns:

schedules (list of dicts): A list of on-call schedules for all users. Each schedule entry includes the user's name, start date, and end date.

## get_users_on_call_schedule(userId)
This function retrieves the on-call schedule for a specific Slack user for the next 3 months.

### Parameters:

userId (string): The PagerDuty ID of the Slack user.
### Returns:

schedule (list of dicts): A list of on-call schedules for the specified user. Each schedule entry includes the user's name, start date, and end date.

## format_schedule_message(schedules)
This function formats a list of on-call schedules into a Slack message.

### Parameters:

schedules (list of dicts): A list of on-call schedules. Each schedule entry should include the user's name, start date, and end date.
### Returns:

formatted_message (string): A formatted message containing the on-call schedules.

## ValidateOrigin(validation_token, request_token)
This static method validates the origin of a request using a validation token.

### Parameters:

validation_token (string): The token to validate.
request_token (string): The token from the incoming request.
### Returns:

True if the validation is successful, False otherwise.
