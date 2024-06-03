#!/bin/env python
# -*- coding: utf-8 -*-

"""
==================================================
   MODULE HEADER
==================================================
 Module Name: Trellix Email Security - Cloud Edition
 Synopsis: Plugin to get Email Security - Cloud Edition Alerts
 Use Case : Threat Analysis based on Alerts from Email Security - Cloud Edition
 Module Author: Prabhat Ranjan
==================================================

==================================================
   MODULE META VARIABLES
==================================================
"""
__plugin_author__ = "Prabhat Ranjan"
__dependency__ = '{"pyfso-saas":"1.0.0"}'
__plugin_notes__ = "Get Alerts from Trellix Email Security - Cloud Edition"
__fso_version__ = "6.0.0"
__plugin_name__ = "Email Security - Cloud Edition"
__display_name__ = "Trellix Email Security"
__plugin_vendor__ = "Trellix"
__plugin_version__ = "1.0.0"
__plugin_categories__ = ("Threat Intelligence",)
__plugin_icon__ = "trellix.png"
__plugin_description__ = """
The Email Security - Cloud Edition platform provides real-time, dynamic threat protection without the use of signatures to protect an organization across the primary threat vectors,
including Web, email, and files, and across the different stages of an attack life cycle. It incorporates an end-user portal that allows quarantine management, as well as review of malicious email and statistics.
This Security Orchestrator plugin enables the retrieval of alerts and message traces based on Message ID.
"""

"""
==================================================
   MODULE IMPORTS
==================================================
"""
# Plugin specific imports
import json
from datetime import datetime, timezone
import requests
# FSO Specific Imports
from iso.data.user_param_types import UserComplexType
from iso.plugins.device import ISODevicePlugin
from iso.data import parameters
from pyfso_saas import (
    FsoRequests,
    handle_errors,
    HANDLE_ERRORS_OUTPUT_PARAMS,
    get_parameters,
    RegexPattern,
)


"""
==================================================
   GLOBAL VARIABLE
==================================================
"""
API_VERSION = 'v1'


"""
==================================================
   COMPLEX TYPES
==================================================
"""


class ETPEmail(UserComplexType):
    __description__ = "response from ETP Message Trace"

    class Data(UserComplexType):
        class Attributes(UserComplexType):
            acceptedDateTime = (parameters.String, "acceptedDateTime")
            countryCode = (parameters.String, "countryCode")
            domain = (parameters.String, "domain")
            downStreamMsgID = (parameters.String, "downStreamMsgID")
            emailSize = (parameters.String, "emailSize")
            lastModifiedDateTime = (parameters.String, "lastModifiedDateTime")
            originalMessageID = (parameters.String, "originalMessageID")
            recipientHeader = (parameters.String.list, "recipientHeader")
            recipientSMTP = (parameters.String.list, "recipientSMTP")
            senderHeader = (parameters.String, "senderHeader")
            senderSMTP = (parameters.String, "senderSMTP")
            senderIP = (parameters.String, "senderIP")
            status = (parameters.String, "status")
            subject = (parameters.String, "subject")
            urlDomains = (parameters.String.list, "urlDomains")

            class Verdicts(UserComplexType):
                AS = (parameters.String, "AS")
                AV = (parameters.String, "AV")
                AT = (parameters.String, "AT")
                PV = (parameters.String, "PV")
                YARA = (parameters.String, "YARA")
                ActionYARA = (parameters.String, "ActionYARA")

            verdicts = (Verdicts, "Verdicts")

            class Internal(UserComplexType):
                timestamp = (parameters.String, "timestamp")
            internal = (Internal, "internal")

        attributes = (Attributes, "Attributes")
        id = (parameters.String, "id")
        type = (parameters.String, "type")
        customer_id = (parameters.String, "customer_id")

        class Included(UserComplexType):
            class Attributes(UserComplexType):
                name = (parameters.String, "name")
            attributes = (Attributes, "attributes")
            type = (parameters.String, "type")

        included = (Included.list, "included")

    data = (Data.list, "Data")

    class Meta(UserComplexType):
        total = (parameters.String, "total")
        copyright = (parameters.String, "copyright")

    meta = (Meta, "Meta")


class ETPMessageRemediate(UserComplexType):
    __description__ = "response from ETP Message Remediate"

    class Data(UserComplexType):
        successful = (parameters.String.list, "successful")
        failed = (parameters.String.list, "failed")

        class FailureReasons(UserComplexType):
            reason = (parameters.String, "reason")
            messageIDs = (parameters.String.list, "message_ids")

        failureReasons = (FailureReasons.list, "failure_reasons")

    data = (Data, "Data")

    class Meta(UserComplexType):
        copyright = (parameters.String, "copyright")

    meta = (Meta, "Meta")


class ETPUrlClickReport(UserComplexType):
    __description__ = "response from ETP URL Click Report"

    class Data(UserComplexType):
        sha256 = (parameters.String, "sha256")
        url = (parameters.String, "url")
        url_click_missed = (parameters.Integer.list, "url_click_missed")
        url_click_blocked = (parameters.Integer.list, "url_click_blocked")

    data = (Data, "Data")

    class Meta(UserComplexType):
        copyright = (parameters.String, "copyright")

    meta = (Meta, "Meta")
    type = (parameters.String, "type")


"""
==================================================
   ERROR HANDLING
==================================================
"""


class ETPError(Exception):
    pass


class ETPException(Exception):
    pass


class MissingRequiredParameter(Exception):
    pass


class ValidationError(Exception):
    pass


"""
==================================================
   CUSTOM ERROR HANDLING
==================================================
"""
CUSTOM_ERRORS = [
    {
        "exception": ETPError,
        "trace": "ETPError: [{}]",
        "status_msg": "ETPError: [{}]",
        "task_success": False,
        "success": True,
    },
    {
        "exception": ETPException,
        "trace": "ETPException: [{}]",
        "status_msg": "ETPException: [{}]",
        "task_success": False,
        "success": True,
    },
    {
        "exception": MissingRequiredParameter,
        "trace": "MissingRequiredParameter: [{}]",
        "status_msg": "MissingRequiredParameter: [{}]",
        "task_success": False,
        "success": True,
    },
    {
        "exception": ValidationError,
        "trace": "ValidationError: [{}]",
        "status_msg": "ValidationError: [{}]",
        "task_success": False,
        "success": True,
    },
    {
        "exception": KeyError,
        "trace": "KeyError : [{}]",
        "status_msg": "KeyError : [{}]",
        "task_success": False,
        "success": True,
    }
]

"""
==================================================
   PLUGIN CLASS
==================================================
"""


class TrellixETP(ISODevicePlugin):
    """Plugin Device Class"""

    version = __plugin_version__
    name = __plugin_name__
    display_name = __display_name__
    vendor = __plugin_vendor__
    description = __plugin_description__
    categories = __plugin_categories__
    icon = __plugin_icon__

    """
    Plugin Device Parameters
    ===========================
    """
    pluginParameters = (
        ISODevicePlugin.Parameter(
            name="url",
            description="URL of cloud Email Security Server, example: https://etp.us.fireeye.com. Accept valid URL only",
            typ=parameters.String,
            properties={
                "regex_pattern": RegexPattern.URL,
            }
        ),
        ISODevicePlugin.Parameter(
            name="api_key",
            description="ETP API key",
            typ=parameters.String,
            encrypted=True,
        ),
    )

    """
    Plugin Command Definitions
    ===========================
    """
    commands = (
        ISODevicePlugin.Command(
            name="retrieve_message",
            description="Retrieves the particular message with the specified Email Security message ID.",
            manualTimeToCompleteInSec=60,
            actionName="Retrieve",
            targetName="Message",
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    typ=parameters.String.list,
                    name="message_id",
                    description="The ID of the Email Security message.",
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.String,
                    name="traffic_type",
                    description="The direction of the email traffic.Accepted value are (inbound, outbound)",
                    value="inbound",
                    properties={
                        "choices": [
                            {"label": "Inbound", "value": "inbound"},
                            {"label": "Outbound", "value": "outbound"},
                        ],
                        "optional": True,
                    },
                ),
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.email_security.ETPEmail.list,
                    name="etp_email",
                    description="User ComplexType of Email Security Message Trace",
                    properties={"optional": True},
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.JSON,
                    name="raw_json",
                    description="Email Security Message Trace Raw Response",
                    properties={"optional": True},
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String.list,
                    name="retrieved_message_ids",
                    description="List of message id, for which message retrieved",
                    properties={"optional": True},
                ),
            ) + HANDLE_ERRORS_OUTPUT_PARAMS,
            summaryParameterNames=(
                "etp_email", "retrieved_message_ids", "raw_json", "task_success", "status_msg", "response_code"
            ),
        ),
        ISODevicePlugin.Command(
            name="email_search",
            description="Retrieves email trace information as per the attributes and traffic type that are accessible "
                        "in the Email Security.Each input parameters can have max of 10 values",
            manualTimeToCompleteInSec=60,
            actionName="Email",
            targetName="Search",
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    typ=parameters.String.list,
                    name="from_email",
                    description="List of senders email.Accept valid emails only",
                    properties={
                        "optional": True,
                        "regex_pattern": RegexPattern.EMAIL,
                    },
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.String.list,
                    name="recipients",
                    description="List of recipients.Accept valid emails only",
                    properties={
                        "optional": True,
                        "regex_pattern": RegexPattern.EMAIL,
                    },
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.String,
                    name="subject",
                    description="The subject of email",
                    properties={"optional": True},
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.String,
                    name="from_time",
                    description="Timestamp search start. Please provide time in ISO8601 format. (eg. "
                                "'2024-01-02T15:04:05.000z').Both 'from_time' and 'to_time' are required fields to "
                                "specify the datetime range for the search.",
                    properties={
                        "optional": True,
                        "regex_pattern": RegexPattern.DATETIME.ISO_8601_DATETIME,
                    },
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.String,
                    name="to_time",
                    description="Timestamp search stop. Please provide time in ISO8601 format. (eg. "
                                "2024-01-02T15:04:05.000z).Both 'from_time' and 'to_time' are required fields to "
                                "specify the datetime range for the search. If 'from_time' is provided but 'to_time' "
                                "is not, the current datetime will be used as the end time.",
                    properties={
                        "optional": True,
                        "regex_pattern": RegexPattern.DATETIME.ISO_8601_DATETIME,
                    },
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.String,
                    name="status",
                    description="email status. Accepted values are: (accepted, deleted, delivered, delivered ("
                                "retroactive), dropped, dropped oob, dropped (oob retroactive), permanent failure, "
                                "processing, quarantined, rejected, temporary failure, scanned, scan bypassed, split)",
                    properties={
                        "optional": True,
                        "choices": [
                            {"label": "accepted", "value": "accepted"},
                            {"label": "deleted", "value": "deleted"},
                            {"label": "delivered", "value": "delivered"},
                            {"label": "dropped", "value": "dropped"},
                            {"label": "temporary_failure", "value": "temporary failure"},
                            {"label": "scanned", "value": "scanned"},
                            {"label": "scan_bypassed", "value": "scan bypassed"},
                            {"label": "split", "value": "split"},
                            {"label": "dropped_oob", "value": "dropped oob"},
                            {"label": "permanent_failure",
                                "value": "permanent failure"},
                            {"label": "processing", "value": "processing"},
                            {"label": "quarantined", "value": "quarantined"},
                            {"label": "rejected", "value": "rejected"},
                            {"label": "delivered_retroactive",
                                "value": "delivered (retroactive)"},
                            {"label": "dropped_oob_retroactive",
                                "value": "dropped (oob retroactive)"},
                        ]
                    },
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.Bool,
                    name="has_attachment",
                    description="Mark true if email contains attachment",
                    properties={"optional": True},
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.Float,
                    name="min_message_size",
                    description="Minimum size of the email.Accept positive float only",
                    properties={
                        "optional": True,
                        "regex_pattern": RegexPattern.FLOAT,
                    },
                    value=0,
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.Float,
                    name="max_message_size",
                    description="Maximum size of the email.Accept positive float only",
                    properties={
                        "optional": True,
                        "regex_pattern": RegexPattern.FLOAT,
                    },
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.String.list,
                    name="sender_ip",
                    description="List of sending SMTP IPs.Accept valid ip_addresses only",
                    properties={
                        "optional": True,
                        "regex_pattern": RegexPattern.IP_ADDRESS,
                    },
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.String.list,
                    name="domains",
                    description="List of domains. Accept valid domains only",
                    properties={
                        "optional": True,
                        "regex_pattern": RegexPattern.DOMAIN,
                    },
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.Integer,
                    name="limit",
                    description="Max number of emails to return.Default is 20.Accept positive integer only",
                    properties={
                        "optional": True,
                        "regex_pattern": RegexPattern.INT,
                    },
                    value=20,
                )
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.email_security.ETPEmail,
                    name="etp_email",
                    description="User ComplexType of Email Security Email Trace",
                    properties={"optional": True},
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.JSON,
                    name="raw_json",
                    description="Email Security Email Trace Raw Response",
                    properties={"optional": True},
                ),
            ) + HANDLE_ERRORS_OUTPUT_PARAMS,
            summaryParameterNames=(
                "etp_email", "raw_json", "task_success", "status_msg", "response_code"
            ),
        ),
        ISODevicePlugin.Command(
            name="message_remediate",
            description="Remediates messages in ETP by specified Message IDs",
            manualTimeToCompleteInSec=60,
            actionName="Message",
            targetName="Remediate",
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    typ=parameters.String.list,
                    name="message_id",
                    description="The ID of the Email Security message.",
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.String,
                    name="action",
                    description="The action to take on the message IDs, accepted values are (quarantine, move, "
                                "delete). If action selected as move, then move_to is required parameter",
                    value="quarantine",
                    properties={
                        "choices": [
                            {"label": "Quarantine", "value": "quarantine"},
                            {"label": "Move", "value": "move"},
                            {"label": "Delete", "value": "delete"},
                        ],
                    },
                ),
                ISODevicePlugin.InputParameter(
                    typ=parameters.String,
                    name="move_to",
                    description="The folder to move message to in the users inbox.If "
                                "action selected as move, then move_to is required parameter",
                    properties={"optional": True},
                ),
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.email_security.ETPMessageRemediate,
                    name="remediate_response",
                    description="User ComplexType of Email Security Message Remediate",
                    properties={"optional": True},
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.String.list,
                    name="remediated_message_ids",
                    description="List of message IDs for emails that have been remediated",
                    properties={"optional": True},
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.JSON,
                    name="raw_json",
                    description="Email Security Message Remediate Raw Response",
                    properties={"optional": True},
                ),
            ) + HANDLE_ERRORS_OUTPUT_PARAMS,
            summaryParameterNames=(
                "remediate_response", 
                "remediated_message_ids",
                "raw_json", 
                "task_success", 
                "status_msg", 
                "response_code"
            ),
        ),
        ISODevicePlugin.Command(
            name="url_click_report",
            description="Retrieves URL click reports",
            manualTimeToCompleteInSec=60,
            actionName="Get",
            targetName="UrlClickReport",
            inputParameters=(
                ISODevicePlugin.InputParameter(
                    typ=parameters.String,
                    name="alert_id",
                    description="The ID of the Advance threat alert",
                ),
            ),
            outputParameters=(
                ISODevicePlugin.OutputParameter(
                    typ=parameters.email_security.ETPUrlClickReport,
                    name="url_click_report",
                    description="User ComplexType of Email Security URL Click Report",
                    properties={"optional": True},
                ),
                ISODevicePlugin.OutputParameter(
                    typ=parameters.JSON,
                    name="raw_json",
                    description="URL click report Raw Response",
                    properties={"optional": True},
                ),
            ) + HANDLE_ERRORS_OUTPUT_PARAMS,
            summaryParameterNames=(
                "url_click_report", 
                "raw_json", 
                "task_success", 
                "status_msg", 
                "response_code"
            ),
        ),
    )

    # Init Constructor
    def __init__(self, *args, **kwargs):
        super(TrellixETP, self).__init__(*args, **kwargs)
        base_url = get_parameters(self, "url", regex_pattern=RegexPattern.URL).rstrip("/")
        self.base_url = f"{base_url}/api/{API_VERSION}"
        self.session = FsoRequests(
            device=self,
            verify_certs=False,
            headers={
                "Content-Type": "application/json",
                "x-fireeye-api-key": get_parameters(self, "api_key"),
            },
            default_timeout=120,
        )

        self.result = self.makeResult()
        self.result.success = True
        self.result["status_msg"] = parameters.String("Task execution Successful")
        self.result["task_success"] = parameters.Bool(True)

    """
    Plugin Task Methods
    ===========================
    """

    @handle_errors(custom=CUSTOM_ERRORS)
    def testDevice(self):
        """testDevice"""
        self.result.trace("Running testDevice Task")
        try:
            api_endpoint = "/alerts"
            self._make_http_request(
                "POST", api_endpoint, json_payload={"size": 2}
            )
            self.result.trace("Running testDevice task: Success!")
            self.result["task_success"] = parameters.Bool(True)
            self.result["status_msg"] = parameters.String(
                "Running testDevice task: Success!")
            self.result.success = True
        except ETPException as etp_exc:
            raise ETPException(str(etp_exc))
        except ETPError as etp_err:
            raise ETPError(str(etp_err))
        except Exception as exc:
            raise Exception(str(exc))

        return self.result

    @handle_errors(custom=CUSTOM_ERRORS)
    def retrieve_message(self, request):
        """
        Returns the attributes of a particular message with the specified Email Security message ID.
        """
        # Get IDs
        etp_message_ids = get_parameters(request, "message_id", is_list=True)
        traffic_type = get_parameters(request, "traffic_type")
        if traffic_type not in ["inbound", "outbound"]:
            raise ValidationError("accepted value of traffic_type is inbound or outbound")
        # Set Params
        params = {"traffic_type": traffic_type}

        # Empty collections
        result_list = []
        raw_json_list = []
        msg_ids_not_found = []
        retrieved_message_ids = []
        for msg_id in etp_message_ids:
            try:
                api_endpoint = f"/messages/{msg_id}"
                # Make request
                response = self._make_http_request("GET", api_endpoint, params)
                result_list.append(response.json(strict=False))
                raw_json_list.append(response.json())
                retrieved_message_ids.append(msg_id)
            except (ETPException, ETPError):
                self.result.error(1001, f"MessageID : {msg_id} not found!")
                msg_ids_not_found.append(msg_id)
            except Exception as exc:
                self.result.error(
                    1002, f"Failed to fetch message for messageID : {msg_id}")
                raise Exception(exc)
        
        self.result["etp_email"] = parameters.email_security.ETPEmail.list(
            result_list)
        self.result["retrieved_message_ids"] = parameters.String.list(retrieved_message_ids)
        self.result["raw_json"] = parameters.JSON(json.dumps(raw_json_list))
        self.result["task_success"] = parameters.Bool(True)
        if msg_ids_not_found:
            status_msg = ", ".join(
                f"MessageID {msg_id} : Not found" for msg_id in msg_ids_not_found)
        else:
            status_msg = "Successfully fetched all the messageID"
        self.result["status_msg"] = parameters.String(status_msg)
        del self.result["response_code"]
        return self.result

    @handle_errors(custom=CUSTOM_ERRORS)
    def email_search(self, request):
        """
        This API retrieves email trace information as per the attributes and traffic type that are accessible in the Email Security.
        """
        self.result.trace("Running email_search Task!")

        limit = get_parameters(request, "limit", regex_pattern=RegexPattern.INT)

        # Set Params
        payload = {
            "attributes": _get_attributes_for_email_search(request),
        }

        if limit is not None:
            if limit <= 0:
                raise ValidationError("limit can not be less than 1")
            payload["size"] = limit

        # Make request
        try:
            self.result.trace(f"payload :{payload}")
            response = self._make_http_request(
                "POST", "/messages/trace",
                json_payload=payload
            )
            # Set Output Params
        
            self.result["etp_email"] = parameters.email_security.ETPEmail(
                response.json(strict=False)
            )
            self.result["raw_json"] = parameters.JSON(response.text)
            data = response.json().get('data')
            if data is not None:
                total_emails = len(data)
                self.result.trace(f"Found total {total_emails} email")
            else:
                self.result.trace("No email data found")
            # self.logger.user_info(f"response : {response.json()}")
            self.result["status_msg"] = parameters.String(
                "Successfully retrieved the messages.")
            self.result["task_success"] = parameters.Bool(True)
        except ValidationError as err:
            raise ValidationError(err)
        except ETPException as etp_exc:
            raise ETPException(etp_exc)
        except ETPError as etp_err:
            raise ETPError(etp_err)
        except Exception as error:
            self.result.error(
                41703, "Failed email Search. ERROR: {}".format(error)
            )
            raise Exception(str(error))

        return self.result

    @handle_errors(custom=CUSTOM_ERRORS)
    def message_remediate(self, request):
        """
        Enqueues the message IDs provided in the request for remediation from the user's o365 inbox.
        """
        self.result.trace("Running message_remediate Task!")

        action = get_parameters(request, "action")
        if action not in ["quarantine", "move", "delete"]:
            raise ValidationError("valid action are quarantine, move, action")

        # Set Params
        payload = {
            "message_ids": get_parameters(request, "message_id", is_list=True),
            "action_override": action
        }

        if action == "move":
            move_to = get_parameters(request, "move_to")

            if not move_to:
                raise MissingRequiredParameter("Required Parameter move_to is missing. Action move was selected but "
                                               "no move to location was given")
            else:
                payload["move_to"] = move_to

        api_endpoint = "/messages/remediate"
        # Make request
        try:
            response = self._make_http_request(
                "POST", api_endpoint, json_payload=payload)
            response_json = response.json(strict=False)
            self.result["remediate_response"] = parameters.email_security.ETPMessageRemediate(
                response_json
            )
            successful_msg_ids = response_json["data"]["successful"]
            failed_msg_ids = response_json["data"]["failed"]
            if failed_msg_ids:
                status_msg = f"Message remediate failed for {'.'.join(failed_msg_ids)}"
                success = False
            else:
                status_msg = "Successfully remediated the message"
                success = True
            if successful_msg_ids:
                self.result["remediated_message_ids"] = parameters.String.list(successful_msg_ids)
            self.result["raw_json"] = parameters.JSON(response.text)
            self.result["status_msg"] = parameters.String(status_msg)
            self.result["task_success"] = parameters.Bool(success)
        except ETPException as etp_exc:
            raise ETPException(str(etp_exc))
        except ETPError as etp_err:
            raise ETPError(str(etp_err))
        except Exception as exc:
            raise Exception(str(exc))

        return self.result

    @handle_errors(custom=CUSTOM_ERRORS)
    def url_click_report(self, request):
        """
        Returns the URL click report for particular alert ID
        """
        self.result.trace("Running url_click_report Task!")

        alert_id = get_parameters(request, "alert_id")
        api_endpoint = f"/alerts/urlclickreport?alert_id={alert_id}"

        try:
            response = self._make_http_request("GET", api_endpoint)
            # Set Output Params
            
            self.result["url_click_report"] = parameters.email_security.ETPUrlClickReport(
                response.json(strict=False)
            )
            self.result["raw_json"] = parameters.JSON(response.text)
            self.result["status_msg"] = parameters.String(
                "Successfully fetched url click report.")
            self.result["task_success"] = parameters.Bool(True)
        except ETPException as etp_exc:
            raise ETPException(str(etp_exc))
        except ETPError as etp_err:
            raise ETPError(str(etp_err))
        except Exception as exc:
            raise Exception(str(exc))

        return self.result

    # ===============================================
    # Begin Core Task Logic Handlers and Helpers
    # ===============================================

    def _make_http_request(self, method, api_endpoint, params=None, json_payload=None, data=None):
        try:
            response = self.session.request(
                method=method,
                url=f"{self.base_url}{api_endpoint}",
                params=params,
                data=data,
                json=json_payload,
            )
            response.raise_for_status()
            self.result['response_code'] = parameters.Integer(
                response.status_code)
            return response
        except requests.exceptions.HTTPError as err:
            self.result.error(10001, err.response.json())
            self.result['response_code'] = parameters.Integer(
                err.response.status_code)
            raise ETPError(str(err))
        except requests.exceptions.RequestException as err:
            self.result.error(10002, err)
            self.result['response_code'] = parameters.Integer(
                err.response.status_code)
            raise ETPException(str(err))
        except Exception as exc:
            raise Exception(str(exc))


def _get_attributes_for_email_search(request):
    from_email_list = get_parameters(request, "from_email", is_list=True, regex_pattern=RegexPattern.EMAIL)
    recepients_list = get_parameters(request, "recepients", is_list=True, regex_pattern=RegexPattern.EMAIL)
    subject = get_parameters(request, "subject")
    from_time = get_parameters(request, "from_time", regex_pattern=RegexPattern.DATETIME.ISO_8601_DATETIME)
    to_time = get_parameters(request, "to_time", regex_pattern=RegexPattern.DATETIME.ISO_8601_DATETIME)
    status = get_parameters(request, "status")
    has_attachment = get_parameters(request, "has_attachment")
    min_message_size = get_parameters(request, "min_message_size", regex_pattern=RegexPattern.FLOAT)
    max_message_size = get_parameters(request, "max_message_size", regex_pattern=RegexPattern.FLOAT)
    sender_ip_list = get_parameters(request, "sender_ip", regex_pattern=RegexPattern.IP_ADDRESS)
    domains_list = get_parameters(request, "domains", is_list=True, regex_pattern=RegexPattern.DOMAIN)

    attributes = {}
    if from_email_list:
        attributes["fromEmail"] = {
            "value": from_email_list, "filter": "in", "includes": ["SMTP"]
        }

    if recepients_list:
        attributes["recipients"] = {
            "value": recepients_list, "filter": "in", "includes": ["SMTP", "HEADER"]
        }

    if subject:
        attributes["subject"] = {
            "value": [subject], "filter": "in"
        }

    if from_time is not None:
        if to_time is None:
            to_time = get_current_date_time()
        attributes["period"] = {
            "range": {
                "fromAcceptedDateTime": from_time,
                "toAcceptedDateTime": to_time
            }
        }
    else:
        if to_time is not None:
            raise ValidationError("If a 'to_time' is provided, 'from_time' must also be specified")

    if status:
        if status not in ["accepted", "deleted", "delivered", "delivered (retroactive)", "dropped", "dropped oob", "dropped (oob retroactive)", "permanent failure", "processing", "quarantined", "rejected", "temporary failure", "scanned", "scan bypassed", "split"]:
            raise ValidationError(f"Value is not acceptable {status} for status.")
        attributes["status"] = {
            "value": [status], "filter": "in"
        }

    if has_attachment:
        attributes["hasAttachment"] = {
            "value": has_attachment
        }

    if isinstance(min_message_size, float) or isinstance(max_message_size, float):
        if "messageSize" not in attributes:
            attributes["messageSize"] = {}

        if isinstance(min_message_size, float):
            if min_message_size < 0:
                raise ValidationError("min_message_size can't be less than zero")
            attributes["messageSize"]["min"] = min_message_size

        if isinstance(max_message_size, float):
            if max_message_size < 0:
                raise ValidationError("max_message_size can't be less than zero")
            elif max_message_size == 0:
                raise ValidationError("mas_message_size can't be zero")
            attributes["messageSize"]["max"] = max_message_size

    if sender_ip_list:
        attributes["senderIP"] = {
            "value": sender_ip_list, "filter": "in"
        }

    if domains_list:
        attributes["domains"] = {
            "value": domains_list, "filter": "in"
        }

    return attributes


# current date time in iso8601 format (eg. 2024-06-03T02:40:05.690z)
def get_current_date_time():
    # Get the current datetime in UTC timezone
    current_datetime = datetime.now(timezone.utc)

    # Format the datetime object to the desired format
    return current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'z'


