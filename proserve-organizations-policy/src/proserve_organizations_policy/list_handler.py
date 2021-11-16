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
from .utilities import build_policy_model


def _list_handler(
    session: SessionProxy,
    model: ResourceModel,
    callback_context: MutableMapping[str, Any],
    logger: Logger,
    next_token: str,
) -> ProgressEvent:

    org_client = session.client("organizations")

    try:
        list_policy_args = {"Filter": model.PolicyType, "MaxResults": 10}
        if next_token:
            list_policy_args["NextToken"] = next_token

        policies_response = org_client.list_policies(**list_policy_args)
        # logger.debug(policies_response)
    except Exception as e:
        logger.error("Could not list SCPs")
        raise e

    policies = policies_response.get("Policies")
    resource_models = (
        [build_policy_model(policy) for policy in policies] if policies else []
    )
    logger.debug(f'new next token is {policies_response.get("NextToken")}')
    logger.debug(f"return list of policy models: {resource_models}")
    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModels=resource_models,
        nextToken=policies_response.get("NextToken"),
    )
