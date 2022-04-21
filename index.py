import json
import boto3
from botocore.exceptions import ClientError

def my_handler(event, context):
    msg = event['Records'][0]['Sns']['Message']

    msg_json = json.loads(msg)
    email = msg_json['email']
    token = msg_json['token']
    msg_type = msg_json['message_type']
    print("email: ", email)
    print("token: ", token)
    print("message_type: ", msg_type)

    SENDER = 'olayinka.o@northeastern.edu'
    SUBJECT = "Verify your email address!!!"
    DOMAIN_NAME = "dev.olayinka-olasunkanmi.me"
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
