Plugin Parameters :

	client_id(String)                                - The unique identifier of the application registered at Azure Active Directory.
	client_secret(String)                            - Client Secret of the application registered at Azure Active Directory.
	tenant_id(String)                                - The unique identifier of the Azure Active Directory
	graph_api_version(String)                        - Microsoft graph API version. e.g v1.0, beta
	verify_certs(Bool)                               - Should the TLS certificates be verified
	timeout(Integer)                                 - request timeout
	code(String)                                     - The authorization_code that the app requested. The app can use the authorization code to request an access token for the target resource.This is required for first API call to generate access_token.Later we store refresh_token to generate new access_token
	redirect_uri(String)                             - The redirect_uri of your app, where authentication responses can be sent and received by your app. It must exactly match one of the redirect URIs you registered in the portal, except it must be URL-encoded.If you don't use default value please update redirect_uri in url while generating code in browser
	proxyProtocol(String)                            - Proxy protocol
	proxyHost(HostName | IPAddress)                  - Proxy Hostname or IP Address
	proxyPort(Integer)                               - Proxy Port
	proxyUser(String)                                - Proxy User
	proxyPassword(String)                            - Proxy User Password

Commands :

	1. sendMessage
		Send a message to a channel
		input -
			teamDisplayName(String)                        - displayName for the team to send a message to
			channelDisplayName(String)                     - displayName for the channel to send a message to
			message(String)                                - message to send to the channel
		output -
			statusMsg(String)                              - Status of the plug-in execution
			success(Bool)                                  - True if message sent

	2. replyMessage
		Reply to a message in a channel
		input -
			teamDisplayName(String)                        - displayName for the team to reply to a message
			channelDisplayName(String)                     - displayName for the channel to reply a message
			messageid(String)                              - id of the message to reply to (watchChannelAdapter provides in output)
			message(String)                                - message to reply with
		output -
			statusMsg(String)                              - Status of the plug-in execution
			success(Bool)                                  - True if message sent

	3. createTeam
		Create a new Team with specified users and owners.
		input -
			teamDisplayName(String)                        - teamDisplayName of team to create
			mailNickname(String)                           - mailNickname is an unique identifier for a group or a user, and it is used when creating or updating groups and users using Azure AD Graph API.It has to be unique within the container or organizational unit where the group or user is located
			description(String)                            - description of team to create
			members(String List)                           - a list of the mailNickname's of users to add as members
			owners(String List)                            - a list of the mailNickname's of users to add as owners
		output -
			statusMsg(String)                              - Status of the plug-in execution
			success(Bool)                                  - True if team created
			team_id(String)                                - id of the team created

	4. createChannel
		Create a new channel for a team
		input -
			teamDisplayName(String)                        - displayName of team to create a channel for
			channelDisplayName(String)                     - displayName of the channel to create
			description(String)                            - description of channel to create
		output -
			statusMsg(String)                              - Status of the plug-in execution
			success(Bool)                                  - True if channel created
			channel_id(String)                             - channel_id of the channel created

	5. deleteTeam
		Delete a Team.O365 group is deleted but team must be manually deleted
		input -
			teamDisplayName(String)                        - teamDisplayName of team to delete
		output -
			statusMsg(String)                              - Status of the plug-in execution
			success(Bool)                                  - True if team deleted

	6. deleteChannel
		Delete a Channel for a team
		input -
			teamDisplayName(String)                        - displayName of team that has a channel to delete
			channelDisplayName(String)                     - displayName of channel to delete
		output -
			statusMsg(String)                              - Status of the plug-in execution
			success(Bool)                                  - True if channel deleted

	7. watchChannelAdapter
		Watch the channel and looks for a custom command prefix in the new messages.
		input -
			teamDisplayName(String)                        - displayName for the team that has a channel to watch
			channelDisplayName(String)                     - displayName for the channel to watch
			commandPrefix(String)                          - The required prefix to a command.  E.g. !FSO command <IP>  the commandPrefix here would be !FSO
		output -
			statusMsg(String)                              - Status of the plug-in execution
			success(Bool)                                  - True if watchChannelAdapter succesful
			MicrosoftTeamsChatMessage(microsoft_MicrosoftTeamsChatMessage)          - MicrosoftTeamsChatMessage that had a detected command prefix
			CommandAndParameters(microsoft_CommandAndParameters)                    - Json command and paramenters detected in a MicrosoftTeamsChatMessage
			teamDisplayName(String)                        - teamDisplayName that had a detected command prefix
			channelDisplayName(String)                     - channelDisplayName that had a detected command prefix
