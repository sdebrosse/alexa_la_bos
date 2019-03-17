# Alexa Skill - LA Board of Supervisors

This skill allows citizens to hear about the motions before the LA Board of Supervisors (upcoming and past). The user can also request that Alexa send an SMS message (containing a link to any motion's PDF) to a phone number.

Follow these steps to deploy the demo:
1. Build a Python 3.6 deployment package for the Lambda functon (index.py). Then create a Lambda function inside your AWS accountand upload the deployment package.
2. For this Lambda function, create an IAM role with the following managed policies attached:
	* AWSLambdaRole
	* AWSLambdaExecute
	* AmazonSNSFullAccess (used to send SMS messages to the user)
3. Create an Alexa skill. Drop skills.json into the "JSON Editor" inside the Alexa Development console for your skill.
4. Configure your skill to use your Lambda function from #1 under "Endpoint"