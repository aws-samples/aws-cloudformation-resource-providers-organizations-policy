# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import logging
import re
from typing import Any, MutableMapping, Optional

from cloudformation_cli_python_lib import (
    Action,
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
    exceptions,
    identifier_utils,
)

from .create_handler import _create_handler
from .delete_handler import _delete_handler
from .list_handler import _list_handler
from .models import ResourceHandlerRequest, ResourceModel
from .read_handler import _read_handler
from .update_handler import _update_handler

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel("DEBUG")
TYPE_NAME = "ProServe::Organizations::Policy"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint


@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState

    LOG.debug(f"received create request: {request}")

    if model.Arn or model.PolicyId:
        progress: ProgressEvent = ProgressEvent(
            status=OperationStatus.FAILED,
            resourceModel=model,
        )
        LOG.debug("Readonly properties passed into create. Invalid request.")
        return progress.failed(
            HandlerErrorCode.InvalidRequest,
            "Read only properties passed into create. Invalid Request.",
        )

    try:
        # setting up random primary identifier compliant with cfn standard

        if not model.PolicyName:
            primary_identifier = identifier_utils.generate_resource_identifier(
                stack_id_or_name=request.stackId,
                logical_resource_id=request.logicalResourceIdentifier,
                client_request_token=request.clientRequestToken,
                max_length=128,
            )
            model.PolicyName = primary_identifier
        if isinstance(session, SessionProxy):
            progress = _create_handler(session, model, callback_context, LOG)
            return read_handler(session, request, progress.callbackContext)

        else:
            LOG.error("No session available")
            raise Exception("No session available")

    except Exception as e:
        # exceptions module lets CloudFormation know the type of failure that occurred
        raise exceptions.InternalFailure(f"was not expecting {e}")
        # this can also be done by returning a failed progress event
        # return ProgressEvent.failed(HandlerErrorCode.InternalFailure, f"was not expecting type {e}")


@resource.handler(Action.UPDATE)
def update_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    LOG.debug(f"received update request: {request}")
    model = request.desiredResourceState
    # existing_tags = request.previousResourceState
    if isinstance(session, SessionProxy):
        progress = _update_handler(session, model, callback_context, LOG)
    return read_handler(session, request, progress.callbackContext)


@resource.handler(Action.DELETE)
def delete_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    LOG.debug(f"received delete request: {request}")
    model = request.desiredResourceState

    policy_id_match = re.match("^p-[a-zA-Z\d_]{8,128}$", model.PolicyId)

    if not policy_id_match:
        progress_event = ProgressEvent(
            status=OperationStatus.FAILED,
        )
        return progress_event.failed(
            HandlerErrorCode.InvalidRequest, "Policy Id does not match regex."
        )

    if isinstance(session, SessionProxy):
        progress = _delete_handler(session, model, callback_context, LOG)
    else:
        LOG.error("No session available")
        raise Exception("No session available")
    return progress


@resource.handler(Action.READ)
def read_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    LOG.debug(f"received read request: {request}")
    model = request.desiredResourceState
    if isinstance(session, SessionProxy):
        progress = _read_handler(session, model, callback_context, LOG)
    else:
        LOG.error("No session available")
        raise Exception("No session available")
    return progress


@resource.handler(Action.LIST)
def list_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    LOG.debug(f"list request: {request}")
    LOG.debug(f"list initial callback_context: {callback_context}")
    model = request.desiredResourceState
    next_token = request.nextToken

    LOG.debug(f"next token is:{next_token}.")
    if isinstance(session, SessionProxy):
        progress = _list_handler(session, model, callback_context, LOG, next_token)
    else:
        LOG.error("No session available")
        raise Exception("No session available")
    return progress
