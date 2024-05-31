#!/bin/env python
# -*- coding: utf-8 -*-

"""
==================================================
   MODULE HEADER
==================================================
 Module Name: Microsoft Teams
 Synopsis: A Plugin to integrate with MS Teams
 Use Case : Read/Write meesages to a channel
 Module Author: Prabhat Ranjan
==================================================

==================================================
   MODULE IMPORTS
==================================================
"""
from sys import version_info as python_version
import dateutil.parser
from datetime import datetime, timedelta, tzinfo
from io import StringIO
import json
import uuid
import time
import re

# FSO Specific Imports
from pyfso import get_parameters, FsoRequests, PROXY_PARAMS, handle_errors, fso_sleep, FSOPluginDB
from iso.data.user_param_types import UserComplexType
from iso.plugins.device import ISODevicePlugin
from iso.data import parameters

__author__ = "Prabhat Ranjan"
__dependency__ = '{"pyfso": "2.2.15"}'
__notes__ = """
Use this plugin in order to create a new virtual team, add members and owners, configure team settings, add channels,
install apps, add tabs and archive or delete the team.
https://docs.microsoft.com/en-us/graph/teams-concept-overview

In order to use this plugin the following setup is required:

1) An office 365 tenant with a username and password.

2) Register the application with the Microsoft Identity platform.
https://docs.microsoft.com/en-us/graph/auth-register-app-v2?toc=.%2Fref%2Ftoc.json&view=graph-rest-1.0

3) Create a new application secret in order to authenticate with Azure AD.
https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal#certificates-and-secrets

4) Add permissions for the application to access web API's.
https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-configure-app-access-web-apis#add-permissions-to-access-web-apis

Feature                 Required permisison
Create team             Group.ReadWrite.All User.ReadWrite.All
Delete team             Group.ReadWrite.All
Create channel          Group.ReadWrite.All
Delete channel          Group.ReadWrite.All
Send message            Group.ReadWrite.All
Reply message           Group.ReadWrite.All
Watch Channel Adapter   Group.ReadWrite.All

5) Get an administrator of the office 365 tenant to grant consent to the API permissions the app needs.
https://docs.microsoft.com/en-us/graph/permissions-reference
https://docs.microsoft.com/en-us/azure/active-directory/develop/consent-framework

## NOTE :-
    - All commands work fine if we generate access_token using code Authorization flow , but if we generate access_token using client_credentials flow only 4 out of 7 commands work (Create team , Delete team, Create channel, Delete channel)
    - To generate access_token using code Authorization flow, we need to provide delegated level Microsoft Graph permission listed above
    - To generate access_token using client_credentials flow, we need to provide application level Microsoft Graph permission listed above
    - To generate access_token using client_credentials flow we need to fill (client_id, client_secret, tenant_id, api_version) in device parameter
    - To generate access_token using code Authorization flow we need to fill additional device parameters (code, redirect_uri) other than required device parameters

## Steps to register redirect_uri in Microsoft Azure AD
    - select Mobile and desktop applications as platform and then choose 'https://login.microsoftonline.com/common/oauth2/nativeclient' as redirect_uri

## Steps to generate code in browser
    - url to hit in the browser : 'https://login.microsoftonline.com/<<tenant_id>>/oauth2/v2.0/authorize?client_id=<<client_id>>&response_type=code&redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient&response_mode=query&scope=offline_access%20Group.ReadWrite.All%20User.ReadWrite.All&state=12345&code_challenge=TwJRPYBgvttujOB4jwM8rSTsX-XnwqaG-D3HQtU931o&code_challenge_method=S256'
    - Replace tenant_id and client_id before hitting the url in the browser
    - After hitting the url it will ask the user to username and password to login in Microsoft Server and then it will ask you to give Microsoft Graph Permission
    - After successful login it will return code in the url in the browser and url should contain code
    - copy the url and fill in the device parameter 'code'

"""
__fso_version__ = "6.0.0"
__plugin_name__ = "Microsoft Teams"
__display__name__ = "Microsoft Teams"
__plugin_vendor__ = "Microsoft"
__vendor_url__ = "https://www.microsoft.com/en-in/microsoft-teams/group-chat-software"
__plugin_version__ = "2.0.0"
__plugin_categories__ = ("Messaging",)
__plugin_icon__ = "microsoft_teams.png"
__dependency__ = '{"Pyfso": "2.2.15"}'
__plugin_description__ = "Microsoft Teams is a unified communications platform that combines persistent workplace chat, video meetings, file storage (including collaboration on files), and application integration.This plugin integrates with Microsoft Teams using the Microsoft graph REST API."


"""
==================================================
   GLOBAL
==================================================
"""

TAG_RE = re.compile(r"<[^>]+>")
ZERO = timedelta(0)


class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()


def remove_tags(text):
    return TAG_RE.sub("", text)


class GraphError(Exception):
    pass


class GraphException(Exception):
    pass


CUSTOM_ERRORS = [
    {
        "exception": GraphError,
        "trace": "Error connecting to Graph Server: [{}]",
        "status_message": "Error connecting to Graph Server.",
        "result_success": False,
        "cmd_success": False,
    },
    {
        "exception": GraphException,
        "trace": "Exception connecting to Graph Server: [{}]",
        "status_message": "Exception connecting to Graph Server",
        "result_success": False,
        "cmd_success": True,
    },
]


"""
==================================================
   USER COMPLEX TYPE
==================================================
"""


class MicrosoftTeamsChatMessage(UserComplexType):
    __description__ = 'Represents an individual chat message within a channel or chat.'
    _id = (parameters.String, 'id')
    replyToId = (parameters.String, 'replyToId')

    class From(UserComplexType):
        class Application(UserComplexType):
            displayName = (parameters.String, 'displayName')
            _id = (parameters.String, 'id')
            tenantId = (parameters.String, 'tenantId')

            class Thumbnails(UserComplexType):
                _id = (parameters.String, 'id')

                class Large(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Medium(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Small(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Source(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                source = (Source, 'Source')
                small = (Small, 'Small')
                medium = (Medium, 'Medium')
                large = (Large, 'Large')

            thumbnails = (Thumbnails.list, 'Thumbnails')

        application = (Application, 'Application')

        class ApplicationInstance(UserComplexType):
            displayName = (parameters.String, 'displayName')
            _id = (parameters.String, 'id')
            tenantId = (parameters.String, 'tenantId')

            class Thumbnails(UserComplexType):
                _id = (parameters.String, 'id')

                class Large(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Medium(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Small(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Source(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                source = (Source, 'Source')
                small = (Small, 'Small')
                medium = (Medium, 'Medium')
                large = (Large, 'Large')

            thumbnails = (Thumbnails.list, 'Thumbnails')

        applicationInstance = (ApplicationInstance, 'ApplicationInstance')

        class Conversation(UserComplexType):
            displayName = (parameters.String, 'displayName')
            _id = (parameters.String, 'id')
            tenantId = (parameters.String, 'tenantId')

            class Thumbnails(UserComplexType):
                _id = (parameters.String, 'id')

                class Large(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Medium(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Small(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Source(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                source = (Source, 'Source')
                small = (Small, 'Small')
                medium = (Medium, 'Medium')
                large = (Large, 'Large')

            thumbnails = (Thumbnails.list, 'Thumbnails')

        conversation = (Conversation, 'Conversation')

        class ConversationIdentityType(UserComplexType):
            displayName = (parameters.String, 'displayName')
            _id = (parameters.String, 'id')
            tenantId = (parameters.String, 'tenantId')

            class Thumbnails(UserComplexType):
                _id = (parameters.String, 'id')

                class Large(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Medium(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Small(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Source(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                source = (Source, 'Source')
                small = (Small, 'Small')
                medium = (Medium, 'Medium')
                large = (Large, 'Large')

            thumbnails = (Thumbnails.list, 'Thumbnails')

        conversationIdentityType = (
            ConversationIdentityType, 'ConversationIdentityType')

        class Device(UserComplexType):
            displayName = (parameters.String, 'displayName')
            _id = (parameters.String, 'id')
            tenantId = (parameters.String, 'tenantId')

            class Thumbnails(UserComplexType):
                _id = (parameters.String, 'id')

                class Large(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Medium(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Small(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Source(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                source = (Source, 'Source')
                small = (Small, 'Small')
                medium = (Medium, 'Medium')
                large = (Large, 'Large')

            thumbnails = (Thumbnails.list, 'Thumbnails')

        device = (Device, 'Device')

        class Encrypted(UserComplexType):
            displayName = (parameters.String, 'displayName')
            _id = (parameters.String, 'id')
            tenantId = (parameters.String, 'tenantId')

            class Thumbnails(UserComplexType):
                _id = (parameters.String, 'id')

                class Large(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Medium(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Small(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Source(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                source = (Source, 'Source')
                small = (Small, 'Small')
                medium = (Medium, 'Medium')
                large = (Large, 'Large')

            thumbnails = (Thumbnails.list, 'Thumbnails')

        encrypted = (Encrypted, 'Encrypted')

        class Guest(UserComplexType):
            displayName = (parameters.String, 'displayName')
            _id = (parameters.String, 'id')
            tenantId = (parameters.String, 'tenantId')

            class Thumbnails(UserComplexType):
                _id = (parameters.String, 'id')

                class Large(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Medium(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Small(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Source(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                source = (Source, 'Source')
                small = (Small, 'Small')
                medium = (Medium, 'Medium')
                large = (Large, 'Large')

            thumbnails = (Thumbnails.list, 'Thumbnails')

        guest = (Guest, 'Guest')

        class Phone(UserComplexType):
            displayName = (parameters.String, 'displayName')
            _id = (parameters.String, 'id')
            tenantId = (parameters.String, 'tenantId')

            class Thumbnails(UserComplexType):
                _id = (parameters.String, 'id')

                class Large(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Medium(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Small(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Source(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                source = (Source, 'Source')
                small = (Small, 'Small')
                medium = (Medium, 'Medium')
                large = (Large, 'Large')

            thumbnails = (Thumbnails.list, 'Thumbnails')

        phone = (Phone, 'Phone')

        class User(UserComplexType):
            displayName = (parameters.String, 'displayName')
            _id = (parameters.String, 'id')
            tenantId = (parameters.String, 'tenantId')

            class Thumbnails(UserComplexType):
                _id = (parameters.String, 'id')

                class Large(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Medium(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Small(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                class Source(UserComplexType):
                    height = (parameters.String, 'height')
                    sourceItemId = (parameters.String, 'sourceItemId')
                    url = (parameters.String, 'url')
                    width = (parameters.String, 'width')
                    content = (parameters.String, 'content')

                source = (Source, 'Source')
                small = (Small, 'Small')
                medium = (Medium, 'Medium')
                large = (Large, 'Large')

            thumbnails = (Thumbnails.list, 'Thumbnails')

        user = (User, 'User')

    whofrom = (From.list, 'From')

    etag = (parameters.String, 'etag')
    messageType = (parameters.String, 'messageType')
    createdDateTime = (parameters.String, 'createdDateTime')
    lastModifiedDateTime = (parameters.String, 'lastModifiedDateTime')
    deletedDateTime = (parameters.String, 'deletedDateTime')
    subject = (parameters.String, 'subject')

    class Body(UserComplexType):
        content = (parameters.String, 'content')
        contentType = (parameters.String, 'contentType')

    body = (Body, 'Body')
    summary = (parameters.String, 'summary')

    class Attachments(UserComplexType):
        _id = (parameters.String, 'id')
        contentType = (parameters.String, 'contentType')
        contentUrl = (parameters.String, 'contentUrl')
        content = (parameters.String, 'content')
        name = (parameters.String, 'name')
        thumbnailUrl = (parameters.String, 'thumbnailUrl')

    attachments = (Attachments.list, 'Attachments')

    class Mentions(UserComplexType):
        _id = (parameters.String, 'id')
        mentionText = (parameters.String, 'mentionText')

        class Mentioned(UserComplexType):
            class Application(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            application = (Application, 'Application')

            class ApplicationInstance(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            applicationInstance = (ApplicationInstance, 'ApplicationInstance')

            class Conversation(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            conversation = (Conversation, 'Conversation')

            class ConversationIdentityType(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            conversationIdentityType = (
                ConversationIdentityType, 'ConversationIdentityType')

            class Device(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            device = (Device, 'Device')

            class Encrypted(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            encrypted = (Encrypted, 'Encrypted')

            class Guest(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            guest = (Guest, 'Guest')

            class Phone(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            phone = (Phone, 'Phone')

            class User(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            user = (User, 'User')

        mentioned = (Mentioned.list, 'Mentioned')

    mentions = (Mentions.list, 'Mentions')

    importance = (parameters.String, 'importance')
    policyViolation = (parameters.String, 'policyViolation')

    class Reactions(UserComplexType):
        createdDateTime = (parameters.String, 'createdDateTime')
        reactionType = (parameters.String, 'reactionType')

        class User(UserComplexType):
            class Application(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            application = (Application, 'Application')

            class ApplicationInstance(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            applicationInstance = (ApplicationInstance, 'ApplicationInstance')

            class Conversation(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            conversation = (Conversation, 'Conversation')

            class ConversationIdentityType(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            conversationIdentityType = (
                ConversationIdentityType, 'ConversationIdentityType')

            class Device(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            device = (Device, 'Device')

            class Encrypted(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            encrypted = (Encrypted, 'Encrypted')

            class Guest(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            guest = (Guest, 'Guest')

            class Phone(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            phone = (Phone, 'Phone')

            class User(UserComplexType):
                displayName = (parameters.String, 'displayName')
                _id = (parameters.String, 'id')
                tenantId = (parameters.String, 'tenantId')

                class Thumbnails(UserComplexType):
                    _id = (parameters.String, 'id')

                    class Large(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Medium(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Small(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    class Source(UserComplexType):
                        height = (parameters.String, 'height')
                        sourceItemId = (parameters.String, 'sourceItemId')
                        url = (parameters.String, 'url')
                        width = (parameters.String, 'width')
                        content = (parameters.String, 'content')

                    source = (Source, 'Source')
                    small = (Small, 'Small')
                    medium = (Medium, 'Medium')
                    large = (Large, 'Large')

                thumbnails = (Thumbnails.list, 'Thumbnails')

            user = (User, 'User')

        user = (User.list, 'User')

    reactions = (Reactions.list, 'Reactions')

    locale = (parameters.String, 'locale')
    deleted = (parameters.String, 'deleted')


class CommandAndParameters(UserComplexType):
    __description__ = (
        "Represents a command and parameters detected in an individual chat message."
    )
    command = (parameters.String, "command")
    command_parameters = (parameters.String, "command_parameters")


"""
==================================================
   PLUGIN CLASS
==================================================
"""


# Plugin Device Class
class MicrosoftTeams(ISODevicePlugin):
    """ Plugin Device Class """

    name = __plugin_name__
    version = __plugin_version__
    display_name = __display__name__
    description = __plugin_description__
    vendor = __plugin_vendor__
    categories = __plugin_categories__
    icon = __plugin_icon__

    """
    Plugin Device Parameters
    ===========================
    """
    pluginParameters = (
        ISODevicePlugin.Parameter(
            name="client_id",
            description="The unique identifier of the application registered at Azure Active Directory.",
            typ=parameters.String,
        ),
        ISODevicePlugin.Parameter(
            name="client_secret",
            description="Client Secret of the application registered at Azure Active Directory.",
            typ=parameters.String,
            encrypted=True,
        ),
        ISODevicePlugin.Parameter(
            name="tenant_id",
            description="The unique identifier of the Azure Active Directory",
            typ=parameters.String,
        ),
        ISODevicePlugin.Parameter(
            name="graph_api_version",
            description="Microsoft graph API version. e.g v1.0, beta",
            typ=parameters.String,
            properties={"choices": [
                {"label": "v1.0", "value": "v1.0"},
                {"label": "beta", "value": "beta"}
            ]},
        ),
        ISODevicePlugin.Parameter(
            name="verify_certs",
            description="Should the TLS certificates be verified",
            typ=parameters.Bool,
            value=True,
            properties={"optional": True},
        ),
        ISODevicePlugin.Parameter(
            name="timeout",
            description="request timeout",
            typ=parameters.Integer,
            value=120,
            properties={"optional": True},
        ),
        ISODevicePlugin.Parameter(
            name="code",
            description="The authorization_code that the app requested. The app can use the authorization code to request an access token for the target resource.This is required for first API call to generate access_token.Later we store refresh_token to generate new access_token",
            typ=parameters.String,
            properties={'optional': True},
        ),
        ISODevicePlugin.Parameter(
            name="redirect_uri",
            description="The redirect_uri of your app, where authentication responses can be sent and received by your app. It must exactly match one of the redirect URIs you registered in the portal, except it must be URL-encoded.If you don't use default value please update redirect_uri in url while generating code in browser",
            typ=parameters.String,
            properties={'optional': True},
            value='https://login.microsoftonline.com/common/oauth2/nativeclient'
        ),
    ) + PROXY_PARAMS

    """
    Plugin Command Definitions
    ===========================
    """
    commands = (
        ISODevicePlugin.Command(
            name="sendMessage",
            description="Send a message to a channel",
            manualTimeToCompleteInSec=120,
            actionName="Send",
            targetName="Message",
            summaryParameterNames=("statusMsg", "success"),
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    name="teamDisplayName",
                    typ=parameters.String,
                    description="displayName for the team to send a message to",
                ),
                ISODevicePlugin.InputParameter(
                    name="channelDisplayName",
                    typ=parameters.String,
                    description="displayName for the channel to send a message to",
                ),
                ISODevicePlugin.InputParameter(
                    name="message",
                    typ=parameters.String,
                    description="message to send to the channel",
                ),
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="statusMsg",
                    description="Status of the plug-in execution",
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.Bool, name="success", description="True if message sent"
                ),
            ),
        ),
        ISODevicePlugin.Command(
            name="replyMessage",
            description="Reply to a message in a channel",
            manualTimeToCompleteInSec=120,
            actionName="Reply",
            targetName="Message",
            summaryParameterNames=("statusMsg", "success"),
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    name="teamDisplayName",
                    typ=parameters.String,
                    description="displayName for the team to reply to a message",
                ),
                ISODevicePlugin.InputParameter(
                    name="channelDisplayName",
                    typ=parameters.String,
                    description="displayName for the channel to reply a message",
                ),
                ISODevicePlugin.InputParameter(
                    name="messageid",
                    typ=parameters.String,
                    description="id of the message to reply to (watchChannelAdapter provides in output)",
                ),
                ISODevicePlugin.InputParameter(
                    name="message",
                    typ=parameters.String,
                    description="message to reply with",
                ),
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="statusMsg",
                    description="Status of the plug-in execution",
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.Bool, name="success", description="True if message sent"
                ),
            ),
        ),
        ISODevicePlugin.Command(
            name="createTeam",
            description="Create a new Team with specified users and owners.",
            manualTimeToCompleteInSec=120,
            actionName="Create",
            targetName="Team",
            summaryParameterNames=("statusMsg", "success", "team_id"),
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    name="teamDisplayName",
                    typ=parameters.String,
                    description="teamDisplayName of team to create",
                ),
                ISODevicePlugin.InputParameter(
                    name="mailNickname",
                    typ=parameters.String,
                    description="mailNickname is an unique identifier for a group or a user, and it is used when creating or updating groups and users using Azure AD Graph API.It has to be unique within the container or organizational unit where the group or user is located",
                ),
                ISODevicePlugin.InputParameter(
                    name="description",
                    typ=parameters.String,
                    description="description of team to create",
                    properties={"optional": True},
                ),
                ISODevicePlugin.InputParameter(
                    name="members",
                    typ=parameters.String.list,
                    description="a list of the mailNickname's of users to add as members",
                ),
                ISODevicePlugin.InputParameter(
                    name="owners",
                    typ=parameters.String.list,
                    description="a list of the mailNickname's of users to add as owners",
                ),
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="statusMsg",
                    description="Status of the plug-in execution",
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.Bool, name="success", description="True if team created"
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="team_id",
                    description="id of the team created",
                    properties={"optional": True},
                ),
            ),
        ),
        ISODevicePlugin.Command(
            name="createChannel",
            description="Create a new channel for a team",
            manualTimeToCompleteInSec=120,
            actionName="Create",
            targetName="Channel",
            summaryParameterNames=("statusMsg", "success", "channel_id"),
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    name="teamDisplayName",
                    typ=parameters.String,
                    description="displayName of team to create a channel for",
                ),
                ISODevicePlugin.InputParameter(
                    name="channelDisplayName",
                    typ=parameters.String,
                    description="displayName of the channel to create",
                ),
                ISODevicePlugin.InputParameter(
                    name="description",
                    typ=parameters.String,
                    description="description of channel to create",
                    properties={"optional": True},
                ),
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="statusMsg",
                    description="Status of the plug-in execution",
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.Bool, name="success", description="True if channel created"
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="channel_id",
                    description="channel_id of the channel created",
                    properties={"optional": True},
                ),
            ),
        ),
        ISODevicePlugin.Command(
            name="deleteTeam",
            description="Delete a Team.O365 group is deleted but team must be manually deleted",
            manualTimeToCompleteInSec=120,
            actionName="Delete",
            targetName="Team",
            summaryParameterNames=("statusMsg", "success"),
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    name="teamDisplayName",
                    typ=parameters.String,
                    description="teamDisplayName of team to delete",
                ),
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="statusMsg",
                    description="Status of the plug-in execution",
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.Bool, name="success", description="True if team deleted"
                ),
            ),
        ),
        ISODevicePlugin.Command(
            name="deleteChannel",
            description="Delete a Channel for a team",
            manualTimeToCompleteInSec=120,
            actionName="Delete",
            targetName="Channel",
            summaryParameterNames=("statusMsg", "success"),
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    name="teamDisplayName",
                    typ=parameters.String,
                    description="displayName of team that has a channel to delete",
                ),
                ISODevicePlugin.InputParameter(
                    name="channelDisplayName",
                    typ=parameters.String,
                    description="displayName of channel to delete",
                ),
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="statusMsg",
                    description="Status of the plug-in execution",
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.Bool, name="success", description="True if channel deleted"
                ),
            ),
        ),
        ISODevicePlugin.AdapterCommand(
            name="watchChannelAdapter",
            description="Watch the channel and looks for a custom command prefix in the new messages.",
            manualTimeToCompleteInSec=120,
            actionName="Watch",
            targetName="Channel",
            summaryParameterNames=("statusMsg", "success", "MicrosoftTeamsChatMessage", "CommandAndParameters", "teamDisplayName", "channelDisplayName"),
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    name="teamDisplayName",
                    typ=parameters.String,
                    description="displayName for the team that has a channel to watch",
                ),
                ISODevicePlugin.InputParameter(
                    name="channelDisplayName",
                    typ=parameters.String,
                    description="displayName for the channel to watch",
                ),
                ISODevicePlugin.InputParameter(
                    name="commandPrefix",
                    description="The required prefix to a command.  E.g. !FSO command <IP>  the commandPrefix here would be !FSO",
                    typ=parameters.String,
                ),
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="statusMsg",
                    description="Status of the plug-in execution",
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.Bool, name="success", description="True if watchChannelAdapter succesful"
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.microsoft_teams.MicrosoftTeamsChatMessage,
                    name="MicrosoftTeamsChatMessage",
                    description="MicrosoftTeamsChatMessage that had a detected command prefix",
                    properties={"optional": True},
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.microsoft_teams.CommandAndParameters,
                    name="CommandAndParameters",
                    description="Json command and paramenters detected in a MicrosoftTeamsChatMessage",
                    properties={"optional": True},
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="teamDisplayName",
                    description="teamDisplayName that had a detected command prefix",
                    properties={"optional": True},
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String,
                    name="channelDisplayName",
                    description="channelDisplayName that had a detected command prefix",
                    properties={"optional": True},
                ),
            ),
        ),
    )

    # Init Constructor
    def __init__(self, *args, **kwargs):
        super(MicrosoftTeams, self).__init__(*args, **kwargs)
        self.client_id = get_parameters(self, "client_id")
        self.client_secret = get_parameters(self, "client_secret")
        self.tenant_id = get_parameters(self, "tenant_id")
        self.timeout = get_parameters(self, "timeout")
        self.verify_certs = get_parameters(self, "verify_certs")
        self.api_version = get_parameters(self, "graph_api_version")
        self.code = get_parameters(self, "code")
        self.redirect_uri = get_parameters(self, "redirect_uri")
        self.graph_api_url = "https://graph.microsoft.com/" + self.api_version
        self.access_token_url = "https://login.microsoftonline.com/{}/oauth2/token".format(
            self.tenant_id)
        self.FSOPluginDB = FSOPluginDB(plugin_name=__display__name__)
        self.fso_requests = FsoRequests(device=self, verify_certs=self.verify_certs, retries=3, backoff_factor=0.4,
                                        status_forcelist=(500, 502, 503, 504, 409), default_timeout=self.timeout)
        self.scope = "Group.ReadWrite.All User.ReadWrite.All"
        self.code_challenge = 'TwJRPYBgvttujOB4jwM8rSTsX-XnwqaG-D3HQtU931o'
        self.code_challenge_method = 'S256'
        self.code_verifier = 'KciCHQSvXhGYtC9ahMOiicFekEeY2_NA88tNOWskUpyMxweFtnI4eQ0dWj76xDyhvhGGtqqwyLZ1HJTv'
        self.result = self.makeResult()
        self.result.success = True
        self.token_response = {}
        self.access_token = None

    # Generate access_token for authentication
    @handle_errors(custom=CUSTOM_ERRORS)
    def generateNewToken(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://localhost"
        }

        if self.code:
            # if code is full url instead of code , extract code part
            self.code = self.code.split('code=')[1].split('&')[0]
            if self.redirect_uri:
                self.logger.user_info('Generating access token using authorization code flow')
                data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                    "code": self.code,
                    "code_verifier": self.code_verifier
                }
            else:
                self.result.error(10000, "Please provide redirect_uri in the device parameter")
                self.result.success = False
                raise GraphError("Please provide required parameter redirect_uri in the device parameter")
        else:
            self.logger.user_info('Generating access token using client_credentials flow')
            data = {
                "grant_type": "client_credentials",
                "resource": "https://graph.microsoft.com",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }

       # Make the request to get an oAuth2 token
        try:
            token_response = self.fso_requests.get(
                url=self.access_token_url, data=data, headers=headers
            )

            if not token_response:
                raise GraphError("Invalid token response received ")

            self.token_response = token_response.json()
            self.access_token = self.token_response["access_token"]
            self.logger.user_info('Successfully generated access_token for authentication')
            if self.dbContainsTokenResponse():
                self.updateRefreshTokenInDB()
            else:
                self.storeTokenResponseInDB()

        except Exception as exp:
            raise GraphError(
                "Failed to get oAuth2 token from Microsoft Online servers. {}".format(str(exp.response.text)))

    @handle_errors(custom=CUSTOM_ERRORS)
    def tokenRefresh(self):
        if "refresh_token" not in self.token_response:
            raise GraphException(
                "refresh token do not exists. Please try running this command again.")
        # make the request to refresh oAuth2 token
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.token_response["refresh_token"],
        }
        try:
            token_response = self.fso_requests.post(
                self.access_token_url, data=data)
            self.result.trace('Successfully generated access_token using refresh_token')
            self.token_response = token_response.json()
            self.access_token = self.token_response.get("access_token")
            if self.dbContainsTokenResponse():
                self.updateRefreshTokenInDB()
            else:
                self.storeTokenResponseInDB()
        except Exception as exc:
            self.result.error(10001, 'Failed to generate access_token from refresh token due to : {}'.format(exc.response.text))

    def tokenExpiresInSecond(self):
        if not self.token_response["access_token"] or int(time.time()) >= int(self.token_response["expires_on"]):
            return 0
        return int(self.token_response["expires_on"]) - int(time.time())

    def isAccessTokenExpired(self):
        if self.tokenExpiresInSecond() < 5:
            return True
        return False

    def validateAccessToken(self):
        self.result.trace('Validating access_token')
        if self.dbContainsTokenResponse():
            self.logger.user_info('FSOPluginDB contains token_response. Fetching token_response from db ---->')
            self.token_response = self.getTokenResponseFromDB()
            self.access_token = self.token_response['access_token']
            if self.isAccessTokenExpired():
                self.tokenRefresh()
                if self.isAccessTokenExpired():
                    self.generateNewToken()
        else:
            self.generateNewToken()


    """
    FSOPluginDB related functions
    =============================
    """
    def getTokenResponseFromDB(self):
        results = self.FSOPluginDB.get_all()
        if results:
            for result in results:
                if 'token_response' in result['data']:
                    tokenResponse = result['data']['token_response']
                    self.result.trace('Successfully fetched token response!!')
                    return tokenResponse
        return None

    def dbContainsTokenResponse(self):
        results = self.FSOPluginDB.get_all()
        if results:
            for result in results:
                if 'token_response' in result['data']:
                    return True
        return False

    def storeTokenResponseInDB(self):
        self.FSOPluginDB.store_json({'token_response': self.token_response})

    def getDocID_tokenResponse(self):
        doc_id = None
        results = self.FSOPluginDB.get_all()
        if results:
            for result in results:
                if 'token_response' in result['data']:
                    doc_id = result['id']
                    self.result.trace('Successfully fetched doc_id!!')
                    break
        return doc_id

    def updateRefreshTokenInDB(self):
        doc_id = self.getDocID_tokenResponse()
        self.FSOPluginDB.set_json({'token_response': self.token_response}, doc_id)

    """
    Plugin Command Methods
    ===========================
    """

    @handle_errors(custom=CUSTOM_ERRORS)
    def testDevice(self):
        # test device by getting information for the signed-in user
        self._request(method="GET", uri="/users")

        # result
        if self.result.success:
            statusMsg = "testDevice completed successfully"
            self.result["statusMsg"] = parameters.String(statusMsg)
            self.result["success"] = parameters.Bool(True)
        else:
            statusMsg = "testDevice command failed"
            self.result['statusMsg'] = parameters.String(statusMsg)
            self.result["success"] = parameters.Bool(False)
        return self.result

    # automatically sends an email
    @handle_errors(custom=CUSTOM_ERRORS)
    def createTeam(self, request):
        self.result.trace('createTeam command started')

        # right now this plugin creates a new Azure AD group for the team
        # alternatives - dont make groups have users provide existing group
        # alternatives - only make groups if not provided

        # lookup ids for members and owners
        members_list = get_parameters(request, "members", is_list=True)
        owners_list = get_parameters(request, "owners", is_list=True)

        members_ids_list = self._getUserIds(members_list)
        owners_ids_list = self._getUserIds(owners_list)

        # create a group - setting owners and members
        teamDisplayName = get_parameters(request, "teamDisplayName")
        mailNickname = get_parameters(request, "mailNickname")
        description = get_parameters(request, "description")

        # check if group is already exist
        response = self._request(method="GET", uri="/groups?$filter=mailNickname eq('{}')".format(mailNickname))
        if len(response.get('value')) == 1:
            try:
                group_id = response['value'][0]['_id']
                self.result.trace('Group already exist with specified mailNickname. Creating teams using the group')
            except (KeyError, IndexError):
                self.result.trace('Group does not exist. Creating a new group with specified owners and members')

        else:
            payload = {
                "displayName": "{}".format(teamDisplayName),
                "mailNickname": "{}".format(mailNickname),
                "description": "{}".format(description),
                "visibility": "Private",
                "groupTypes": ["Unified"],
                "mailEnabled": "true",
                "securityEnabled": "false",
                "members@odata.bind": members_ids_list,
                "owners@odata.bind": owners_ids_list,
            }
            response = self._request(method="POST", uri="/groups", json=payload)
            if response:
                # self.logger.user_info('response : {}'.format(response))
                if "_id" in response:
                    self.result.trace(
                        'successfully created group with specified owners and members in Azure AD')
                    group_id = response["_id"]
                    self.logger.user_info('group_id : {}'.format(group_id))
                else:
                    self.result.error(
                        10002, "group_id not found in response. response is not correct format")
                    self.result['statusMsg'] = parameters.String(
                        'group_id not found in response. response is not correct format')
                    self.result['success'] = False
                    return self.result
            else:
                self.result['statusMsg'] = parameters.String(
                    'Failed to create group in Azure AD. check trace for more details!')
                self.result['success'] = parameters.Bool(False)
                return self.result

        # add the team to the group
        payload = {
            "memberSettings": {"allowCreateUpdateChannels": "true"},
            "messagingSettings": {"allowUserEditMessages": "true", "allowUserDeleteMessages": "true"},
            "funSettings": {"allowGiphy": "true", "giphyContentRating": "moderate"},
        }

        # If the group was created less than 15 minutes ago, it's possible for the Create team call to fail with a 404 error code due to replication delays. The recommended pattern is to retry the Create team call three times, with a 10 second delay between calls.
        for i in range(5):
            response = self._request(method="PUT", uri="/groups/{}/team".format(group_id), json=payload)
            if response:
                break
            fso_sleep(10, self.send_keepalive)

        # The created team has the same ID as the group.
        # In order to create a team, the group must have a least one owner.
        # If the group was created less than 15 minutes ago, it's possible for the Create team call to fail with a 404 error
        # code due to replication delays. The recommended pattern is to retry the Create team call three times,
        # with a 10 second delay between calls.

        # result
        if response:
            statusMsg = "createTeam completed successfully"
            success = False
            team_id = response['_id']
            self.result['team_id'] = parameters.String(team_id)
        else:
            statusMsg = "Failed to create the team.check trace for more details!"
            success = False
        self.result["statusMsg"] = parameters.String(statusMsg)
        self.result["success"] = parameters.Bool(success)
        return self.result

    # known bug
    # https://techcommunity.microsoft.com/t5/Microsoft-Teams/Teams-exist-after-Group-Deletion/td-p/38051
    @handle_errors(custom=CUSTOM_ERRORS)
    def deleteTeam(self, request):
        self.result.trace('deleteTeam command started')
        teamDisplayName = get_parameters(request, "teamDisplayName")
        # list groups to lookup group id
        group_id = self._getGroupId(teamDisplayName)

        if not group_id:
            self.result['statusMsg'] = parameters.String(
                'Group not found in Azure Active Directory for teamDisplayName : {}'.format(teamDisplayName))
            self.result['success'] = parameters.Bool(False)
            return self.result

        # Generally it's delete group in Azure AD in first API call, but it still shows in Microsoft Teams

        response = self._request(
            method="DELETE", uri="/groups/{}".format(group_id))

        # calling following API will delete the team on microsoft team
        for i in range(3):
            group_id = self._getGroupId(teamDisplayName)
            if not group_id:
                break
            else:
                fso_sleep(10, self.send_keepalive())
                self._request(
                    method="DELETE", uri="/groups/{}".format(group_id))

        if response:
            statusMsg = "deleteTeam completed successfully"
            success = True

        else:
            statusMsg = "Failed to delete team. check trace for more details!"
            success = False
        # result
        self.result['statusMsg'] = parameters.String(statusMsg)
        self.result['success'] = parameters.Bool(success)
        return self.result

    @handle_errors(custom=CUSTOM_ERRORS)
    def createChannel(self, request):
        self.result.trace('createChannel command started')
        teamDisplayName = get_parameters(request, "teamDisplayName")

        # list groups to lookup group id
        group_id = self._getGroupId(teamDisplayName)

        if not group_id:
            self.result['statusMsg'] = parameters.String(
                'group_id not found for teamDisplayName : {}'.format(teamDisplayName))
            self.result['success'] = parameters.Bool(False)
            return self.result

        # create the channel
        channelDisplayName = get_parameters(request, "channelDisplayName")
        description = get_parameters(request, "description")
        payload = {"displayName": "{}".format(
            channelDisplayName), "description": "{}".format(description)}

        response = self._request(
            method="POST", uri="/teams/{}/channels".format(group_id), json=payload)

        # result
        if response:
            statusMsg = "createChannel completed successfully"
            success = True
            channel_id = response.get('_id')
            self.result['channel_id'] = parameters.String(channel_id)
        else:
            statusMsg = 'Failed to create channel.check trace for more details!'
            success = False
        self.result["statusMsg"] = parameters.String(statusMsg)
        self.result["success"] = parameters.Bool(success)
        return self.result

    @handle_errors(custom=CUSTOM_ERRORS)
    def deleteChannel(self, request):
        self.result.trace('deleteChannel command started')
        teamDisplayName = get_parameters(request, "teamDisplayName")
        # list groups to lookup group id
        group_id = self._getGroupId(teamDisplayName)

        if not group_id:
            self.result['statusMsg'] = parameters.String(
                'group_id not found for teamDisplayName : {}'.format(teamDisplayName))
            self.result['success'] = parameters.Bool(False)
            return self.result

        channelDisplayName = get_parameters(request, "channelDisplayName")
        # list channels of the group to lookup channel id
        channel_id = self._getChannelId(group_id, channelDisplayName)
        if not channel_id:
            self.result['statusMsg'] = parameters.String(
                'channel_id not found for channelDisplayName : {}'.format(channelDisplayName))
            self.result['success'] = parameters.Bool(False)
            return self.result

        # delete the channel
        response = self._request(
            method="DELETE", uri="/teams/{}/channels/{}".format(group_id, channel_id))

        # result
        if response:
            statusMsg = "deleteChannel completed successfully"
            success = True
        else:
            statusMsg = 'Failed to delete channel.check trace for more details!'
            success = False

        self.result["statusMsg"] = parameters.String(statusMsg)
        self.result["success"] = parameters.Bool(success)

        return self.result

    @handle_errors(custom=CUSTOM_ERRORS)
    def sendMessage(self, request):
        self.result.trace('sendMessage command started')
        teamDisplayName = get_parameters(request, "teamDisplayName")
        # list groups to lookup group id
        group_id = self._getGroupId(teamDisplayName)

        if not group_id:
            self.result['statusMsg'] = parameters.String(
                'group_id not found for teamDisplayName : {}'.format(teamDisplayName))
            self.result['success'] = parameters.Bool(False)
            return self.result

        # list channels of the group to lookup channel id
        channelDisplayName = get_parameters(request, "channelDisplayName")
        # list channels of the group to lookup channel id
        channel_id = self._getChannelId(group_id, channelDisplayName)
        if not channel_id:
            self.result['statusMsg'] = parameters.String(
                'channel_id not found for channelDisplayName : {}'.format(channelDisplayName))
            self.result['success'] = parameters.Bool(False)
            return self.result

        # send the message
        message = str(get_parameters(request, 'message'))
        payload = {"body": {"contentType": "text", "content": "{}".format(message)}}

        response = self._request(
            method="POST", uri="/teams/{}/channels/{}/messages".format(group_id, channel_id), json=payload)

        # result
        if response:
            statusMsg = "sendMessage completed successfully"
            success = True
        else:
            statusMsg = 'Failed to send message to channel.Check trace for more details!'
            success = False
        self.result["statusMsg"] = parameters.String(statusMsg)
        self.result["success"] = parameters.Bool(success)

        return self.result

    @handle_errors(custom=CUSTOM_ERRORS)
    def replyMessage(self, request):
        self.result.trace('replyMessage command started')
        teamDisplayName = get_parameters(request, "teamDisplayName")
        # list groups to lookup group id
        group_id = self._getGroupId(teamDisplayName)

        if not group_id:
            self.result['statusMsg'] = parameters.String(
                'group_id not found for teamDisplayName : {}'.format(teamDisplayName))
            self.result['success'] = parameters.Bool(False)
            return self.result

        # list channels of the group to lookup channel id
        channelDisplayName = get_parameters(request, "channelDisplayName")
        # list channels of the group to lookup channel id
        channel_id = self._getChannelId(group_id, channelDisplayName)
        if not channel_id:
            self.result['statusMsg'] = parameters.String(
                'channel_id not found for channelDisplayName : {}'.format(channelDisplayName))
            self.result['success'] = parameters.Bool(False)
            return self.result

        # send the reply
        message_id = get_parameters(request, "messageid")
        message = get_parameters(request, 'message')
        payload = {"body": {"contentType": "text",
                            "content": "{}".format(message)}}
        response = self._request(
            method="POST",
            uri="/teams/{}/channels/{}/messages/{}/replies".format(
                group_id, channel_id, message_id),
            json=payload,
        )

        # result
        if response:
            statusMsg = "replyMessage completed successfully"
            success = True
        else:
            statusMsg = 'Failed to replyMessage due to API error'
            success = False
        self.result["statusMsg"] = parameters.String(statusMsg)
        self.result["success"] = parameters.Bool(success)
        return self.result

    @handle_errors(custom=CUSTOM_ERRORS)
    def watchChannelAdapter(self, request):
        # keep track of the time the last command was run, so as not to repeat commands
        self.result.trace('watchChannelAdapter command started')
        last_time_command_run = None

        self.result.trace('replyMessage command started')
        teamDisplayName = get_parameters(request, "teamDisplayName")
        # list groups to lookup group id
        group_id = self._getGroupId(teamDisplayName)
        commandPrefix = get_parameters(request, "commandPrefix")

        if not group_id:
            self.result['statusMsg'] = parameters.String(
                'group_id not found for teamDisplayName : {}'.format(teamDisplayName))
            self.result['success'] = parameters.Bool(False)
            return self.result

        # list channels of the group to lookup channel id
        channelDisplayName = get_parameters(request, "channelDisplayName")
        # list channels of the group to lookup channel id
        channel_id = self._getChannelId(group_id, channelDisplayName)
        if not channel_id:
            self.result['statusMsg'] = parameters.String(
                'channel_id not found for channelDisplayName : {}'.format(channelDisplayName))
            self.result['success'] = parameters.Bool(False)
            return self.result

        # loop that turns this command into a long running adapter
        while True:
            self.send_keepalive()

            # get top message(adapter should run once per second,check that message time is in between now, 30 sec ago)
            response = self._request(
                method="GET", uri="/teams/{}/channels/{}/messages?$top=1".format(group_id, channel_id)
            )
            if response:
                seconds_ago = datetime.now(utc) - timedelta(seconds=30)
                message_time = dateutil.parser.parse(
                    response["value"][0]["createdDateTime"])
                now = datetime.now(utc)
                # diff = now - message_time
                # self.logger.user_info(u"seconds_ago datetime {}".format(seconds_ago))
                # self.logger.user_info(u"message_time datetime {}".format(message_time))
                # self.logger.user_info(u"now datetime {}".format(now))
                # self.logger.user_info(u"diff now - message_time: {}".format(diff))

                if seconds_ago < message_time < now:
                    messages = response["value"]
                    # self.logger.user_info(u"messages value's {}".format(messages))
                else:
                    messages = None
                    # self.logger.user_info(u"message value's is None")

                # find commandPrefix in messages then extract command, command_parameters and parent_message_id
                if messages:
                    for message in messages:
                        # if html contentType remove html tags so we can parse command and command_parameters easier
                        if message["body"]["contentType"] == "html":
                            message_content = remove_tags(
                                message["body"]["content"])
                            # self.logger.user_info(u"message content without tags: {}".format(message_content))
                        else:
                            message_content = message["body"]["content"]
                            # self.logger.user_info(u"message content: {}".format(message_content))

                        # parse and send result only if
                        # the message time is not the same as the last_time_command_run
                        # this prevents us from processing the same command over again and allows repeat commands
                        if message_time != last_time_command_run:
                            last_time_command_run = message_time  # remember last command time
                            # self.logger.user_info(u"last command time set to:{}".format(last_time_command_run))

                            # parse command, command_parameters and parent_message_id
                            match = re.search(
                                r"{} (\b\w+\b)(.*)".format(commandPrefix), message_content)
                            if match:
                                result = self.makeResult()
                                result.success = True
                                result["success"] = parameters.Bool(True)
                                command = match.group(1)
                                command_parameters = match.group(2)
                                # parent_message_id = message["_id"]
                                payload = {
                                    "command": command, "command_parameters": command_parameters.strip()}

                                result["MicrosoftTeamsChatMessage"] = parameters.microsoft_teams.MicrosoftTeamsChatMessage(
                                    message
                                )
                                result["CommandAndParameters"] = parameters.microsoft_teams.CommandAndParameters(
                                    payload)
                                result["teamDisplayName"] = parameters.String(
                                    teamDisplayName)
                                result["channelDisplayName"] = parameters.String(
                                    channelDisplayName)
                                result.send()  # send result to fso

                # this would be the "interval" we check for new commands every second
                time.sleep(1)
                self.send_keepalive()
            else:
                self.result['statusMsg'] = parameters.String(
                    'Failed to fetch message. check trace for more details')
                self.result['success'] = parameters.Bool(False)
                self.result.send()

    def _getUserIds(self, listOfuserNames):
        # lookup user id based on mailNickname for each user
        result_list_of_ids = []
        for username in listOfuserNames:
            response = self._request(
                method="GET", uri="/users?$filter=mailNickname eq('{}')".format(username))
            # correct response should have one value for the specified user so we can get the id
            try:
                if len(response["value"]) == 1:
                    # self.logger.user_info(u"added user: {} with id {}".format( username, response["value"][0]["_id"] ))
                    result_list_of_ids.append(
                        "https://graph.microsoft.com/v1.0/users/{}".format(
                            response["value"][0]["_id"])
                    )
            except KeyError:
                self.result.error(
                    10002, "failed to get userId for user: {} ".format(username))

        return result_list_of_ids

    @handle_errors(custom=CUSTOM_ERRORS)
    def _request(self, **kwargs):
        # keyword arguments for building request
        method = kwargs["method"]
        uri = kwargs["uri"]
        params = kwargs.get("params", None)
        json_payload = kwargs.get("json", None)
        data = kwargs.get("data", None)
        files = kwargs.get("files", None)
        custom_headers = kwargs.get("headers", None)
        stream = kwargs.get("stream", False)
        output = kwargs.get("output", "json")

        # define url for our request we call request with either http:// or
        # api part of url /teams/{id}/channels/{id}/messages

        request_url = self.graph_api_url + uri

        # validate access_token before making API call
        self.validateAccessToken()
        # update session headers with graph api headers
        graph_api_headers = {
            "User-Agent": "fso-python-plugin",
            "Authorization": "Bearer " + self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "SdkVersion": "fso-ms-graph-plugin-{}".format(self.version),
            "x-client-SKU": "fso-ms-graph-plugin",
            "client-request-id": str(uuid.uuid4()),
            "return-client-request-id": "true",
        }

        if custom_headers:
            graph_api_headers.update(custom_headers)

        try:
            if method == 'POST':
                # request a response
                response = self.fso_requests.post(
                    url=request_url,
                    params=params,
                    data=data,
                    json=json_payload,
                    files=files,
                    headers=graph_api_headers
                )
            elif method == 'PUT':
                response = self.fso_requests.put(
                    url=request_url,
                    params=params,
                    data=data,
                    json=json_payload,
                    files=files,
                    headers=graph_api_headers
                )
            elif method == 'DELETE':
                response = self.fso_requests.delete(
                    url=request_url,
                    params=params,
                    data=data,
                    json=json_payload,
                    files=files,
                    headers=graph_api_headers
                )
            elif method == 'GET':
                response = self.fso_requests.get(
                    url=request_url,
                    params=params,
                    headers=graph_api_headers
                )

            self.logger.user_info('status_code : {}, request_url : {}'.format(
                response.status_code, request_url))
        except Exception as e:
            statusMsg = "Failed to make request to url : {}. Error Message : {}".format(
                request_url, e.response.text)
            self.result.error(10004, statusMsg)
            self.result['statusMsg'] = statusMsg
            self.result['success'] = parameters.Bool(False)
            return None

        if stream:
            file_handler = StringIO()
            for content in response.iter_content(decode_unicode=True, chunk_size=1024 * 16):
                try:
                    if content:
                        file_handler.write(content.encode("utf8"))
                except StopIteration:
                    break
            response = file_handler.getvalue()
            file_handler.flush()

        # replace strings problematic for FSO in the response
        if response:
            if output == "json" and response.text:
                response = response.content
                if python_version.major >= 3:
                    response = (
                        response.replace(b'"id":', b'"_id":')
                        .replace(b'"@odata.type":', b'"odata_type":')
                        .replace(b'"from":', b'"whofrom":')
                    )
                else:
                    response = (
                        response.replace('"id":', '"_id":')
                        .replace('"@odata.type":', '"odata_type":')
                        .replace('"from":', '"whofrom":')
                    )
                response = json.loads(response)

        return response

    def _getGroupId(self, teamDisplayName):
        response = self._request(
            method="GET", uri="/groups?$filter=displayName eq('{}')".format(teamDisplayName))
        # check if there is a value in the response
        if response:
            try:
                group_id = response["value"][0]["_id"]
                self.logger.user_info(
                    'Successfully Fetched group_id of teamDisplayName : {}'.format(teamDisplayName))
                return group_id
            except (KeyError, IndexError):
                self.result.error(10005, "Group_id doesn't exist for teamDisplayName : {}. Please check teamDisplayName input.".format(teamDisplayName))
                return None
        # if the response is empty []
        else:
            self.result.error(
                10006, "Group_id doesn't exist for teamDisplayName : {}. Please check teamDisplayName input.".format(teamDisplayName))
            return None

    def _getChannelId(self, group_id, channelDisplayName):
        response = self._request(
            method="GET", uri="/teams/{}/channels?$filter=displayName eq('{}')".format(group_id, channelDisplayName)
        )
        # check if there is a value in the response
        if response:
            try:
                channel_id = response["value"][0]["_id"]
                self.logger.user_info(
                    'Successfully fetched channel_id of channelDisplayname : {}'.format(channelDisplayName))
                return channel_id
            except KeyError:
                self.result.error(10007,
                                  "Failed to find group_id for channelDisplayName : {}. API Response is not in correct format.".format(
                                      channelDisplayName))
        # if the response is empty []
        else:
            self.result.error(
                10008, "channelDisplayName not found: {} ".format(channelDisplayName))
            return None


