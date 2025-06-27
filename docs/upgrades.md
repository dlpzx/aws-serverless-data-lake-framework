# Upgrades

[GitHub release notes](https://github.com/aws-solutions-library-samples/data-lakes-on-aws/releases) are the primary source of information regarding new version changes.

# Upgrade from SDLF 1.x to SDLF 2.x

In the SDLF [2.0.0 release notes](https://github.com/aws-solutions-library-samples/data-lakes-on-aws/releases/tag/2.0.0) you can find the list of new features in SDLF v2.
Please review the release notes before moving forward, in this section we will assume you understand the main feature changes. 
We will focus on how those changes influence the user experience and how users can upgrade from v1 to v2.

## User experience Comparison

### Foundational Infrastructure deployment
CICD setup, foundations and teams deployment.

#### SDLF v1
Summary of SDLF v1 deployment steps as appear in the [workshop SDLF 1.0 section](https://catalog.us-east-1.prod.workshops.aws/workshops/501cb14c-91b3-455c-a2a9-d0a21ce68114/en-US/50-sdlf1/20-production/200-foundational-cicd)

1. **Clone the SDLF repository from GitHub**
2. **Deploy foundational CICD infrastructure** with `./deploy.sh` script using `-f` flag
   - Uploads local repositories to CodeCommit
   - Deploys `sdlf-cicd-team-repos` CloudFormation stack
3. **Deploy DevOps and Child Account CICD resources** with `./deploy.sh` script using `-o -c` flags
   - Repeat for each child environment account (dev, test, prod)
   - Deploys foundational stacks in both DevOps and child accounts
4. **Deploy foundational infrastructure**
   - Clone `sdlf-foundations` repository from CodeCommit
   - Update `parameters-{env}.json` with organization parameters
   - Commit and push to trigger deployment pipeline
5. **Deploy team infrastructure**
   - Clone `sdlf-team` repository from CodeCommit
   - Update `parameters-{env}.json` with team-specific parameters
   - Commit and push to trigger team repository creation and deployment
6. **Deploy pipeline infrastructure**
   - Clone `sdlf-{team}-pipeline` repository
   - Update `parameters-{env}.json` with pipeline-specific parameters
   - Commit and push to trigger pipeline deployment
7. **Deploy dataset configuration**
   - Clone `sdlf-{team}-dataset` repository
   - Update `parameters-{env}.json` with dataset parameters
   - Commit and push to trigger dataset configuration deployment

#### SDLF v2
Summary of SDLF v2 deployment steps as appear in the [workshop SDLF 2.0 section](https://catalog.us-east-1.prod.workshops.aws/workshops/501cb14c-91b3-455c-a2a9-d0a21ce68114/en-US/20-production/300-admin-team)

1. **Clone the SDLF repository from GitHub**
2. **Deploy cross-account CICD roles** with `./deploy.sh crossaccount-cicd-roles` subcommand
   - Run for each data domain account
   - Deploys cross-account IAM roles for DevOps pipelines
3. **Deploy DevOps account resources** with `./deploy.sh devops-account` subcommand
   - Creates `sdlf-main` repository and CICD infrastructure
4. **Deploy foundational and team infrastructure**
   - Clone `sdlf-main` repository from Git provider
   - Configure foundations:
     - Create `foundations-{domain}-{env}.yaml` files using CloudFormation modules
     - Define domain-specific infrastructure using `awslabs::sdlf::foundations::MODULE`
   - Configure teams:
     - Create `team-{domain}-{team}-{env}.yaml` files using CloudFormation modules
     - Define team-specific resources using `awslabs::sdlf::team::MODULE`
   - Create Data Domain Orchestration Files
     - Create `datadomain-{domain}-{env}.yaml` files as nested CloudFormation stacks
     - Orchestrate foundations and teams deployment with dependencies
   - Create `tags.json` file with framework tags
   - Commit and push changes to trigger automated CICD pipelines

### Pipelines, Datasets and Transformation code Development
Pipelines, Datasets deployment and transformation development.

#### SDLF v1
Step-by-step guide for pipeline and dataset development as described in the [workshop SDLF 1.0 section](https://catalog.us-east-1.prod.workshops.aws/workshops/501cb14c-91b3-455c-a2a9-d0a21ce68114/en-US/50-sdlf1/20-production/400-sdlf-team)

1. **Deploy Pipeline infrastructure**
   - Clone `sdlf-{team}-pipeline` repository from CodeCommit
   - Update pipeline parameters in `parameters-{env}.json` with:
      - Team name and pipeline name
      - Stage repository references (stageA and stageB repositories)
   - Commit and push changes to trigger `sdlf-cicd-{team}-pipeline` deployment
2. **Deploy Dataset infrastructure**
   - Clone `sdlf-{team}-dataset` repository from CodeCommit
   - Update dataset parameters in `parameters-{env}.json` with dataset name and pipeline configuration
   - Commit and push changes to trigger `sdlf-cicd-{team}-dataset` deployment
3. **Transform Lambda code development**
   - Clone `sdlf-{team}-datalakeLibrary` repository from CodeCommit
   - Update `dataset_mappings.json` to map each dataset to specific transformation code for stageA and stageB Lambdas
   - Create or update transformation code file
   - Commit and push the changes to update the Lambda layers of the transformation Lambdas
4. **Deploy Glue Job code**
   - Clone `sdlf-utils` and use `glue-jobs-deployer` to deploy Glue Jobs that are triggered in stageB


#### SDLF v2
Step-by-step guide for pipeline and dataset development as described in the [workshop SDLF 2.0 section](https://catalog.us-east-1.prod.workshops.aws/workshops/501cb14c-91b3-455c-a2a9-d0a21ce68114/en-US/20-production/400-sdlf-team)


1. **Deploy Pipeline infrastructure**
   - Clone `sdlf-main-<domain>-{team}` repository from Git provider
   - Create `pipeline-{pipeline}.yaml` definition files using YAML CloudFormation modules. Design the pipeline based on the compute needs. Add triggers and schedulers.
     - Lambda stages: For lightweight, fast processing
     - Glue stages: For traditional ETL workloads
     - EMR Serverless: For big data processing
     - ECS Fargate: For containerized custom processing
     - Data Quality: For automated data validation
     - Develop your own stage as explained in the [Going Further section](https://catalog.us-east-1.prod.workshops.aws/workshops/501cb14c-91b3-455c-a2a9-d0a21ce68114/en-US/20-production/500-going-further) of the workshop.
   - Create/Update `pipelines.yaml` orchestration file that deploys `pipeline-{pipeline}.yaml` as nested CloudFormation stacks 
   - Add framework tags in `tags.json` file
   - Commit and push changes to trigger automated deployment
2. **Deploy Dataset infrastructure**
   - Clone `sdlf-main-<domain>-{team}` repository from Git provider (same repo used for pipelines)
   - Create/Update `datasets.yaml` orchestration file that deploys `awslabs::sdlf::dataset::MODULE` constructs
   - Commit and push changes to trigger automated deployment
3. **Develop Transformation code**
   - Develop stage-specific code in appropriate stage repositories 
   - Update shared libraries in `sdlf-datalakeLibrary` - out of the box it does not contain custom transformations. The reason is that stage-specific code is moved to the stage definition. 
   

## Architectural Comparison
SDLF 2.0 is very much in the same spirit as SDLF 1.0 - the constructs are the same, but they are managed in different
repositories and through different mechanisms that enable a larger variety of data architecture patterns.

### Repository Structure

**SDLF v1 Repositories:**
```
sdlf-foundations     # Core infrastructure
sdlf-team           # Team management
sdlf-pipeline       # Pipeline definitions
sdlf-dataset        # Dataset configurations
sdlf-datalakeLibrary # Shared libraries
sdlf-pipLibrary     # Pipeline utilities
sdlf-stageA         # Ingestion stage
sdlf-stageB         # Transformation stage
sdlf-utils          # Utilities and examples
```

**SDLF v2 Repositories:**
```
sdlf-foundations        # Core infrastructure (enhanced)
sdlf-team              # Team management (simplified)
sdlf-pipeline          # Pipeline orchestration (modular)
sdlf-dataset           # Dataset configurations (enhanced)
sdlf-datalakeLibrary   # Shared libraries !!(without custom transform code)
sdlf-stageA            # Ingestion stage (enhanced)
sdlf-stageB            # Transformation stage (enhanced)
sdlf-stage-lambda      # Lambda-based processing (NEW)
sdlf-stage-glue        # Glue-based processing (NEW)
sdlf-stage-emrserverless # EMR Serverless processing (NEW)
sdlf-stage-ecsfargate  # ECS Fargate processing (NEW)
sdlf-stage-dataquality # Data quality validation (NEW)
sdlf-monitoring        # Comprehensive monitoring (NEW)
sdlf-utils             # Enhanced utilities
```

### Key Dataset and Pipelines Development Differences

| Aspect                       | SDLF v1                                                      | SDLF v2                                                                        |
|------------------------------|--------------------------------------------------------------|--------------------------------------------------------------------------------|
| **Repository Structure**     | Separate repositories per team component (pipeline, dataset) | Single team repository for all components                                      |
| **Pipeline Definition**      | JSON parameters with fixed stageA/stageB architecture        | YAML CloudFormation modules with flexible multi-stage architecture             |
| **Stage Types**              | Limited to stageA and stageB                                 | Multiple stage types (Lambda, Glue, EMR Serverless, ECS Fargate, Data Quality) |
| **Configuration Management** | Multiple JSON parameter files across repositories            | Centralized YAML configuration files                                           |
| **Deployment Coordination**  | Manual coordination between pipeline and dataset deployments | Orchestrated deployment through nested stacks                                  |
| **Environment Promotion**    | Update multiple parameter files separately                   | Single repository with file-based environment management                       |
| **Pipeline Flexibility**     | Fixed two-stage pipeline architecture                        | Any number of stages with custom processing engines                            |
| **Event Handling**           | Basic EventBridge integration                                | Advanced event patterns with flexible trigger types                            |


**SDLF v1 Processing Model:**
```
Data Source → stageA (event-driven) → stageB (batch) → Analytics Layer
                ↓                      ↓
            AWS Lambda             AWS Glue/Lambda
```

**SDLF v2 Processing Model:**
```
Data Source → Multiple Stage Options → Analytics Layer
                        ↓
                       ┌─ sdlf-stage-lambda
                       ├─ sdlf-stage-glue  
                       ├─ sdlf-stage-emrserverless
                       ├─ sdlf-stage-ecsfargate
                       └─ sdlf-stage-dataquality
```

## Migration from v1 to v2

### Pre-Migration Assessment

Before migrating from SDLF v1 to v2, assess your current implementation:

1. **Inventory Current Resources**
   - Document all deployed teams, pipelines, and datasets
   - List custom modifications made to SDLF v1 components
   - Identify dependencies on specific v1 features

2. **Review New v2 Features**
   - Evaluate new stage types (Lambda, EMR Serverless, ECS Fargate, Data Quality)
   - Consider monitoring enhancements
   - Assess VPC support requirements

3. **Plan Migration Strategy**
   - Review recommended migration path
   - Plan for data migration and pipeline testing

### Recommended migration approach

Deploy SDLF v2 alongside existing v1 infrastructure (blue/green deployment). To deploy V2 follow the steps in the [workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/501cb14c-91b3-455c-a2a9-d0a21ce68114/en-US/20-production).

1. Deploy v2 DevOps Infrastructure. IMPORTANT: if you are deploying SDLF v2 in the same accounts as SDLF v1, and you are using the same git provider, the repositories names will run into conflicts. In that scenario, you will need to use the `-g` parameter in the commands using `./deploy.sh`. Make sure you use any string different from `sdlf`. In the example below, the repositories for v2 will be called sdlfv2-X. 
   - `./deploy.sh crossaccount-cicd-roles -d <devops-account-aws-account-id> -p <child-account-aws-profile> -r <aws-region> -f sdlfv2`
   - `./deploy.sh devops-account -d <child-account-1-aws-account-id>,<child-account-2-aws-account-id> -p <devops-account-aws-profile> -r <aws-region> -g sdlfv2`
2. Deploy v2 foundations and team resources using the `<sdlfv2>-main` repository. sdlfv2 represents the value you provided in the `-g` parameter in the previous step.
   - Decide domains in the data mesh - Domains are a NEW concept of SDLF v2 - Choose any domain name except `datalake`
   - Deploy foundations and teams. If you want to avoid conflicting-names issues chose a different team name as in v1. This will ensure pipelines and datasets can be created with the same name without conflicts.


Code migration for each pipeline and dataset:
3. Deploy v2 pipeline (code migration)
   - Assess if SDLF v1 stageA/stageB is the best data processing architecture for the use-case
   - Design the pipeline-{pipeline}.yaml CloudFormation template with the selected stages
   - Update the trigger of each stage with a schedule or event pattern. If you want to re-create the SDLF v1 triggers, the [workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/501cb14c-91b3-455c-a2a9-d0a21ce68114/en-US/20-production/400-sdlf-team) includes an example that mimics it.
     - For the stage A event-driven trigger, you will need to know in advance the prefix where data will be stored in S3
     - For the stage B schedule + event-driven trigger, you can construct the event with the arn of the stage A State Machine
4. Deploy v2 dataset and pipeline
   - Follow the workshop and deploy a pipeline and dataset with the architecture that matches the dataset better
   - In SDLF v2 datasets and pipelines are not tightly coupled. Datasets can be deployed without being linked to a pipeline.
   - You need to define different event triggers in the pipeline to "link" the pipeline execution to the dataset data. For example, in the workshop the example shows an event that reacts to S3 putObject events on a particular S3 location that corresponds to a dataset S3 prefix. This event is an example, you can also opt to react to s3:PutObject events in the whole S3 Bucket, or to any other event coming from other sources (e.g. Glue events, custom EventBridge Bus events)

5. Test the pipeline and dataset
   - Trigger the pipeline with sample data, ensure it succeeds and that the data is transformed as expected
   - Connect the dataset with downstream applications and ensure it is accessed as previously

Data migration:
6. v1-processed data migration: Once all datasets and pipelines are re-created in v2, new data can flow and be processed by the v2 pipelines into the v2 datasets.
But what happens with the data that was processed using v1? There is not a single solution on how to handle the data migration for v1-processed data. It will depend on your requirements.
   - scenario 1: it is not required. v2 will only contain new datasets, v1-datasets will continue to be accessible.
   - scenario 2: it is required. v1-datasets will keep receiving new data, and we want to process it with v2 pipelines into new v2 datasets
     - option 2.1 Sync curated data: sync data from the analytics bucket in v1 to the analytics bucket in v2 - 
     - option 2.2 Sync raw data and re-process with v2: sync data from the raw bucket in v1 to the raw bucket in v2
     - option 2.3 Keep 2 datasets:

Blue/Green swap:
7. Update upstream data ingestion
   - Redirect new data ingestion to v2 raw S3 Bucket
   - Maintain v1 for rollbacks and for availability of downstream applications
8. Update downstream data consumption
   - Connect downstream applications to the new databases
   - Test that v2 datasets are accessible from your data applications
9. Remove v1 upstream data ingestion. 
   - From now onwards data will be process solely with v2
10. Plan and decommission v1
   - If Code is fully migrated to v2
   - And Data is fully migrated to v2
   - And downstream applications only read from v2 datasets
   - Then we can plan the decommission of sdlf v1 - since everything is infrastructure as code you will need to delete the old CloudFormation stacks from the newest to the oldest to avoid orphan resources.

### Rollback Plan

Prepare rollback procedures in case of migration issues:

1. **Configuration Rollback**
   - Keep v1 configurations backed up
   - Document rollback procedures
   - Test rollback in non-production environment

2. **Data Rollback**
   - Maintain v1 data infrastructure (S3 Buckets, KMS keys) during migration period
   - Plan for data synchronization if needed
   - Document data recovery procedures
