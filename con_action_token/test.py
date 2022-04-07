import unittest
from contracting.client import ContractingClient

class MyTestCase(unittest.TestCase):
	def setUp(self):
		self.c = ContractingClient()
		self.c.flush()

		with open("action_core.py") as f:
			contract = f.read()
			self.c.submit(contract, 'action_core')
			
		with open("action_token.py") as f:
			contract = f.read()
			#action core must own this contract
			self.c.submit(contract, 'action_token', owner='action_core')
			
		self.action_core = self.c.get_contract('action_core')
		#self.test = self.c.get_contract('test_con')

		#action contract registered
		self.action_core.register_action(action='test', contract='action_token')
			
	def tearDown(self):
		self.c.flush()
	
	def test_transfer_sending_token_passes(self):
		payload = {
			'function': 'transfer',
			'amount': 50,
			'to': 'user123'
		}
		self.action_core.interact(action='test', payload=payload)
		self.assertEqual(self.action_core.S['balances', 'user123'], 50)

	def test_transfer_sending_more_than_one_has_fails(self):
		payload = {
			'function': 'transfer',
			'amount': 50,
			'to': 'user123'
		}
		self.action_core.interact(action='test', payload=payload)
		self.assertEqual(self.action_core.S['balances', 'user123'], 50)
		
	def test_approve_approving_token_passes(self):
		payload = {
			'function': 'approve',
			'amount': 100,
			'to': 'user123'
		}
		self.action_core.interact(action='test', payload=payload)
		self.assertEqual(self.action_core.S['balances', 'sys', 'user123'], 100)
	
	def test_transfer_from_without_approving_fails(self):
		payload = {
			'function': 'transfer_from',
			'amount': 150,
			'to': 'user123',
			'main_acc': 'sys'
		}
		with self.assertRaises(AssertionError):
			self.action_core.interact(action='test', payload=payload)

	def test_transfer_from_approving_before_passes(self):
		approve_payload = {
			'function': 'approve',
			'amount': 100,
			'to': 'user123'
		}
		self.action_core.interact(action='test', payload=approve_payload)

		transfer_from_payload = {
			'function': 'transfer_from',
			'amount': 100,
			'to': 'user123',
			'main_acc': 'sys'
		}
		
		self.action_core.interact(signer="user123",action='test', payload=transfer_from_payload)
		self.assertEqual(self.action_core.S['balances', 'user123'], 100)

	def test_transfer_from_spending_more_than_approved_fails(self):
		approve_payload = {
			'function': 'approve',
			'amount': 100,
			'to': 'user123'
		}
		self.action_core.interact(action='test', payload=approve_payload)

		transfer_from_payload = {
			'function': 'transfer_from',
			'amount': 101,
			'to': 'user123',
			'main_acc': 'sys'
		}
		with self.assertRaises(AssertionError):
			self.action_core.interact(signer="user123",action='test', payload=transfer_from_payload)
		
	def test_entering_a_negative_value_for_all_functions_fails(self):

		transfer_payload = {
			'function': 'transfer',
			'amount': -50,
			'to': 'user123'
		}
		approve_payload = {
			'function': 'approve',
			'amount': -60,
			'to': 'user123'
		}
		transfer_from_payload = {
			'function': 'transfer_from',
			'amount': -80,
			'to': 'user123',
			'main_acc': 'sys'
		}

		with self.assertRaises(AssertionError):
			self.action_core.interact(action='test', payload=transfer_payload)
		with self.assertRaises(AssertionError):
			self.action_core.interact(action='test', payload=approve_payload)
		with self.assertRaises(AssertionError):
			self.action_core.interact(action='test', payload=transfer_from_payload)
	
		
if __name__ == "__main__":
		unittest.main()
