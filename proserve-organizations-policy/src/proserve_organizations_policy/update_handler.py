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
from typing import Any, MutableMapping  # , Mapping, Optional

import backoff
from cloudformation_cli_python_lib import (  # Action,; HandlerErrorCode,; Resource,; exceptions,; identifier_utils,
    OperationStatus,
    ProgressEvent,
    SessionProxy,
)

from .models import ResourceModel
from .utilities import get_policy, progress_404


def _update_handler(
    session: SessionProxy,
    model: ResourceModel,
    callback_context: MutableMapping[str, Any],
    logger: Logger,
) -> ProgressEvent:
    logger.debug(callback_context)
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModel=model,
        callbackContext=callback_context,
    )

    policy_document = get_policy(model, session, logger)

    org_client = session.client("organizations")
    update_policy_arguments = {
        "PolicyId": model.PolicyId,
        "Content": policy_document,
        "Description": model.Description,
        "Name": model.PolicyName,
    }

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
    def update_policy(args: dict) -> dict:
        return org_client.update_policy(**args)

    try:
        update_response = update_policy(update_policy_arguments)
        logger.debug(update_response)
    except org_client.exceptions.PolicyNotFoundException as e:
        logger.debug(f"Policy Id {model.PolicyId} does not exist.")
        return progress_404(
            f"Policy Id {model.PolicyId} does not exist.", callback_context
        )

    except Exception as e:
        logger.error("Could not update SCP")
        raise e

    # need to check if this works for Tags. then individual tag updates can be done
    # tag_list = model.Tags if previous_state.Tags is None else model.Tags - previous_state.Tags
    # if model.Tags:
    #     if previous_state.Tags:
    #         tag_list = [tag for tag in model.Tags if tag ]
    #     else:
    #         pass

    # tag_resource_arguments["Tags"] = [
    #             {"Key": tag.Key, "Value": tag.Value} for tag in model.Tags
    #         ]

    return progress
