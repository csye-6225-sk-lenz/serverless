import os
import time
import json
import boto3
from urllib import parse
from botocore.exceptions import ClientError

def my_handler(event, context):
    msg = event['Records'][0]['Sns']['Message']
    msg_json = json.loads(msg)
    email = parse.quote(msg_json['email'])
    token = msg_json['token']
    msg_type = msg_json['message_type']
    print("email: ", email)
    print("token: ", token)
    print("message_type: ", msg_type)

    SUBJECT = "Verify your email address!!!"
    DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
    SENDER = f'notification@{DOMAIN_NAME}'
    CHARSET = "UTF-8"
    BODY_HTML = f"""<html>
        <head></head>
        <body>
        <h1>Verify Your Email Address</h1>
        <p>To continue, please verify your email address by clicking the link below. This link is valid for 5 minutes.</p>
        <p><a  href="http://{DOMAIN_NAME}/v1/verifyUserEmail?email={email}&token={token}" target="_blank">Click here to verify email</a></p>
        <p>Or paste the following link in a browser: </p>
        <p>http://{DOMAIN_NAME}/v1/verifyUserEmail?email={email}&token={token} </p>
        </body>
        </html>    
    """

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('EmailVerificationSentMails')
    try:
        response = table.get_item(
            Key={'Email': email})
        if "Item" in response.keys():
            print("User already exists")
            print(response['Item'])
            return "User already exists"
    except ClientError as e:
        print(e.response['Error']['Message'])
        return e.response['Error']['Message']

    try:
        table.put_item(
            Item={
                'Email': email,
                'TTL': int(time.time()) + 1800,})
        print("Puting item in table")
    except ClientError as e:
        print(e.response['Error']['Message'])
        return e.response['Error']['Message']


    client = boto3.client('ses')

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    email,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        print("Meassage sent successfully")
        return "Meassage sent successfully, message id: " + response['MessageId']
