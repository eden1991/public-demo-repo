#!/usr/bin/env python3

import os
import sys
import csv
import boto3
import shutil
import yaml
import argparse

# Get the full path to the directory currently being executed in
src_dir = os.path.dirname(os.path.abspath(__file__))

# Get the path of the root of the package
parent_dir = os.path.split(src_dir)

def assemble_groups(mapping_file_path):

    '''
    Take a list of role names where the format of a role is PREFIX-ROLE_SOURCESYSTEM
    and group them based on source system.

    Returns a dictionary of groups, where each group contains a list of role names.
    '''

    groups = {}

    # Read the CSV file in to a dictionary
    with open(mapping_file_path, mode="r", encoding="utf-8-sig") as fh:

        rd = csv.DictReader(fh, delimiter=',')

        for row in rd:
            
            role_name = row['IAMRoleName'].replace('-', '_')
            components = role_name.split('_')
            role = components[1]

            # Check if the role exists as a key in the groups dict.
            if role not in groups:

                # Add the role, and initialise a list as its value
                groups.update({role: []})

            # Append source_system in to the role's list
            groups[role].append(row)

    return groups


def create_dir_structure(path):

    '''
    Create directory structure for outputting CFN templates.

    Returns directory path.
    '''

    # Create directory structure if it doesn't exist
    print('Creating directory \'{0}\'...'.format(path))

    try:
        os.makedirs('{0}'.format(path))

    # If it does exist, delete the directory and its contents, and recreate the directory
    except FileExistsError:

        print('Directory \'{0}\' already exists! deleting and re-creating...'.format(path))
        shutil.rmtree('{0}'.format(path))
        os.makedirs('{0}'.format(path))

    print('Successfully created directory \'{0}\'.'.format(path))

    return os.path.isdir(path)

def create_template_file(path, file_name, template):
    
    '''
    Take a path and policy string and generate a yaml file.
    
    Returns the relative file path to the new template.
    '''

    file_path = os.path.join(path, file_name)

    with open(file_path, 'w') as f:

      data = yaml.dump(template, f, sort_keys=False) 

    print("Created " + file_path)

    return file_path

def initialise_template():
  
    '''
    Initialise a dictionary containing a Cloudformation template header.

    Returns a dictionary containing a Cloudformation template header block.
    '''

    full_header_template_path = os.path.join(src_dir, 'yaml_templates', 'base_templates', 'base_template_header.yaml')

    try:
        with open(full_header_template_path) as f_header:

            template_yaml = yaml.load(f_header, Loader=yaml.FullLoader)
            template_yaml['Resources'] = {}

    except FileNotFoundError:

        print("Could not find the template {}. Does it exist?".format(full_header_template_path))

    return template_yaml

def create_role_stub():

    '''
    Initialise a dictionary containing a Cloudformation IAM Role stub.

    Returns a dictionary containing a Cloudformation IAM Role definition stub.
    '''

    full_role_template_path = src_dir+'/yaml_templates/base_templates/base_role_template.yaml'

    try:
        with open(full_role_template_path) as f_role:
            
            base_role_template = yaml.load(f_role, Loader=yaml.FullLoader)
    
    except FileNotFoundError:

        print("Could not find the template {}. Does it exist?".format(full_role_template_path))

    return base_role_template

def populate_new_role(role_stub, role, access_requirement_data):

    '''
    Populate a role_stub, replacing the stubbed values

    Params:
      - role_stub: a stub role object generated by the create_role_stub() function.
      - role: A role name to replace the ROLE_NAME stub.
      - access_requirement_data: A dictionary containing values used for populating stubs.

    Returns 2 items:
        - A dictionary containing a new Cloudformation role resource,
        - The newly created resource name.
    '''

    new_role = role_stub
    components = access_requirement_data['IAMRoleName'].replace('ADFS-', '')
    components = components.split('_')

    # If the role name being evaluated doesn't follow the convention PREFIX-RoleName_System, then
    # just assign the RoleName component
    if len(components) <= 1:
        resource_name = components[0]

    # Assign RoleNameSystem
    else:
        resource_name = components[0] + components[1]

    # Rename the resource in the role stub
    resource = new_role.pop('RESOURCE_NAME')
    new_role[resource_name] = resource

    # Set the role name
    new_role[resource_name]['Properties']['RoleName'] = access_requirement_data['IAMRoleName']

    # Construct the role's inline policy name
    inline_policy_name = resource_name+'BasePolicy'
    
    # Set the role's inline policy name
    new_role[resource_name]['Properties']['Policies'][0]['PolicyName'] = inline_policy_name

    return new_role, resource_name

def construct_managed_policy_arn_list(policy_name_list):

    '''
    Take a list of AWS Managed Policy names and construct their respective Arns

    Returns a list of AWS Managed Policy Arns
    '''

    arn_list = []

    for name in policy_name_list:
        arn = 'arn:aws:iam::aws:policy/' + name
        arn_list.append(arn)

    return arn_list

def create_new_inline_policy(role, platform, aws_service, access_requirement):

    '''
    Initialise a dictionary containing a Cloudformation IAM inline policy stub.

    Params:
      - role: The role that the policy is being generated for e.g. DataAnalyst.
      - platform: The name of the respective platform e.g. Retail.
      - aws_service: The AWS Service being granted permissions to.
      - access_requirement: The suffix to be the appended to the policy resource name.

      The poliy name will be in the format [Role][SourceSystem][Suffix] e.g. DataAnalystRetailQuicksightAthenaAccess

     Returns a dictionary containing a Cloudformation IAM inline policy definition.
    '''

    # Set the base path to the yaml directory
    yaml_templates_path = os.path.join(src_dir, 'yaml_templates', '')

    # Set the base policy template full path
    base_template_path = os.path.join(yaml_templates_path, 'base_templates', 'base_policy_template.yaml')

    # Set the statements template path
    statement_templates_path = os.path.join(yaml_templates_path, 'statement_templates', '')

    new_inline_policy = None

    try:
        with open(base_template_path) as f:
            new_inline_policy = yaml.load(f, Loader=yaml.FullLoader)

    except FileNotFoundError:
        print("Could not find the template {}. Does it exist?".format(base_template_path))

    # Definitions are separated by '|', so split by this separater
    definitions = access_requirement.split('|')

    # Get the Permission level for access e.g. ReadOnly, Full, and remove it from the definitions list
    access_level = definitions.pop(0)

    # 'all' is just a placeholder added in to supplement to the source system part of a role name in certain circumstances. 
    # So, remove it if platform contains this value.
    if platform == 'all':
        platform = ''

    # Establish a new inline policy name
    inline_policy_name = role + platform + aws_service + access_level + 'Access'

    # Rename the policy
    new_inline_policy['PolicyName'] = inline_policy_name

    # Initialise list to hold all the generated statements
    statements = []

    # Iterate through and evaluate each statement
    for definition in definitions:

        statement_stub = None

        # Split out the components 
        component_list = definition.split(';')

        # Get the permission Effect
        effect = component_list[0].split(':')[1]
 
        # Get the resources
        resource_names = component_list[1].split(':')[1].split(',')

        # Get the sources
        source_systems = component_list[2].split(':')[1].split(',')

        # Set the template name to find
        template_name = aws_service + access_level + '.yaml'

        # Get a list of statement templates
        template_list = os.listdir(statement_templates_path)

        # Find the relevant statement based on the aws service and Access Requirement, and Effect
        if (effect.find('Deny') != -1):
            full_statement_path = statement_templates_path +'Deny.yaml'

        else:
            full_statement_path = statement_templates_path + '/' + template_name

        try:
            with open(full_statement_path) as f:
                statement_stub = yaml.load(f, Loader=yaml.FullLoader)

        except FileNotFoundError:
            print("Could not find statement template {}. Does it exist in here?".format(full_statement_path))

        statement_stub['Resource'] = []

        # Add the ARNs in to the resources list
        for name in resource_names:
            for source in source_systems:

                arn = 'arn:aws:{}:::{}/{}'.format(aws_service.lower(), name, source)
                statement_stub['Resource'].append(arn)

        # Append the statement stub to the statements list
        statements.append(statement_stub)

    # Add the list of statements to the policy
    new_inline_policy['PolicyDocument']['Statement'] = statements

    return new_inline_policy

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--configfile', action='store', required=True, metavar='CONFIG_FILE', dest='config_file', help='Specify the configuration file full path.')
    
    return parser.parse_args()

def main():

    # parse command line arguments
    args = parse_args()

    # Set the full file path to the config file
    mapping_file_path = vars(args)['config_file']

    # Create / re-create directory structure
    output_dir = src_dir+'/source-system-templates'
    create_dir_structure(output_dir)

    groups = assemble_groups(mapping_file_path)

    # Iterate through all the groups (roles) compiled above and construct base IAM templates
    for role in groups:

        # Generate a template header
        main_template = initialise_template()

        # Iterate through all the source systems in a group and generate the CFN role yaml
        for access_requirement_data in groups[role]:

            # Create a new role stub
            base_role_stub = create_role_stub()

            # Set the source system
            iam_role_name = access_requirement_data['IAMRoleName'].split('_')

            if len(iam_role_name) <= 1:
                platform = 'all'

            else:
                platform = iam_role_name[1]

            # Update the new role stub with the role and source system being evaluated
            role_resource, resource_name = populate_new_role(
                base_role_stub,
                role,
                access_requirement_data
            )

            for aws_service in access_requirement_data:
                if 'IAMRoleName' not in aws_service:
                    if access_requirement_data[aws_service] != 'FALSE':

                        # Generate the new policy
                        new_policy = create_new_inline_policy(role, platform, aws_service, access_requirement_data[aws_service])
                        
                        # Append the policy to the role resource's list of policies
                        role_resource[resource_name]['Properties']['Policies'].append(new_policy)

            # Add the cfn role resource to the main template
            main_template['Resources'].update(role_resource)

        # Construct the template name
        template_name = role.lower()+'-iam-template.yaml'

        # Generate the template file for this group
        create_template_file(output_dir, template_name, main_template)   


if __name__ == '__main__':
    main()