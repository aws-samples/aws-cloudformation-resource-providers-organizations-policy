# ProServe::Organizations::PolicyAttachment

Attaches a policy to a defined target.

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "ProServe::Organizations::PolicyAttachment",
    "Properties" : {
        "<a href="#policyid" title="PolicyId">PolicyId</a>" : <i>String</i>,
        "<a href="#targetid" title="TargetId">TargetId</a>" : <i>String</i>
    }
}
</pre>

### YAML

<pre>
Type: ProServe::Organizations::PolicyAttachment
Properties:
    <a href="#policyid" title="PolicyId">PolicyId</a>: <i>String</i>
    <a href="#targetid" title="TargetId">TargetId</a>: <i>String</i>
</pre>

## Properties

#### PolicyId

The unique identifier (ID) of the policy that you want to attach to the target.

_Required_: Yes

_Type_: String

_Pattern_: <code>^p-[a-zA-Z0-9_]{8,128}$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### TargetId

The unique identifier (ID) of the root, OU, or account that you want to attach the policy to. You can get the ID by calling the ListRoots , ListOrganizationalUnitsForParent , or ListAccounts operations.

_Required_: Yes

_Type_: String

_Pattern_: <code>^([0-9]{12}|r-[a-zA-Z0-9_]{4,32}|ou-[a-zA-Z0-9_]{4,32}-[a-zA-Z0-9_]{8,32})$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

