from email import message
import logging
import os
from sre_constants import CHARSET
import boto3
import pandas as pd
from botocore.exceptions import ClientError

profile_list = ["default"]

ec2 = boto3.client('ec2')

region_list = [
    region['RegionName']for region in ec2.describe_regions()['Regions']
]

regionDataFrame = pd.DataFrame(region_list)

print(regionDataFrame)
disassociatable_ips=[]

for profile in profile_list:

    for region in region_list:

        try:

            # session = boto3.Session(profile_name=f'{profile}', region_name=f'{region}')

            client = boto3.client('ec2',region)
            addresses_dict = client.describe_addresses()
            
            for eip_dict in addresses_dict['Addresses']:
                if ("InstanceId" and "AssociationId" and "NetworkInterfaceId") not in eip_dict:

                    # We add the disassociated EIPs to the list with below template.
                    # [f'{profile}',f'{REGION}',eip_dict['PublicIp']]

                    disassociatable_ips.append([f'{profile}',f'{region}',eip_dict['PublicIp']])

                    # If we are going to release EIPs then use the below code
                    # client.release_address(AllocationId=eip_dict['AllocationId'])

        except ClientError as e:
            logging.basicConfig(
                level=logging.WARNING ,
                format='%(asctime)s %(message)s', 
                datefmt='%m/%d/%Y %I:%M:%S %p'
            )
            logging.warning(e)
            break

df = pd.DataFrame(disassociatable_ips,dtype=str,columns=[
                  'PROFILE', 'REGION', 'ELASTIC IP'])

os.makedirs('EIPS/', exist_ok=True)

df.to_csv(
    'EIPS/elastic_ip_list.csv',
    index=False,
    encoding='utf-8',
    header=True
)

formatted_list = format(df.to_string())
print(formatted_list)
print("Done!...")
if not formatted_list:
        ses = boto3.client('ses',region_name='eu-central-1')
        CHARSET = 'UTF-8'
        body = message
        ses.send_email(
                Destination={
                    "ToAddresses": [
                        "<RECIPIENTS>"
                    ],
                },
                Message={
                    "Body": {
                        "Text": {
                            "Charset": CHARSET,
                            "Data": "There are no unused elastic ip.",
                        }
                    },
                    "Subject": {
                        "Charset": CHARSET,
                        "Data": "Information About Elastic Ips",
                    },
                },
                Source="<SENDERS>",
            )
else:
    ses = boto3.client('ses',region_name='eu-central-1')
    CHARSET = 'UTF-8'
    ses.send_email(
            Destination={
                "ToAddresses": [
                    "<RECIPIENTS>"
                ],
            },
            Message={
                "Body": {
                    "Text": {
                        "Charset": CHARSET,
                        "Data": "List of Elastic Ips:\n" + formatted_list,
                    }
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": "Information About Elastic Ips",
                },
            },
            Source="<SENDERS>",
        )