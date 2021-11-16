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

from cloudformation_cli_python_lib import (
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    SessionProxy,
    exceptions,
)

from .models import ResourceModel
from .utilities import progress_404


def _read_handler(
    session: SessionProxy,
    model: ResourceModel,
    callback_context: MutableMapping[str, Any],
    logger: Logger,
) -> ProgressEvent:
    logger.debug(f"Requested model to read: {model}")

    org_client = session.client("organizations")

    try:
        policy_targets = [
            target["TargetId"]
            for page in org_client.get_paginator("list_targets_for_policy").paginate(
                PolicyId=model.PolicyId
            )
            for target in page["Targets"]
        ]
        if model.TargetId in policy_targets:
            return ProgressEvent(
                status=OperationStatus.SUCCESS,
                resourceModel=model,
            )
        else:
            return progress_404(
                f"Policy Id {model.PolicyId} is not associated with target {model.TargetId}."
            )
    except org_client.exceptions.PolicyNotFoundException as e:
        return progress_404(f"Policy Id {model.PolicyId} does not exist.")
    except org_client.exceptions.TargetNotFoundException as e:
        logger.error(f"Target {model.TargetId} does not exist")
        return progress_404(f"Target {model.TargetId} does not exist")
    except Exception as e:
        logger.error(f"Could not read Policy association: {e}")
        raise exceptions.InternalFailure(f"Could not read Policy association {e}")
