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
            self.c.submit(contract, 'non_lst001')

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

# state_updates proposal tests

    def test_submit_proposal_owner_proposing_to_add_new_owner_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'add_owner': 'traderrob'})

        proposal = {
            'type': 'state_update',
            'add_owner': 'traderrob',
            'executed': False}
        
        submitted_proposal = self.multi_sign.proposal[1]
        confirmation = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(confirmation)

    def test_submit_proposal_owner_proposing_to_remove_owner_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'remove_owner': 'chris'})

        proposal = {
            'type': 'state_update',
            'remove_owner': 'chris',
            'executed': False}
        
        submitted_proposal = self.multi_sign.proposal[1]
        confirmation = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(confirmation)

    def test_submit_proposal_owner_proposing_to_replace_owner_should_succeed(self):
        self.multi_sign.submit_proposal(
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
        
        submitted_proposal = self.multi_sign.proposal[1]
        confirmation = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(confirmation)

    def test_submit_proposal_owner_proposing_to_register_action_contract_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'register_action': {
                    'action': 'vToken',
                    'contract': 'con_action'}})

        proposal = {
            'type': 'state_update',
            'register_action': {
                    'action': 'vToken',
                    'contract': 'con_action'},
            'executed': False}
        
        submitted_proposal = self.multi_sign.proposal[1]
        confirmation = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(confirmation)

    def test_submit_proposal_owner_proposing_to_unregister_action_contract_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'unregister_action': 'sToken'})

        proposal = {
            'type': 'state_update',
            'unregister_action': 'sToken',
            'executed': False}
        
        submitted_proposal = self.multi_sign.proposal[1]
        confirmation = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(confirmation)

    def test_submit_proposal_owner_proposing_to_change_required_confirmation_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'change_requirement': 3})

        proposal = {
            'type': 'state_update',
            'change_requirement': 3,
            'executed': False}
        
        submitted_proposal = self.multi_sign.proposal[1]
        confirmation = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(confirmation)

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
        
        submitted_proposal = self.multi_sign.proposal[1]
        confirmation = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(confirmation)

    def test_submit_proposal_owner_proposing_to_change_action_dailylimit_should_succeed(self):
        self.multi_sign.submit_proposal(
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
        
        submitted_proposal = self.multi_sign.proposal[1]
        confirmation = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(confirmation)

    def test_submit_proposal_owner_proposing_to_change_external_action_dailylimit_should_succeed(self):
        self.multi_sign.submit_proposal(
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
        
        submitted_proposal = self.multi_sign.proposal[1]
        confirmation = self.multi_sign.confirmations[1, 'sys']
        self.assertEqual(proposal, submitted_proposal)
        self.assertTrue(confirmation)

# lst001 proposal tests

    def test_submit_proposal_owner_proposing_a_token_transfer_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer',
                    'amount': 456,
                    'to': 'test_test'}})

    def test_submit_proposal_owner_proposing_a_token_approve_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'approve',
                    'amount': 456,
                    'to': 'test_test'}})

    def test_submit_proposal_owner_proposing_a_token_transfer_from_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'token': 'currency',
                'payload': {
                    'method': 'transfer_from',
                    'amount': 456,
                    'to': 'test_test',
                    'main_account': 'vault'}})

    def test_submit_proposal_owner_proposing_an_action_txn_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'action': 'sToken',
                'bulk': False,
                'payload': {
                    'function': 'vote',
                    'propsl': 'get chart'}})

    def test_submit_proposal_owner_proposing_an_external_action_txn_should_succeed(self):
        self.multi_sign.submit_proposal(
            propsl = {
                'action_core': 'action_core',
                'action': 'token',
                'bulk': False,
                'payload': {
                    'function': 'vote',
                    'propsl': 'get chart'}})



if __name__ == "__main__":
    unittest.main()
