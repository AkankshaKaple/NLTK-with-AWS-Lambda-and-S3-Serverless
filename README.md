# NLTK-with-AWS-Lambda-and-S3-Serverless
The project contains implementation of Twitter Sentiment Analysis using AWS Lambda.

Steps:

1. Install npm serverless on the system : https://nodejs.org/en/download/package-manager/
2. Create an IAM ( Identity and Access Management )  user, name it as ‘serverless-admin’ ( recommended ) 
    - Assign programmatic access 
    - Assign Administrator access in Attach Existing Policies 
    - Download creds
3. Set up Serverless on Laptop:
4. serverless config credentials --provider aws --key XXX --secret YYY --profile serverless-admin
5. Create : sls create --template aws-python3 --path PATH
6. Install serverless-python-requirements plugin : sls plugin install -n serverless-python-requirements
7. Deploy: sls deploy -v
8. Invoke: sls invoke --function-name FUNCTION
