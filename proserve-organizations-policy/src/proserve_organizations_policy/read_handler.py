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

from cloudformation_cli_python_lib import OperationStatus, ProgressEvent, SessionProxy

from .models import ResourceModel
from .utilities import build_policy_model, progress_404


def _read_handler(
    session: SessionProxy,
    model: ResourceModel,
    callback_context: MutableMapping[str, Any],
    logger: Logger,
) -> ProgressEvent:
    logger.debug(f"Requested model to read: {model}")
    logger.debug(callback_context)

    if callback_context.get("new_policy_id"):
        policy_id = callback_context.get("new_policy_id")
    elif model.PolicyId:
        policy_id = model.PolicyId
    else:
        logger.error("No policy id is available, nothing to read.")
        return progress_404(
            "Policy Id not found in model or context. Policy creation failed."
        )

    org_client = session.client("organizations")

    try:
        policy_response = org_client.describe_policy(PolicyId=policy_id)
        logger.debug(policy_response)
        policy = policy_response.get("Policy")
        if policy:
            policy_model = build_policy_model(policy["PolicySummary"])
        else:
            return progress_404(f"Policy Id {policy_id} does not exist.")
    except org_client.exceptions.PolicyNotFoundException as e:
        return progress_404(f"Policy Id {policy_id} does not exist.")
    except Exception as e:
        logger.error("Could not read SCP")
        raise e

    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModel=policy_model,
    )
