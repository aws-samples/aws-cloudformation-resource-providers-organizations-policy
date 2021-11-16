# ProServe::Organizations::Policy

A native CloudFormation resource for AWS Organizations Policies written in python.

## Deployment

Set your AWS credentials to the right account however you prefer and deploy the CloudFormation Resource Type:

```sh
cfn submit -v --region <insert-region-code-here>
```

You might also want to set the default version of the resource like so:

```sh
aws cloudformation set-type-default-version --type "RESOURCE" --type-name "ProServe::Organizations::Policy" --version-id "00000001"
```

And now you can deploy a policy with CloudFormation! `PolicyDocument` and `PolicyUrl` should be mutually exclusive.

```yaml
Resources:
  Policy1:
    Type: ProServe::Organizations::Policy
    Properties:
      PolicyName: CfnSCP
      PolicyType: SERVICE_CONTROL_POLICY
      # PolicyUrl: s3://example-bucket/example_policy.yaml
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Deny
            Action: '*'
            Resource: '*'
      Description: this is a test...yay

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

Inputs into the test suite are located under `inputs` . Two sets of tests are done, one with `PolicyDocument` and another with `PolicyUrl` .

To run the Resource Contract Tests, in one session, run:

```sh
sam local start-lambda
```

and once that is listening, in a second session, run:

```sh
cfn test
```

Detailed outputs will be written to the `rpdk.log` file in the root of repo.
