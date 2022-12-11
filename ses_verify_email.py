import boto3

def verify_email_identity():
    ses_client = boto3.client("ses", region_name="eu-central-1")
    response = ses_client.verify_email_identity(
        EmailAddress=" "
    )
    print(response)
