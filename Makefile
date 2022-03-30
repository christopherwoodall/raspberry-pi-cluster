#########################################
## Preamble
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Modify the block character to be `-\t` instead of `\t`
ifeq ($(origin .RECIPEPREFIX), undefined)
  $(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
endif
.RECIPEPREFIX = -

#########################################
## Setup
.DEFAULT_GOAL := help

ANSIBLE_DIR := $(shell pwd)/ansible
ROLES_DIR := $(ANSIBLE_DIR)/roles


#########################################
## Recipes
default: help
all: help


.PHONY: help
help: ## List commands
-	@echo -e "USAGE: make \033[36m[COMMAND]\033[0m\n"
-	@echo "Available commands:"
-	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\t\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


.PHONY: controller
controller:	## Run the Ansible Playbook to deploy a Controller
-	@echo "Running Controller Playbook..."
-	@cd $(ANSIBLE_DIR)
-	@ansible-playbook playbooks/controller.yml


.PHONY: step
step:	## Run Ansible Playbooks with --step
-	@echo "Stepping through playbook..."
-	@cd $(ANSIBLE_DIR)
-	@ansible-playbook --step playbooks/controller.yml


# .PHONY: controller
# controller:	## Run the Ansible Playbooks to deploy the controller


.PHONY: lint
check: ## Run YAML Lint, Ansible Lint, and remove DOS line endings.
-	@echo "Starting the Linting Process"
-	@echo "Fixing line endings..."
-	@find . -type f -exec sed -i "s|\r$\||" {} \;
-	@echo "Running Linter..."
-	find $(ANSIBLE_DIR) -type f -name "*.yml" -exec ansible-lint --force-color -p {} \;
-	find $(ANSIBLE_DIR) -type f -name "*.yml" -exec yamllint -f colored {} \;

.PHONY: clean
clean: ## Clean up
-	@echo "Cleaning..."
-	@find ./ -name '*.pyc' -exec rm -f {} \;
-	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
-	@find ./ -name '*~' -exec rm -f {} \;
