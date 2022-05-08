import unittest
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
            self.c.submit(contract, 'action_token', owner='con_multi_sign')

        with open("../action_submit.py") as f:
            contract = f.read()
            self.c.submit(contract, 'action_submit', owner='action_core')

        # with open("../action_submit2.py") as f:
        #     contract = f.read()
        #     self.c.submit(contract, 'action_submit2', owner='action_core')

        with open("./con_multi_sign.py") as f:
            code = f.read()
            self.c.submit(code, name="con_multi_sign")

        self.currency = self.c.get_contract("currency")
        self.action_core = self.c.get_contract('action_core')
        self.non_lst001 = self.c.get_contract("non_lst001")
        self.multi_sign = self.c.get_contract("con_multi_sign")

        # send currency to 'vc' for later approval
        self.currency.transfer(signer='con_multi_sign', amount=1000, to='vc')

        # register action contracts 
        self.setupActionRegisteration()

        self.setupApprovals() 

    def setupActionRegisteration(self):
        # multisign registers action contract by concensus
        self.multi_sign.submit_proposal(
             propsl = {
                 'register_action': {
                     'action': 'sToken',
                     'contract': 'action_token'}})
        self.multi_sign.confirm_proposal(signer='benjos', proposal_id=1)

         # external action core registers action contract
        self.action_core.register_action(
            action='action_submit', contract='action_submit')

    def setupApprovals(self):
        self.currency.approve(signer='vc', amount=1000, to='con_multi_sign')

    def tearDown(self):
        self.c.flush()

### Note:
### required number of confirmations to approve a proposal
### is set to 2 for convenient testing purposes.
### default owner/signers : 'sys', 'benjos', 'jeff', 'chris'

    def test_submit_proposal_user_submiting_proposal_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                signer='user123',
                propsl = {
                    'add_owner': 'traderrob'})

# state_updates proposal tests

## add_owner

    def test_submit_proposal_owner_proposing_to_add_new_owner_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
            propsl = {
                'add_owner': 'traderrob'})

        proposal = {
            'type': 'state_update',
            'add_owner': 'traderrob',
            'executed': False}

        owner_confirm = self.multi_sign.confirmations[2, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)

    def test_submit_proposal_owner_confirming_to_add_new_owner_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'add_owner': 'traderrob'})
        
        self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)

        executed_proposal = {
            'type': 'state_update',
            'add_owner': 'traderrob',
            'executed': True}

        updated_owners = ['sys', 'benjos', 'jeff', 'chris', 'traderrob']

        proposal_state = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal, proposal_state)
        self.assertEqual(updated_owners, self.multi_sign.owners.get())

    def test_submit_proposal_owner_proposing_to_add_existing_owner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'add_owner': 'benjos'})

    def test_submit_proposal_if_add_owner_value_is_not_string_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'add_owner': 419})  # should be string
            
## remove_owner

    def test_submit_proposal_owner_proposing_to_remove_existing_owner_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
            propsl = {
                'remove_owner': 'chris'})

        proposal = {
            'type': 'state_update',
            'remove_owner': 'chris',
            'executed': False}

        owner_confirm = self.multi_sign.confirmations[2, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)

    def test_submit_proposal_owner_confirming_to_remove_existing_owner_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'remove_owner': 'chris'})

        self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)

        executed_proposal = {
            'type': 'state_update',
            'remove_owner': 'chris',
            'executed': True}

        updated_owners = ['sys', 'benjos', 'jeff']

        proposal_state = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal, proposal_state)
        self.assertEqual(updated_owners, self.multi_sign.owners.get())
        

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
        submitted_proposal = self.multi_sign.submit_proposal(
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

        owner_confirm = self.multi_sign.confirmations[2, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)

    def test_submit_proposal_owner_confirming_to_replace_existing_owner_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'replace_owner': {
                    'new_owner': 'cray',
                    'existing_owner': 'benjos'}})
        self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)

        executed_proposal = {
            'type': 'state_update',
            'replace_owner': {
                    'new_owner': 'cray',
                    'existing_owner': 'benjos'},
            'executed': True}

        updated_owners = ['sys', 'jeff', 'chris', 'cray']

        proposal_state = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal, proposal_state)
        self.assertEqual(updated_owners, self.multi_sign.owners.get())

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
                    'new_owner': 419,    # should be string
                    'existing_owner': 'benjos'}})

        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'replace_owner': {
                    'new_owner': 'cray',
                    'existing_owner': 419}})  # should be string

## register_action

    def test_submit_proposal_owner_proposing_to_register_action_contract_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
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

        owner_confirm = self.multi_sign.confirmations[2, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)

    def test_submit_proposal_owner_confirming_to_register_an_action_contract_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'register_action': {
                    'action': 'gToken',
                    'contract': 'action_token'}})

        executed_proposal = {
            'type': 'state_update',
            'register_action': {
                    'action': 'gToken',
                    'contract': 'action_token'},
            'executed': True}

        self.multi_sign.confirm_proposal(signer='chris', proposal_id=2)

        proposal_state = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal, proposal_state)
        self.assertEqual('action_token', self.multi_sign.actions['gToken'])
        
    def test_submit_proposal_owner_proposing_to_register_an_already_registered_action_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'register_action': {
                        'action': 'sToken',
                        'contract': 'action_token'}})
            self.multi_sign.confirm_proposal(signer='benjos', proposal_id=2)

    def test_submit_proposal_owner_proposing_to_register_action_contract_not_owned_by_multisg_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'register_action': {
                        'action': 'qToken',
                        'contract': 'action_submit'}})
            self.multi_sign.confirm_proposal(signer='benjos', proposal_id=2)

    def test_submit_proposal_owner_proposing_to_register_a_non_compliant_action_contract_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'register_action': {
                        'action': 'n_contract',
                        'contract': 'non_lst001'}})
            self.multi_sign.confirm_proposal(signer='benjos', proposal_id=2)

    def test_submit_proposal_if_register_action_value_is_not_string_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'register_action': {
                        'action': 'sToken',
                        'contract': 419}})  # should be string
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'register_action': {
                        'action': 419,  # should be string
                        'contract': 'action_token'}})

## unregister_action

    def test_submit_proposal_owner_proposing_to_unregister_action_contract_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'unregister_action': 'sToken'})

        proposal = {
            'type': 'state_update',
            'unregister_action': 'sToken',
            'executed': False}
        
        submitted_proposal = self.multi_sign.proposal[2]
        owner_confirm = self.multi_sign.confirmations[2, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)

    def test_submit_proposal_owner_confirming_to_unregister_action_contract_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'unregister_action': 'sToken'})

        executed_proposal = {
            'type': 'state_update',
            'unregister_action': 'sToken',
            'executed': True}

        self.multi_sign.confirm_proposal(signer='chris', proposal_id=2)

        proposal_state = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal, proposal_state)
        with self.assertRaises(AttributeError):
            self.multi_sign.actions['sToken']

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
                    'unregister_action': 419})  # should be string

## change_confirmation

    def test_submit_proposal_owner_proposing_to_change_required_confirmations_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'change_requirement': 3})

        proposal = {
            'type': 'state_update',
            'change_requirement': 3,
            'executed': False}
        
        submitted_proposal = self.multi_sign.proposal[2]
        owner_confirm = self.multi_sign.confirmations[2, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)
    def test_submit_proposal_owner_confirming_to_change_confirmation_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'change_requirement': 3})

        executed_proposal = {
            'type': 'state_update',
            'change_requirement': 3,
            'executed': True}

        self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)
        
        owner_confirmed = self.multi_sign.confirmations[2, 'sys']
        proposal_state = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal, proposal_state)
        self.assertEqual(3, self.multi_sign.required.get())
        self.assertTrue(owner_confirmed)

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
        self.multi_sign.submit_proposal(
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

        submitted_proposal = self.multi_sign.proposal[2]
        owner_confirm = self.multi_sign.confirmations[2, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)

    def test_submit_proposal_owner_confirming_proposal_to_change_dailylimit_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'change_dailylimit': {
                    'token': 'currency',
                    'amount': ContractingDecimal('3000')}})

        executed_proposal = {
            'type': 'state_update',
            'change_dailylimit': {
                'token': 'currency',
                'amount': ContractingDecimal('3000')},
            'executed': True}

        self.multi_sign.confirm_proposal(signer='benjos', proposal_id=2)

        owner_confirmed = self.multi_sign.confirmations[2, 'sys']
        proposal_state = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal, proposal_state)
        self.assertEqual(ContractingDecimal('3000'), self.multi_sign.daily_limit['currency'])
        self.assertTrue(owner_confirmed)

    def test_submit_proposal_if_change_dailylimit_values_not_appropriate_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'change_dailylimit': {
                        'token': 'currency',
                        'amount': '3000'}})  # supposed to be int, float, or decimal


# lst001_proposal tests

    def test_submit_proposal_owner_proposing_a_token_transfer_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
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

        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)
        

    def test_submit_proposal_owner_proposing_a_token_approve_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
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

        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)

    def test_submit_proposal_owner_proposing_a_token_transfer_from_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
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

        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)

    def test_submit_proposal_if_token_transfer_proposal_contain_inappropriate_data_type_should_fail(self):
        with self.assertRaises(AttributeError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 419,  # supposed to be string
                    'payload': {
                        'method': 'transfer',
                        'amount': 456,
                        'to': 'test_test'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 419,  # supposed to be string
                        'amount': 456,
                        'to': 'test_test'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 'transfer',
                        'amount': 456,
                        'to': 419}})  # supposed to be string
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 'transfer',
                        'amount': '456',  # supposed to be int, float, or decimal
                        'to': 'test_test'}})  

    def test_submit_proposal_if_token_approve_proposal_contain_inappropriate_data_type_should_fail(self):
        with self.assertRaises(AttributeError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 419,  # supposed to be string
                    'payload': {
                        'method': 'approve',
                        'amount': 456,
                        'to': 'test_test'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 419,  # supposed to be string
                        'amount': 456,
                        'to': 'test_test'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 'approve',
                        'amount': '456',  # supposed to be int, float, or decimal
                        'to': 'test_test'}})  
            

    def test_submit_proposal_if_token_transfer_from_proposal_contain_inappropriate_data_type_should_fail(self):
        with self.assertRaises(AttributeError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 419,  # supposed to be string
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
                        'method': 419,  # supposed to be string
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
                        'to': 419,  # supposed to be string
                        'main_account': 'vault'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'token': 'currency',
                    'payload': {
                        'method': 'transfer_from',
                        'amount': '456',   # supposed to be int, float, or decimal
                        'to': 'test_test',  
                        'main_account': 'vault'}})

    def test_other_owner_confirming_token_transfer_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer',
                    'amount': 456,
                    'to': 'test_test'}})

        executed_proposal = {
            'type': 'lst001_proposal',
            'token': 'currency',
                'payload': {
                    'method': 'transfer',
                    'amount': 456,
                    'to': 'test_test'},
            'executed': True}

        result = self.multi_sign.confirm_proposal(signer='benjos', proposal_id=2)
        proposal_state = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal, proposal_state)
        self.assertTrue(result)

    def test_other_owner_confirming_token_approve_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'approve',
                    'amount': 456,
                    'to': 'test_test'}})

        executed_proposal = {
            'type': 'lst001_proposal',
            'token': 'currency',
                'payload': {
                    'method': 'approve',
                    'amount': 456,
                    'to': 'test_test'},
            'executed': True}

        result = self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)
        proposal_state = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal, proposal_state)
        self.assertTrue(result)

    def test_other_owner_confirming_token_transfer_from_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer_from',
                    'amount': 456,
                    'to': 'test_test',
                    'main_account': 'vc'}})

        executed_proposal = {
                'type': 'lst001_proposal',
                'token': 'currency',
                'payload': {
                    'method': 'transfer_from',
                    'amount': 456,
                    'to': 'test_test',
                    'main_account': 'vc'},
                'executed': True}

        result = self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)
        proposal_state = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal, proposal_state)
        self.assertTrue(result)

    def test_owner_transferring_more_than_dailylimit_should_fail(self):
        submitted_proposal = self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer',
                    'amount': 501,
                    'to': 'test_test'}})

        
        with self.assertRaises(AssertionError):
            self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)
        
        

# action_proposal tests

    def test_submit_proposal_owner_proposing_an_action_txn_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
            propsl = {
                'action': 'sToken',
                'bulk': False,
                'payload': {
                    'function': 'transfer',
                    'amount': 20,
                    'to': 'some_initiative'}})

        proposal = {
                'type': 'action_proposal',
                'action': 'sToken',
                'bulk': False,
                'payload': {
                    'function': 'transfer',
                    'amount': 20,
                    'to': 'some_initiative'},
                'executed': False}

        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)

    def test_submit_proposal_owner_proposing_a_nonexisting_action_txn_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action': 'qToken',
                    'bulk': False,
                    'payload': {
                        'function': 'transfer',
                        'amount': 20,
                        'to': 'some_initiative'}})

    def test_submit_proposal_if_action_txn_contain_inappropriate_data_type_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action': 419, #supposed to be a string
                    'bulk': False,
                    'payload': {
                        'function': 'transfer',
                        'amount': 20,
                        'to': 'some_initiative'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action': 'sToken',
                    'bulk': 'False', #supposed to be a bolean
                    'payload': {
                        'function': 'transfer',
                        'amount': 20,
                        'to': 'some_initiative'}})

    def test_submit_proposal_other_owners_confirming_an_action_txn_to_execute_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
            propsl = {
                'action': 'sToken',
                'bulk': False,
                'payload': {
                    'function': 'transfer',
                    'amount': 20,
                    'to': 'some_initiative'}})

        executed_proposal = {
                'type': 'action_proposal',
                'action': 'sToken',
                'bulk': False,
                'payload': {
                    'function': 'transfer',
                    'amount': 20,
                    'to': 'some_initiative'},
                'executed': True}

        result = self.multi_sign.confirm_proposal(signer='chris', proposal_id=2)
        self.assertEqual(executed_proposal, submitted_proposal)
        self.assertTrue(result)

    def test_submit_proposal_owner_confirming_a_bulk_txn_action_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
            propsl = {
                'action': 'sToken',
                'bulk': True,
                'payload': [{
                    'function': 'transfer',
                    'amount': 20,
                    'to': 'some_initiative'},
                    {
                    'function': 'transfer',
                    'amount': 20,
                    'to': 'some_initiative'},
                    {
                    'function': 'transfer',
                    'amount': 20,
                    'to': 'some_initiative'}]})

        executed_proposal = {
                'type': 'action_proposal',
                'action': 'sToken',
                'bulk': True,
                'payload': [{
                    'function': 'transfer',
                    'amount': 20,
                    'to': 'some_initiative'},
                    {'function': 'transfer',
                    'amount': 20,
                    'to': 'some_initiative'},
                    {'function': 'transfer',
                    'amount': 20,
                    'to': 'some_initiative'}],
                'executed': True}

        self.multi_sign.confirm_proposal(signer='benjos',proposal_id=2)
        submitted_proposal = self.multi_sign.proposal[2]
        self.assertEqual(executed_proposal,  submitted_proposal)

    def test_submit_proposal_bulk_payload_not_list_should_fail(self):
        with self.assertRaises(AssertionError):
            submitted_proposal = self.multi_sign.submit_proposal(
                propsl = {
                    'action': 'sToken',
                    'bulk': True,
                    'payload': ({
                        'function': 'transfer',
                        'amount': 20,
                        'to': 'some_initiative'},
                        {
                        'function': 'transfer',
                        'amount': 20,
                        'to': 'some_initiative'},
                        {
                        'function': 'transfer',
                        'amount': 20,
                        'to': 'some_initiative'})})        
        
# external_action_proposal tests

    def test_submit_proposal_owner_proposing_an_ext_action_txn_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
            propsl = {
                'action_core': 'action_core',
                'action': 'action_submit',
                'payload': {
                    'function': 'submit',
                    'proposal': 'let get a chart'}})

        proposal = {
                'type': 'external_action_proposal',
                'action_core': 'action_core',
                'action': 'action_submit',
                'payload': {
                    'function': 'submit',
                    'proposal': 'let get a chart'},
                'executed': False}

        owner_confirm = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(owner_confirm)

    def test_submit_proposal_if_ext_action_txn_contain_inappropriate_data_type_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action_core': 419,  # supposed to be string
                    'action': 'action_submit',
                    'payload': {
                        'function': 'submit',
                        'proposal': 'let get a chart'}})
        with self.assertRaises(AssertionError):
            self.multi_sign.submit_proposal(
                propsl = {
                    'action_core': 'action_core',
                    'action': 419,   # supposed to be string
                    'payload': {
                        'function': 'submit',
                        'proposal': 'let get a chart'}})

    def test_submit_proposal_other_owners_confirming_an_ext_action_txn_to_execute_should_succeed(self):
        submitted_proposal = self.multi_sign.submit_proposal(
            propsl = {
                'action_core': 'action_core',
                'action': 'action_submit',
                'payload': {
                    'function': 'submit',
                    'proposal': 'let get a chart'}})

        executed_proposal = {
            'type': 'external_action_proposal',    
            'action_core': 'action_core',
            'action': 'action_submit',
            'payload': {
                'function': 'submit',
                'proposal': 'let get a chart'},
            'executed': True}
        
        result = self.multi_sign.confirm_proposal(signer='chris', proposal_id=2)
        
        action_state = self.action_core.S['con_multi_sign']
        self.assertEqual(executed_proposal, submitted_proposal)
        self.assertEqual('let get a chart', action_state)
        self.assertTrue(result)


# specific methods tests

    def test_confirm_proposal_owner_confirming_a_nonexisting_proposal_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.confirm_proposal(proposal_id=0)

    def test_confirm_proposal_owner_confirming_an_executed_proposal_should_fail(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'add_owner': 'traderrob'})
        
        self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)
        with self.assertRaises(AssertionError): 
            self.multi_sign.confirm_proposal(signer='chris', proposal_id=2) 

    def test_confirm_proposal_same_owner_confirming_a_proposal_twice_should_fail(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'add_owner': 'vogel'})
        
        self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)
        with self.assertRaises(AssertionError): 
            self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)

    def test_revoke_proposal_owner_revoking_a_nonexisting_proposal_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.revoke_proposal(proposal_id=0)      

    def test_revoke_proposal_owner_revoking_an_executed_proposal_should_fail(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'remove_owner': 'chris'})

        self.multi_sign.confirm_proposal(signer='jeff', proposal_id=2)
        with self.assertRaises(AssertionError):
            self.multi_sign.revoke_proposal(proposal_id=2)

    def test_revoke_proposal_owner_revoking_a_proposal_not_first_confirmed_by_same_owner_should_fail(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'remove_owner': 'chris'})

        with self.assertRaises(AssertionError):
            self.multi_sign.revoke_proposal(signer='benjos', proposal_id=2)

    def test_is_under_limit_accumulated_transfers_beyond_dailylimit_should_fail(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer',
                    'amount': 200,
                    'to': 'test_test'}})

        self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer',
                    'amount': 200,
                    'to': 'clay'}})

        self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer',
                    'amount': 200,
                    'to': 'mike'}})

        self.multi_sign.confirm_proposal(signer='benjos',proposal_id=2)
        self.multi_sign.confirm_proposal(signer='jeff', proposal_id=3)
        with self.assertRaises(AssertionError):
            self.multi_sign.confirm_proposal(signer='chris', proposal_id=4)

    def test_is_under_limit_regular_time_interval_always_1_day(self):
        env = {'now': Datetime(hour=18, day=8, month=5, year=2022)}
        
        self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer',
                    'amount': 200,
                    'to': 'test_test'}})
        self.multi_sign.confirm_proposal( environment=env, signer='chris', proposal_id=2)
        last_day = self.multi_sign.last_day.get()
        self.assertEqual(last_day, Datetime(day=8, month=5, year=2022))

    
if __name__ == "__main__":
    unittest.main()
