import unittest
#from decimal import Decimal
from contracting.stdlib.bridge.decimal import ContractingDecimal
from contracting.stdlib.bridge.time import Datetime
from contracting.client import ContractingClient


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.c = ContractingClient()
        self.c.flush()

        with open("../currency.s.py") as f:
            contract = f.read()
            self.c.submit(contract, 'currency', constructor_args={
                          "vk": "con_multi_sign"})

        with open("../non_lst001.py") as f:
            contract = f.read()
            self.c.submit(contract, 'non_lst001', owner='con_multi_sign')

        with open("../con_action_token/action_core.py") as f:
            contract = f.read()
            self.c.submit(contract, 'action_core')

        with open("../con_action_token/action_token.py") as f:
            contract = f.read()
            self.c.submit(contract, 'action_token', owner='action_core')

        with open("./con_multi_sign.py") as f:
            code = f.read()
            self.c.submit(code, name="con_multi_sign")

        self.currency = self.c.get_contract("currency")
        self.action_core = self.c.get_contract('action_core')
        #self.action_token = self.c.get_contract('action_token')
        self.non_lst001 = self.c.get_contract("non_lst001")
        self.multi_sign = self.c.get_contract("con_multi_sign")

        # action contract registered
        self.action_core.register_action(
            action='token', contract='action_token')

        # self.setupApprovals()

    def setupApprovals(self):
        self.currency.approve(amount=999999999, to="con_multi_sign")

    def tearDown(self):
        self.c.flush()

    def test_submit_proposal_user_submiting_proposal_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                signer='user123',
                propsl = {
                    'add_owner': 'traderrob'})

# state_updates proposal tests

## add_owner

    def test_submit_proposal_owner_proposing_to_add_new_owner_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'add_owner': 'traderrob'})

        proposal = {
            'type': 'state_update',
            'add_owner': 'traderrob',
            'executed': False}

        message = 'there was no concensus to add traderrob'
        
        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_owner_confirming_to_add_new_owner_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'add_owner': 'traderrob'})
        result = self.multi_sign.confirm_proposal(signer='jeff', proposal_id=1)

        proposal = {
            'type': 'state_update',
            'add_owner': 'traderrob',
            'executed': True}

        updated_owners = ['sys', 'benjos', 'jeff', 'chris', 'traderrob']

        self.assertEqual(proposal, result)
        self.assertEqual(updated_owners, self.multi_sign.owners.get())
        #number_of_confirmations = self.multi_sign.owner_confirmed[1]

    def test_submit_proposal_owner_proposing_to_add_existing_owner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'add_owner': 'benjos'})

    def test_submit_proposal_if_add_owner_value_is_not_string_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'add_owner': 419})
            
## remove_owner

    def test_submit_proposal_owner_proposing_to_remove_existing_owner_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'remove_owner': 'chris'})

        proposal = {
            'type': 'state_update',
            'remove_owner': 'chris',
            'executed': False}

        message = 'there was no concensus to remove chris'
        
        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_owner_confirming_to_remove_existing_owner_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'remove_owner': 'chris'})
        result = self.multi_sign.confirm_proposal(signer='jeff', proposal_id=1)

        proposal = {
            'type': 'state_update',
            'remove_owner': 'chris',
            'executed': True}

        updated_owners = ['sys', 'benjos', 'jeff']

        self.assertEqual(proposal, result)
        self.assertEqual(updated_owners, self.multi_sign.owners.get())
        #number_of_confirmations = self.multi_sign.owner_confirmed[1]

    def test_submit_proposal_owner_proposing_to_remove_nonexisting_owner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'remove_owner': 'mike'})

    def test_submit_proposal_if_remove_owner_value_is_not_string_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'remove_owner': 419})

## replace_owner

    def test_submit_proposal_owner_proposing_to_replace_existing_owner_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'replace_owner': {
                    'new_owner': 'cray',
                    'existing_owner': 'benjos'}})

        proposal = {
            'type': 'state_update',
            'replace_owner': {
                    'new_owner': 'cray',
                    'existing_owner': 'benjos'},
            'executed': False}

        message = 'there was no concensus to replace benjos with cray'
        
        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_owner_confirming_to_replace_existing_owner_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'replace_owner': {
                    'new_owner': 'cray',
                    'existing_owner': 'benjos'}})
        result = self.multi_sign.confirm_proposal(signer='jeff', proposal_id=1)

        proposal = {
            'type': 'state_update',
            'replace_owner': {
                    'new_owner': 'cray',
                    'existing_owner': 'benjos'},
            'executed': True}

        updated_owners = ['sys', 'jeff', 'chris', 'cray']

        self.assertEqual(proposal, result)
        self.assertEqual(updated_owners, self.multi_sign.owners.get())
        #number_of_confirmations = self.multi_sign.owner_confirmed[1]

    def test_submit_proposal_owner_proposing_to_replace_nonexisting_owner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'replace_owner': {
                    'new_owner': 'cray',
                    'existing_owner': 'test_test'}})

    def test_submit_proposal_if_replace_owner_value_is_not_string_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'replace_owner': {
                    'new_owner': 419,
                    'existing_owner': 'benjos'}})

        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'replace_owner': {
                    'new_owner': 'cray',
                    'existing_owner': 419}})

## register_action

    def test_submit_proposal_owner_proposing_to_register_action_contract_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'register_action': {
                    'action': 'gToken',
                    'contract': 'action_token'}})

        proposal = {
            'type': 'state_update',
            'register_action': {
                    'action': 'gToken',
                    'contract': 'action_token'},
            'executed': False}


        message = 'there was no concensus to register gToken'
        
        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])    
        
    def test_submit_proposal_owner_proposing_to_register_an_already_registered_action_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'register_action': {
                        'action': 'sToken',
                        'contract': 'action_token'}})
            self.multi_sign.confirm_proposal(signer='benjos', proposal_id=1)

    def test_submit_proposal_owner_proposing_to_register_action_contract_not_owned_by_multisg_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'register_action': {
                        'action': 'tToken',
                        'contract': 'action_token'}})
            self.multi_sign.confirm_proposal(signer='benjos', proposal_id=1)

    def test_submit_proposal_owner_proposing_to_register_a_non_compliant_action_contract_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'register_action': {
                        'action': 'n_contract',
                        'contract': 'non_lst001'}})
            self.multi_sign.confirm_proposal(signer='benjos', proposal_id=1)

    def test_submit_proposal_if_register_action_value_is_not_string_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'register_action': {
                        'action': 'sToken',
                        'contract': 419}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'register_action': {
                        'action': 419,
                        'contract': 'action_token'}})

## unregister_action

    def test_submit_proposal_owner_proposing_to_unregister_action_contract_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'unregister_action': 'sToken'})

        proposal = {
            'type': 'state_update',
            'unregister_action': 'sToken',
            'executed': False}
        
        message = 'there was no concensus to unregister sToken'
        
        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_owner_proposing_to_unregister_a_nonexisting_action_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'unregister_action': 'lToken'})
            self.multi_sign.confirm_proposal(signer='chris', proposal_id=1)

    def test_submit_proposal_if_unregister_action_value_is_not_string_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'unregister_action': 419})

    def test_submit_proposal_owner_proposing_to_change_required_confirmations_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'change_requirement': 3})

        proposal = {
            'type': 'state_update',
            'change_requirement': 3,
            'executed': False}
        
        message = 'there was no concensus to change required confirmations to 3'
        
        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_owner_proposing_to_change_required_confirmations_beyond_acceptable_range_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'change_requirement': 9})
            self.multi_sign.confirm_proposal(signer='chris', proposal_id=1)    

        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'change_requirement': 0})
            self.multi_sign.confirm_proposal(signer='benjos', proposal_id=2)

    def test_submit_proposal_owner_if_change_requirement_value_is_not_int_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'change_requirement': '9'})
            
## change_dailylimit

    def test_submit_proposal_owner_proposing_to_change_token_dailylimit_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'change_dailylimit': {
                    'token': 'currency',
                    'amount': ContractingDecimal('3000')}})

        proposal = {
            'type': 'state_update',
            'change_dailylimit': {
                'token': 'currency',
                'amount': ContractingDecimal('3000')},
            'executed': False}

        message = f"there was no concensus to change token dailylimit to {ContractingDecimal('3000')}"
        
        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_owner_proposing_to_change_action_dailylimit_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'change_dailylimit': {
                    'action': 'gToken',
                    'amount': ContractingDecimal('3000')}})

        proposal = {
            'type': 'state_update',
            'change_dailylimit': {
                'action': 'gToken',
                'amount': ContractingDecimal('3000')},
            'executed': False}
        
        message = f"there was no concensus to change action dailylimit to {ContractingDecimal('3000')}"

        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_owner_proposing_to_change_external_action_dailylimit_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'change_dailylimit': {
                    'external_action': 'eToken',
                    'amount': ContractingDecimal('3000')}})

        proposal = {
            'type': 'state_update',
            'change_dailylimit': {
                'external_action': 'eToken',
                'amount': ContractingDecimal('3000')},
            'executed': False}

        message = f"there was no concensus to change external action dailylimit to {ContractingDecimal('3000')}"
        
        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_if_change_dailylimit_amount_value_is_not_decimal_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'change_dailylimit': {
                        'token': 'currency',
                        'amount': 3000}})
        
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'change_dailylimit': {
                        'action': 'gToken',
                        'amount': 3000}})

        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'change_dailylimit': {
                        'external_action': 'eToken',
                        'amount': 3000}})

    def test_submit_proposal_if_change_dailylimit_token_action_e_action_value_is_not_string_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'change_dailylimit': {
                        'token': 419,
                        'amount': ContractingDecimal('3000')}})
        
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'change_dailylimit': {
                        'action': 419,
                        'amount': ContractingDecimal('3000')}})

        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'change_dailylimit': {
                        'external_action': 419,
                        'amount': ContractingDecimal('3000')}})


# lst001_proposal

    def test_submit_proposal_owner_proposing_a_token_transfer_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer',
                    'amount': 456,
                    'to': 'test_test'}})

        proposal = {
                'type': 'lst001_proposal',
                'token': 'currency',
                'payload': {
                    'method': 'transfer',
                    'amount': 456,
                    'to': 'test_test'},
                'executed': False}

        message = 'there was no concensus to transfer 456'

        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_owner_proposing_a_token_approve_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'approve',
                    'amount': 456,
                    'to': 'test_test'}})

        proposal = {
                'type': 'lst001_proposal',
                'token': 'currency',
                'payload': {
                    'method': 'approve',
                    'amount': 456,
                    'to': 'test_test'},
                'executed': False}

        message = 'there was no concensus to approve 456'

        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_owner_proposing_a_token_transfer_from_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer_from',
                    'amount': 456,
                    'to': 'test_test',
                    'main_account': 'vault'}})

        proposal = {
                'type': 'lst001_proposal',
                'token': 'currency',
                'payload': {
                    'method': 'transfer_from',
                    'amount': 456,
                    'to': 'test_test',
                    'main_account': 'vault'},
                'executed': False}

        message = 'there was no concensus to spend 456 from vault'

        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_if_token_transfer_proposal_contain_inappropriate_data_type_should_fail(self):
        with self.assertRaises(AttributeError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 419,
                    'payload': {
                        'method': 'transfer',
                        'amount': 456,
                        'to': 'test_test'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 419,
                        'amount': 456,
                        'to': 'test_test'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 'transfer',
                        'amount': 456,
                        'to': 419}})

    def test_submit_proposal_if_token_approve_proposal_contain_inappropriate_data_type_should_fail(self):
        with self.assertRaises(AttributeError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 419,
                    'payload': {
                        'method': 'approve',
                        'amount': 456,
                        'to': 'test_test'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 419,
                        'amount': 456,
                        'to': 'test_test'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 'approve',
                        'amount': 456,
                        'to': 419}})

    def test_submit_proposal_if_token_transfer_from_proposal_contain_inappropriate_data_type_should_fail(self):
        with self.assertRaises(AttributeError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 419,
                    'payload': {
                        'method': 'transfer_from',
                        'amount': 456,
                        'to': 'test_test',
                        'main_account': 'vault'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 419,
                        'amount': 456,
                        'to': 'test_test',
                        'main_account': 'vault'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 'transfer_from',
                        'amount': 456,
                        'to': 419,
                        'main_account': 'vault'}})


# action_proposal

    def test_submit_proposal_owner_proposing_an_action_txn_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'action': 'sToken',
                'bulk': False,
                'payload': {
                    'function': 'vote',
                    'propsl': 'get chart'}})

        proposal = {
                'type': 'action_proposal',
                'action': 'sToken',
                'bulk': False,
                'payload': {
                    'function': 'vote',
                    'propsl': 'get chart'},
                'executed': False}

        message = 'there was no concensus to execute sToken txn'

        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_owner_proposing_a_nonexisting_action_txn_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action': 'qToken',
                    'bulk': False,
                    'payload': {
                        'function': 'vote',
                        'propsl': 'get chart'}})

    def test_submit_proposal_if_action_txn_contain_inappropriate_data_type_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action': 419,
                    'bulk': False,
                    'payload': {
                        'function': 'vote',
                        'propsl': 'get chart'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action': 'sToken',
                    'bulk': 'False',
                    'payload': {
                        'function': 'vote',
                        'propsl': 'get chart'}})

        
# external_action_proposal

    def test_submit_proposal_owner_proposing_an_external_action_txn_should_succeed(self):
        result = self.multi_sign.submit_proposal(
            propsl = {
                'action_core': 'action_core',
                'action': 'token',
                'bulk': False,
                'payload': {
                    'function': 'vote',
                    'propsl': 'get chart'}})

        proposal = {
                'type': 'external_action_proposal',
                'action_core': 'action_core',
                'action': 'token',
                'bulk': False,
                'payload': {
                    'function': 'vote',
                    'propsl': 'get chart'},
                'executed': False}

        message = 'there was no concensus to execute token txn from action_core'

        submitted_proposal = self.multi_sign.proposal[1]
        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertEqual(message, result)
        self.assertTrue(owner_confirm)
        self.assertFalse(submitted_proposal['executed'])

    def test_submit_proposal_if_e_action_txn_contain_inappropriate_data_type_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action_core': 419,
                    'action': 'token',
                    'bulk': False,
                    'payload': {
                        'function': 'vote',
                        'propsl': 'get chart'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action_core': 'action_core',
                    'action': 419,
                    'bulk': False,
                    'payload': {
                        'function': 'vote',
                        'propsl': 'get chart'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action_core': 'action_core',
                    'action': 'token',
                    'bulk': 'False',
                    'payload': {
                        'function': 'vote',
                        'propsl': 'get chart'}})


if __name__ == "__main__":
    unittest.main()
