Plugin Parameters :

	client_id(String)                                - The unique identifier of the application registered at Azure Active Directory.Accept valid UUID only
	client_secret(String)                            - Client Secret of the application registered at Azure Active Directory.
	azure_active_directory_id(String)                - The unique identifier of the Azure Active Directory.(AAD > Properties > Directory ID).Accept valid UUID only
	graph_api_version(String)                        - Microsoft graph API version. e.g v1.0, beta
	scope(String)                                    - The value passed for the scope parameter in this request should be the resource identifier (Application ID URI) of the resource you want, affixed with the .default suffix. For Microsoft Graph, the value is https://graph.microsoft.com/.default. This value informs the Microsoft identity platform endpoint that of all the application permissions you have configured for your app, it should issue a token for the ones associated with the resource you want to use.

Commands :

	1. get_users
		Get users in the organization.
		input -
			name(String List)                              - The display name of the user.
			email(String List)                             - The user's email address.Accept valid emails only
			enable_raw_json(Bool)                          - Enable Raw Json output? If True, will additionally give rawJson returned by Microsoft graph API
		output -
			user_details(azure_ad.AzureActiveDirectoryUser List)                    - Microsoft Azure Active Directory users
			raw_json(JSON)                                 - RawJson as returned by graph API. Will be returned if enable_raw_json is true
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	2. get_users_advance
		Get users in the organization.
		input -
			id(String List)                                - The unique identifier for the user. If unique identifier is given, other search parameters will be ignored.Accept valid UUID only
			name(String List)                              - The display name of the user
			given_name(String List)                        - The first name of the user.
			job_title(String List)                         - The user's job title.
			email(String List)                             - The user's email address.accept valid email.Accept valid email only
			surname(String List)                           - The last name of the user.
			user_principal_name(String List)               - The user's principal name.
			enable_raw_json(Bool)                          - Enable Raw Json output? If True, will additionally give rawJson returned by Microsoft graph API
			properties(String)                             - Properties to be selected as a comma separated string
		output -
			user_details(azure_ad.AzureActiveDirectoryUser List)                    - Microsoft Azure Active Directory users
			raw_json(JSON)                                 - RawJson as returned by graph API. Will be returned if enable_raw_json is true
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	3. update_users
		Update user details in the Azure AD
		input -
			unique_id(String List)                         - The unique identifier for the user.Accept valid UUID only
			parameters(JSON)                               - Other params to update as a json body. e.g. {'city': 'xyz', 'country': 'IND'}
		output -
			updated_users(String List)                     - Updated users list
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	4. enable_users
		Enable user in the organization.
		input -
			unique_id(String List)                         - The unique identifier for the user.Accept valid UUID only
		output -
			enabled_users(String List)                     - Enabled users list
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response

	5. disable_users
		Disable users in the organization.
		input -
			unique_id(String List)                         - The unique identifier for the user.Accept valid UUID only.
		output -
			disabled_users(String List)                    - Disabled users list
			task_success(Bool)                             - False if any part of task fails
			status_msg(String)                             - Task execution status message
			response_code(Integer)                         - Response code of the api response
