################################################################################
# © 2021 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at http://aws.amazon.com/agreement or other written
# agreement between Customer and either Amazon Web Services, Inc. or Amazon
# Web Services EMEA SARL or both.
################################################################################
from logging import Logger
from typing import Any, MutableMapping

import backoff
from cloudformation_cli_python_lib import (
    OperationStatus,
    ProgressEvent,
    SessionProxy,
    exceptions,
)

from .models import ResourceModel


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
        callbackContext=callback_context,
    )

    org_client = session.client("organizations")

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
    def attach_policy(policy_id: str, target_id: str) -> dict:
        return org_client.attach_policy(PolicyId=policy_id, TargetId=target_id)

    try:
        response = attach_policy(model.PolicyId, model.TargetId)
        logger.debug(response)
    except org_client.exceptions.DuplicatePolicyAttachmentException as e:
        logger.error("Already attached")
        raise exceptions.AlreadyExists(
            "PolicyAttachment", f"Policy:{model.PolicyId}-Target:{model.TargetId}"
        )
    except Exception as e:
        logger.error("Could not associate Policy with target")
        raise exceptions.InternalFailure(f"{e}")

    return progress
