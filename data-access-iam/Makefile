# Usage:

bucket = dataplatform-iam-templates
directory = source-system-templates
full_path = s3://${bucket}/${directory}
local_templates_directory = src/source-system-templates

read_me:
	@echo "Usage:"
	@echo "make					Display this Readme"
	@echo "make role_maker				Run the src/role_maker.py script to generate the IAM templates"	
	@echo "make re_upload_templates		Delete all templates in the S3 path and re-upload the local templates"
	@echo "make remove_templates 	 		Delete all templates in the S3 path"
	@echo "make upload_templates			Upload all the local templates to the S3 path"
	@echo "make deploy_templates			Deploy new stacks from all the templates in full_path"
	@echo "make deploy_<ROLE_NAME>_template	Deploy a new stack from the specified template located in the S3 path"


role_maker:
	python3 src/role_maker.py -f role_policy_mapping.csv

re_upload_templates: remove_templates upload_templates
	@echo "Re-uploading templates.."

remove_templates:
	@echo "Deleting old templates from ${full_path}"
	@aws s3 rm ${full_path} --recursive

upload_templates:
	@echo "Copying new templates to ${full_path}"
	@aws s3 cp ${local_templates_directory} ${full_path} --recursive

deploy_templates: deploy_cloudengineer_template deploy_dataanalyst_template deploy_dataengineer_template deploy_datascientist_template deploy_datasteward_template deploy_sysaccounts_template
	@echo "Deploying all templates.."

deploy_cloudengineer_template:
	aws cloudformation create-stack --stack-name cloudengineer-iam-stack --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/cloudengineer-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: create-stack

deploy_dataanalyst_template:
	aws cloudformation create-stack --stack-name 'dataanalyst-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/dataanalyst-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: create-stack

deploy_dataengineer_template:
	aws cloudformation create-stack --stack-name 'dataengineer-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/dataengineer-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: create-stack

deploy_datascientist_template:
	aws cloudformation create-stack --stack-name 'datascientist-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/datascientist-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: create-stack

deploy_datasteward_template:
	aws cloudformation create-stack --stack-name 'datasteward-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/datasteward-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: create-stack

deploy_sysaccounts_template:
	aws cloudformation create-stack --stack-name 'sysaccounts-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/sysaccounts-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: create-stack

update_stacks: update_cloudengineer_iam_stack update_dataanalyst_iam_stack update_dataengineer_iam_stack update_datascientist_iam_stack update_datasteward_iam_stack update_sysaccounts_iam_stack
	@echo "Updating all stacks.."

update_cloudengineer_iam_stack:
	aws cloudformation update-stack --stack-name 'cloudengineer-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/cloudengineer-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: update-stack

update_dataanalyst_iam_stack:
	aws cloudformation update-stack --stack-name 'dataanalyst-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/dataanalyst-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: update-stack

update_dataengineer_iam_stack:
	aws cloudformation update-stack --stack-name 'dataengineer-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/dataengineer-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: update-stack

update_datascientist_iam_stack:
	aws cloudformation update-stack --stack-name 'datascientist-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/datascientist-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: update-stack

update_datasteward_iam_stack:
	aws cloudformation update-stack --stack-name 'datasteward-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/datasteward-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: update-stack

update_sysaccounts_iam_stack:
	aws cloudformation update-stack --stack-name 'sysaccounts-iam-stack' --template-url https://dataplatform-iam-templates.s3-ap-southeast-2.amazonaws.com/source-system-templates/sysaccounts-iam-template.yaml --capabilities CAPABILITY_NAMED_IAM
.PHONY: update-stack

delete_stacks:
	aws cloudformation delete-stack --stack-name 'cloudengineer-iam-stack'
	aws cloudformation delete-stack --stack-name 'dataanalyst-iam-stack'
	aws cloudformation delete-stack --stack-name 'dataengineer-iam-stack'
	aws cloudformation delete-stack --stack-name 'datascientist-iam-stack'
	aws cloudformation delete-stack --stack-name 'datasteward-iam-stack'
	aws cloudformation delete-stack --stack-name 'sysaccounts-iam-stack'
.PHONY: delete-stack