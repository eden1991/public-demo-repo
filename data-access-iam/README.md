# What

This python script is designed to take a csv file consisting of the various roles required for data platform access, iterate through them and generate IAM Roles/Policies that are used to control access to the data platform data sources. 

## Usage

1. Make changes to the role_policy_mapping.csv config file.
    * Add a new row for a role, formatting the name like so `PREFIX-ROLE_SOURCESYSTEM` e.g. `ADFS-Role1_Sys1`, and add the desired permissions under the column of the service being granted to. 
    * Add a new service by adding in a new column, following the format of the existing serices.
2. Execute the python script `src/role_maker.py` and pass in the aforementioned .csv config file e.g. `python3 role_maker.py -f role_policy_mapping.csv`.
3. Upload the generated cloud formation templates from the newly created folder to S3.
4. Deploy or update a stack by pointing to the template object's S3 URL.

## Permissions definition format

At present, the tool supports adding S3 IAM permissions. This can be extended to accommodate other services but will require some tweaking. For now, the following format defines a policy under the S3 column:

`<AccessType|>Effect:<effect>;resources:<resources>;sources<sources>`

The definition keys take the following values:
* <AccessType>: ReadOnly, Full
* Effect: Allow, Deny
* resources: S3 bucket names separated by commas.
* sources: S3 bucket directories, separated by commas.
    * Nested directories can be added by using forward slashes e.g. `dir/nestedDir`.

The separators do the following:
* `|` - Bars separate all the role components as well as the AccessType (which always goes first at the start of a defintion), e.g: `AccessType|Effect;resources;sources|Effect;resources;sources`
* `;` - Semi-colons separate the statement attributes e.g. `|;resources;sources|`
* `:` - Colons separate Keys from Values within a statement component. `|;resources:resource1,resource2;sources:source1,source2`

This is an example of a full definition example:
    `ReadOnly|Effect:Allow;resources:non-prod-raw-zone;sources:sys1/*,sys2/*,sys3/*|Effect:Deny;resources:non-prod-raw-zone;sources:danger/zone`

The above definition will grant readonly access to:
* non-prod-raw-zone/sys1/*
* non-prod-raw-zone/sys2/*
* non-prod-raw-zone/sys3/*

And will explicitly Deny access to:
* non-prod-raw-zone/danger/zone

The asterisk (*) means 'recursively include all sub directories and files'.

## Uploading CF Templates

Ideally uploading the templates should be performed using the AWS-CLI tool and the supporting `makefile`.

There are a couple of ways to do this. One way is to open the AWS console and navigate to CloudFormation. From this page select the relevant existing stack. Click `Update`. Select `Replace Current Template` and then `Upload a template file`. `Choose File` and select the relevant, newly generated file from the working directory.
