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
import io
import json
from typing import Optional
from urllib.parse import urlparse

from cloudformation_cli_python_lib import (
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    SessionProxy,
)

from .models import ResourceModel  # , set_or_none, T

# def get_policy_tags(client, policy_id: str ) -> Optional[AbstractSet[T]]:
#     return set_or_none(
#                 (
#                     tag
#                     for page in client.get_paginator(
#                         "list_tags_for_resource"
#                     ).paginate(
#                         ResourceId=policy_id,
#                     )
#                     for tag in page["Tags"]
#                 )
#             )


def build_policy_model(policy_summary: dict) -> Optional[ResourceModel]:
    # policy_tags = get_policy_tags(policy_summary.get("Id"))
    policy_model = ResourceModel(
        PolicyName=policy_summary.get("Name"),
        PolicyType=policy_summary.get("Type"),
        PolicyDocument=None,
        PolicyUrl=None,
        Description=policy_summary.get("Description"),
        PolicyId=policy_summary.get("Id"),
        Arn=policy_summary.get("Arn"),
        # Tags=policy_tags,
    )
    return policy_model


def get_s3_object(session: SessionProxy, s3_url: str) -> str:
    client = session.client("s3")
    buffer = io.BytesIO()
    parsed_uri = urlparse(s3_url)
    # print(parsed_uri)
    client.download_fileobj(
        Bucket=parsed_uri.netloc, Key=parsed_uri.path[1:], Fileobj=buffer
    )
    return buffer.getvalue().decode()


def get_policy(model, session, logger):
    if model.PolicyUrl:
        logger.debug(f"Trying to download: {model.PolicyUrl}")
    try:
        policy_document = (
            get_s3_object(session, model.PolicyUrl)
            if model.PolicyUrl
            else json.dumps(model.PolicyDocument)
        )
    except Exception as e:
        logger.exception("Could not download policy document from S3.")
        raise e
    return policy_document


def progress_404(message: str = "Not Found", call_back_context={}) -> ProgressEvent:
    return ProgressEvent(
        status=OperationStatus.FAILED,
        errorCode=HandlerErrorCode.NotFound,
        message=message,
        callbackContext=call_back_context,
    )
