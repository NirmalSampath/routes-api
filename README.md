# Itinerary API (AWS CDK + Lambda + API Gateway)

This project deploys an AWS Lambda function behind an API Gateway using the AWS Cloud Development Kit (CDK).
The Lambda function integrates with the Digitransit API
 to provide route planning functionality.

---

## Prerequisites

- **AWS Account** & programmatic access credentials (Access Key + Secret Key)  
- **AWS CLI** installed → [Install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
  ```bash
  npm install -g aws-cdk
  ```
- **Python 3.12** installed with **pip**

---

## Setup

### 1. Export AWS credentials  
Set your AWS credentials and region so that CDK can authenticate with AWS.

#### macOS / Linux
```bash
export AWS_ACCESS_KEY_ID=<your_access_key_id>
export AWS_SECRET_ACCESS_KEY=<your_secret_access_key>
export AWS_REGION=<your_region>
```

#### Windows (PowerShell)
```powershell
$env:AWS_ACCESS_KEY_ID="<your_access_key_id>"
$env:AWS_SECRET_ACCESS_KEY="<your_secret_access_key>"
$env:AWS_REGION="<your_region>"
```

---

### 2. Update Digitransit API Key  
Create `.env` in the root and, add the environment variable with your Digitransit API key:

```python
"DIGITRANSIT_API_KEY": "<your_digitransit_api_key>"
```

---

### 3. Bootstrap your AWS environment  
CDK requires bootstrapping before the first deploy:

```bash
cdk bootstrap aws://<aws_account_id>/<aws_region>
```

---

### 4. Synthesize the CloudFormation template  
This command generates the CloudFormation template from your CDK code:

```bash
cdk synth
```

---

### 6. Deploy the stack  
Finally, deploy your resources to AWS:

```bash
cdk deploy
```

Confirm with **`y`** when prompted.

---

## Verification

Once deployment completes, CDK will output the **API Gateway endpoint URL**.  
Example:

```
Outputs:
ItineraryStack.ItineraryApiEndpoint = https://<api_id>.execute-api.<region>.amazonaws.com/prod/
```
**Fetch the API Key using the following aws cli command or from the aws console**

```
aws apigateway get-api-keys --include-values --region <your_aws_region>
```


Test it with:

```bash
curl "https://<api_id>.execute-api.<region>.amazonaws.com/prod/routes?start=Aalto-Yliopisto&stop=Keilaniemi&time=20250912084500"
```

---

## Cleanup

To delete all provisioned resources:

```bash
cdk destroy
```
