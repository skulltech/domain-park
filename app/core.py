import requests
import xmltodict
import json
from datetime import date, timedelta

class APIException(Exception):
	pass


class AlpNames:
	def __init__(self):
		with open('credentials.json') as f:
			credentials = json.load(f)
		self.reseller_id = credentials['alpnames']['reseller_id']
		self.api_key = credentials['alpnames']['api_key']
		self.customer_id = credentials['alpnames']['customer_id']

	def register_domain(self, domain_name, nameservers, privacy, contact_id):
		if privacy:
			privacy_param = 'true'
		else:
			privacy_param = 'false'

		payload = {
		'auth-userid': self.reseller_id,
		'api-key': self.api_key,
		'domain-name': domain_name,
		'years': 1,
		'customer-id': self.customer_id,
		'reg-contact-id': contact_id,
		'admin-contact-id': contact_id,
		'tech-contact-id': contact_id,
		'billing-contact-id': contact_id,
		'ns': nameservers,
		'invoice-option': 'PayInvoice',
		'purchase-privacy': privacy_param,
		'auto-renew': 'false'
		}

		response = requests.post('https://httpapi.com/api/domains/register.json', params=payload)
		response_dict = response.json()

		if response_dict['status'] == 'Success':
			return (True, 'Success')
		elif response_dict['status'] == 'error':
			return (False, response_dict['error'])

	def get_contacts(self):
		payload = {
		'auth-userid': self.reseller_id,
		'api-key': self.api_key,
		'customer-id': self.customer_id,
		'no-of-records': 10,
		'page-no': 1
		}

		response = requests.get('https://httpapi.com/api/contacts/search.json', params=payload)
		response_dict = response.json()

		return [(contact['contact.contactid'], contact['contact.name']) for contact in response_dict['result']]

	def get_order_id(self, domain_name):
		payload = {
		'auth-userid': self.reseller_id,
		'api-key': self.api_key,
		'domain-name': domain_name
		}

		response = requests.get('https://httpapi.com/api/domains/orderid.json', params=payload)
		response_dict = response.json()

		if type(response_dict) is int:
			return (True, response_dict)
		else:
			return (False, response_dict['message'])

	def add_dns_record(self, domain_name, host, address):
		payload = {
		'auth-userid': self.reseller_id,
		'api-key': self.api_key,
		'domain-name': domain_name,
		'value': address,
		'host': host
		}

		response = requests.post('https://httpapi.com/api/dns/manage/add-ipv4-record.json', params=payload)
		response_dict = response.json()

		if response_dict['status'] == 'Success':
			return (True, 'Success')
		elif response_dict['status'] == 'ERROR':
			return (False, response_dict['message'])

	def edit_nameservers(self, order_id, nameservers):
		payload = {
		'auth-userid': self.reseller_id,
		'api-key': self.api_key,
		'order-id': order_id,
		'ns': nameservers
		}

		response = requests.post('https://httpapi.com/api/domains/modify-ns.json', params=payload)
		response_dict = response.json()

		if response_dict['status'] == 'Success':
			return (True, 'Success')
		elif response_dict['status'] == 'ERROR':
			return (False, response_dict['message'])

	def activate_dns(self, order_id):
		payload = {
		'auth-userid': self.reseller_id,
		'api-key': self.api_key,
		'order-id': order_id
		}

		response = requests.post('https://httpapi.com/api/domains/modify-ns.json', params=payload)
		response_dict = response.json()

		if response_dict['status'] == 'Success':
			return (True, 'Success')
		elif response_dict['status'] == 'ERROR':
			return (False, response_dict['message'])


class RookMedia:
	def __init__(self):
		self.guid = 'B210F61C-E9F4-4FFB-919E-BE1D2FCD91F6'

	def list_domains(self):
		payload = {
		'guid': self.guid,
		'action': 'listdomains'
		}

		response = requests.get('http://api.rookdns.com/manageDomain.php', params=payload).json()

		if response['response']['status'] == 'FAILURE':
			raise APIException(response['response']['Message'])
		elif response['response']['status'] == 'SUCCESS':
			return [item['domain'] for item in response['response']['domainList']]

	def get_folders(self):
		today = date.today()
		delta = timedelta(days=1)
		yesterday = today - delta
		
		payload = {
		'GUID': self.guid,
		'STATS_DATE': yesterday.isoformat(),
		'FOLIO_SUMMARY': 1
		}

		response = requests.post('http://api.rookdns.com/apistats.php', params=payload)
		response = xmltodict.parse(response.text)

		if response['APIResult']['ErrorCode'] != '0':
			raise APIException(response['APIResult']['ErrorMessage'])
		else:
			return [{'name': folder['@name'], 'id': folder['@id']} for folder in response['APIResult']['ResponseData']['FolioList']['Folio']]

	def get_folio_id(self, folder_name):
		folders = self.get_folders()

		for folder in folders:
			if folder['name'] == folder_name:
				return folder['id']

		raise APIException('RookMedia: Folder not found')

	def add_domain(self, domain_name, folder_id):
		payload = {
		'action': 'adddomains',
		'foliokey': folder_id,
		'guid': self.guid,
		'domainlist': domain_name
		}

		response = requests.post('http://api.rookdns.com/manageDomain.php', data=payload)
		return response


class ParkingCrew:
	def __init__(self, account_no):
		with open('credentials.json') as f:
			credentials = json.load(f)
		self.user_name = credentials['parkingcrew'][account_no]['username']
		self.api_key = credentials['parkingcrew'][account_no]['api_key']

	def add_folder(self, folder_name):
		payload = {
		'user_name': self.user_name,
		'api_key': self.api_key,
		'action': 'addfolder',
		'foldername': folder_name}

		response = requests.get('https://api.parkingcrew.com/manage_v3.php', params=payload)
		response_dict = xmltodict.parse(response.text)

		if response_dict['response']['result']['success'] == '1':
			return (True, response_dict['response']['id'])
		elif response_dict['response']['result']['success'] == '0':
			return (False, response_dict['response']['result']['error']['msg'])

	def add_domain(self, domain_name, folder_id):
		payload = {
		'user_name': self.user_name,
		'api_key': self.api_key,
		'action': 'add',
		'domain': domain_name,
		'folder': folder_id}

		response = requests.get('https://api.parkingcrew.com/manage_v3.php', params=payload)
		response_dict = xmltodict.parse(response.text)

		if response_dict['response']['result']['success'] == '1':
			return (True, 'Success')
		elif response_dict['response']['result']['success'] == '0':
			return (False, response_dict['response']['result']['error']['msg'])

	def add_keywords(self, domain_name, keywords):
		payload = {
		'user_name': self.user_name,
		'api_key': self.api_key,
		'action': 'managedomains',
		'type': 'keyword',
		'setting': keywords[0],
		'domain': domain_name
		}

		response = requests.get('https://api.parkingcrew.com/manage_v3.php', params=payload)
		response_dict = xmltodict.parse(response.text)

		if response_dict['response']['result']['success'] == '0':
			return (False, response_dict['response']['result']['error']['msg'])

		payload = {
		'user_name': self.user_name,
		'api_key': self.api_key,
		'action': 'managedomains',
		'type': 'related',
		'setting': '|'.join(keywords),
		'domain': domain_name
		}

		response = requests.get('https://api.parkingcrew.com/manage_v3.php', params=payload)
		response_dict = xmltodict.parse(response.text)

		if response_dict['response']['result']['success'] == '1':
			return (True, 'Success')
		elif response_dict['response']['result']['success'] == '0':
			return (False, response_dict['response']['result']['error']['msg'])

	def get_folder_list(self):
		payload = {
		'user_name': self.user_name,
		'api_key': self.api_key,
		'action': 'folderlist'
		}

		response = requests.get('https://api.parkingcrew.com/manage_v3.php', params=payload)
		response_dict = xmltodict.parse(response.text)

		if response_dict['response']['result']['success'] == '0':
			return (False, response_dict['response']['result']['error']['msg'])

		folder_list = response_dict['response']['folderlist']['folder']
		return folder_list

	def get_folder_id(self, folder_name):
		folder_list = self.get_folder_list()
		
		for folder in folder_list:
			if folder['name'] == folder_name:
				return int(folder['id'])