import logging
import os
import boto3
import pandas as pd
from botocore.exceptions import ClientError

profile_list = ["default"]

ec2 = boto3.client('ec2')
region_dictionary = ec2.describe_regions()

# print(region_dictionary) for log purposes.

region_list = [
    region['RegionName']for region in ec2.describe_regions()['Regions']
]

print(region_list)
disassociatable_ips=[]

for profile in profile_list:

    for region in region_list:

        try:

            session = boto3.Session(profile_name=f'{profile}', region_name=f'{region}')

            client = session.client('ec2')
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

df = pd.DataFrame(disassociatable_ips, columns=[
                  'PROFILE', 'REGION', 'ELASTIC IP'])

os.makedirs('EIPS/', exist_ok=True)

df.to_csv(
    'EIPS/elastic_ip_list.csv',
    index=False,
    encoding='utf-8',
    header=True
)

print("Done!...")