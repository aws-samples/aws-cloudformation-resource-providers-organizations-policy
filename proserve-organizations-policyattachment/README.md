# ProServe::Organizations::PolicyAttachment

A native CloudFormation resource for AWS Organizations Policy Attachments written in python.

## Deployment

Set your AWS credentials to the right account however you prefer and deploy the CloudFormation Resource Type:

```sh
cfn submit -v --region <insert-region-code-here>
```

You might also want to set the default version of the resource like so:

```sh
aws cloudformation set-type-default-version --type "RESOURCE" --type-name "ProServe::Organizations::PolicyAttachment" --version-id "00000001"
```

And now you can deploy a policy association with CloudFormation!

```yaml
Resources:
  Policy1Attachment:
    Type: ProServe::Organizations::PolicyAttachment
    Properties:
      PolicyId: p-12345678
      TargetId: ou-1234-1234asdf

```

## Testing

All commands are executed with the `proserve-organizations-policy` as the current working directory.

Once your preferred python environment is created, install the requirements:

```sh
pip install -r requirements.txt
```

Create the package for the resource type, but do not submit it:

```sh
cfn submit --dry-run
```

Inputs into the test suite are located under `inputs`. Valid properties need to be provided for `PolicyId` and `TargetId` for the tests to complete successfully.

To run the Resource Contract Tests, in one session, run:

```sh
sam local start-lambda
```

and once that is listening, in a second session, run:

```sh
cfn test
```

Detailed outputs will be written to the `rpdk.log` file in the root of repo.
