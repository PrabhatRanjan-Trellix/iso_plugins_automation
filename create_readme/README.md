Plugin Parameters :

	url(String)                                      - URL of cloud Email Security Server, example: https://etp.us.fireeye.com. Accept valid URL only
	api_key(String)                                  - ETP API key

Commands :

	1. retrieve_message
		Retrieves the particular message with the specified Email Security message ID.
		input -
			message_id(String List)                        - The ID of the Email Security message.
			traffic_type(String)                           - The direction of the email traffic.Accepted value are (inbound, outbound)
		output -
			etp_email(email_security.ETPEmail List)        - User ComplexType of Email Security Message Trace
			raw_json(JSON)                                 - Email Security Message Trace Raw Response
			retrieved_message_ids(String List)             - List of message id, for which message retrieved
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	2. email_search
		Retrieves email trace information as per the attributes and traffic type that are accessible in the Email Security.Each input parameters can have max of 10 values
		input -
			from_email(String List)                        - List of senders email.Accept valid emails only
			recipients(String List)                        - List of recipients.Accept valid emails only
			subject(String)                                - The subject of email
			from_time(String)                              - Timestamp search start. Please provide time in ISO8601 format. (eg. '2024-01-02T15:04:05.000z').Both 'from_time' and 'to_time' are required fields to specify the datetime range for the search.
			to_time(String)                                - Timestamp search stop. Please provide time in ISO8601 format. (eg. 2024-01-02T15:04:05.000z).Both 'from_time' and 'to_time' are required fields to specify the datetime range for the search. If 'from_time' is provided but 'to_time' is not, the current datetime will be used as the to_time time.
			status(String)                                 - email status. Accepted values are: (accepted, deleted, delivered, delivered (retroactive), dropped, dropped oob, dropped (oob retroactive), permanent failure, processing, quarantined, rejected, temporary failure, scanned, scan bypassed, split)
			has_attachment(Bool)                           - Mark true if email contains attachment
			min_message_size(Float)                        - Minimum size of the email.Accept positive float only
			max_message_size(Float)                        - Maximum size of the email.Accept positive float only
			sender_ip(String List)                         - List of sending SMTP IPs.Accept valid ip_addresses only
			domains(String List)                           - List of domains. Accept valid domains only
			limit(Integer)                                 - Max number of emails to return.Default is 20.Accept positive integer only
		output -
			etp_email(email_security.ETPEmail)             - User ComplexType of Email Security Email Trace
			raw_json(JSON)                                 - Email Security Email Trace Raw Response
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	3. message_remediate
		Remediates messages in ETP by specified Message IDs
		input -
			message_id(String List)                        - The ID of the Email Security message.
			action(String)                                 - The action to take on the message IDs, accepted values are (quarantine, move, delete). If action selected as move, then move_to is required parameter
			move_to(String)                                - The folder to move message to in the users inbox.If action selected as move, then move_to is required parameter
		output -
			remediate_response(email_security.ETPMessageRemediate)                  - User ComplexType of Email Security Message Remediate
			remediated_message_ids(String List)            - List of message IDs for emails that have been remediated
			raw_json(JSON)                                 - Email Security Message Remediate Raw Response
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	4. url_click_report
		Retrieves URL click reports
		input -
			alert_id(String)                               - The ID of the Advance threat alert
		output -
			url_click_report(email_security.ETPUrlClickReport)                      - User ComplexType of Email Security URL Click Report
			raw_json(JSON)                                 - URL click report Raw Response
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response
