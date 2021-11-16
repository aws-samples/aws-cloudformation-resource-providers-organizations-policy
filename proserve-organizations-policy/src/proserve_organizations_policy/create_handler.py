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
from logging import Logger
from typing import Any, MutableMapping

import backoff
from cloudformation_cli_python_lib import OperationStatus, ProgressEvent, SessionProxy

from .models import ResourceModel
from .utilities import get_policy


def _create_handler(
    session: SessionProxy,
    model: ResourceModel,
    callback_context: MutableMapping[str, Any],
    logger: Logger,
) -> ProgressEvent:
    logger.debug(callback_context)
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModel=model,
        # callbackContext=callback_context,
    )

    policy_document = get_policy(model, session, logger)

    org_client = session.client("organizations")

    create_policy_arguments = {
        "Content": policy_document,
        "Description": model.Description,
        "Name": model.PolicyName,
        "Type": model.PolicyType,
    }

    # if model.Tags:
    #     create_policy_arguments["Tags"] = [
    #         {"Key": tag.Key, "Value": tag.Value} for tag in model.Tags
    #     ]

    @backoff.on_exception(
        backoff.constant,
        (
            org_client.exceptions.ConcurrentModificationException,
            org_client.exceptions.TooManyRequestsException,
        ),
        jitter=backoff.random_jitter,
        max_time=40,
        interval=1,
    )
    def create_policy(args: dict) -> dict:
        return org_client.create_policy(**args)

    try:
        response = create_policy(create_policy_arguments)
        callback_context["new_policy_id"] = (
            response.get("Policy").get("PolicySummary").get("Id")
        )
        progress.callbackContext = callback_context

    except Exception as e:
        logger.error("Could not create SCP")
        raise e

    return progress
