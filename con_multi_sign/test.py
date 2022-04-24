import unittest
from decimal import Decimal 
from contracting.stdlib.bridge.time import Datetime
from contracting.client import ContractingClient

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.c = ContractingClient()
        self.c.flush()

        with open("../currency.s.py") as f:
            contract = f.read()
            self.c.submit(contract, 'currency', constructor_args={"vk": "con_multi_sign"})

        with open("../non_lst001.py") as f:
            contract = f.read()
            self.c.submit(contract, 'non_lst001')

        with open("./con_multi_sign.py") as f:
            code = f.read()
            self.c.submit(code, name="con_multi_sign")

        self.currency = self.c.get_contract("currency")
        self.non_lst001 = self.c.get_contract("non_lst001")
        self.multi_sign = self.c.get_contract("con_multi_sign")
        
        self.setupApprovals()


    def setupApprovals(self):
        self.currency.approve(amount=999999999, to="con_multi_sign")

    def tearDown(self):
        self.c.flush()
    
    def test_change_metadata_owners_agreeing_on_a_value_should_succeed(self):
        
        #default number of required confirmations is 2
        #hence two owners/signers with the same chosen value is required to change metadata

        self.multi_sign.change_metadata(signer="jeff", key="req", value=3)
        self.multi_sign.change_metadata(signer="chris", key="req", value=3)
        req = self.c.get_var("con_multi_sign", "required")
        self.assertEqual(req, 3)

        #required confirmations changed to 3 
        #hence three owners/signers with the same chosen value is required to change metadatahence
        
        self.multi_sign.change_metadata(key="dailylimit", value=125.84)
        self.multi_sign.change_metadata(signer="benjos", key="dailylimit", value=125.84)
        self.multi_sign.change_metadata(signer="chris", key="dailylimit", value=125.84)
        dailylimit = self.c.get_var("con_multi_sign", "dailyLimit")
        self.assertEqual(dailylimit, Decimal('125.84'))
    
    def test_change_metadata_entering_incorrect_key_should_fail(self):
        self.multi_sign.change_metadata(signer="jeff", key="req", value=3)
        r = self.multi_sign.change_metadata(signer="chris", key="rec", value=3)
        self.assertEqual(r, "key does not exist!")

        self.multi_sign.change_metadata(key="dailylimit", value=125.84)
        d = self.multi_sign.change_metadata(signer="benjos", key="daily", value=125.84)
        self.assertEqual(d, "key does not exist!")
    
    def test_change_metadata_owners_disagreeing_on_a_value_should_fail(self):
        self.multi_sign.change_metadata(signer="jeff", key="req", value=4)
        r = self.multi_sign.change_metadata(signer="chris", key="req", value=3)
        self.assertEqual(r, "there was no concensus to change required confirmations")

        self.multi_sign.change_metadata(key="dailylimit", value=125.48)
        d = self.multi_sign.change_metadata(signer="benjos", key="dailylimit", value=125.84)
        self.assertEqual(d, "there was no concensus to change dailylimit")

    def test_change_metadata_user_calling_method_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.change_metadata(signer="user123", key="req", value=4)
        with self.assertRaises(AssertionError):
            self.multi_sign.change_metadata(signer="user123", key="dailylimit", value=5000)

    def test_addOwner_owners_agreeing_on_adding_a_newOwner_should_succeed(self):
         #default number of required confirmations is 2
        #hence two owners/signers with the same chosen value is required to add new member

        self.multi_sign.addOwner(signer="chris", newOwner = "traderrob")
        self.multi_sign.addOwner(signer="benjos", newOwner = "traderrob")
        owner_list = ['sys', 'benjos', 'jeff', 'chris', 'traderrob']

        ownerList = self.c.get_var("con_multi_sign", "owners")
        self.assertEqual(ownerList , owner_list)

    def test_addOwner_owner_adding_newOnwer_without_support_of_otherOwners_should_fail(self):
        m = self.multi_sign.addOwner(signer="chris", newOwner = "traderrob")
        #self.multi_sign.addOwner(signer="benjos", newOwner = "traderrob")
        self.assertEqual(m , "there was no concensus to add traderrob")
    
    def test_addOwner_user_adding_a_newOwner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.addOwner(signer = "user123", newOwner = "doug")

    def test_addOwner_owner_adding_an_existingOwner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.addOwner(newOwner = "benjos")   
    
    def test_removeOwner_owner_removing_owner_should_succeed(self):
        #default number of required confirmations is 2
        #hence two owners/signers with the same chosen value is required to remove existingOwner

        self.multi_sign.removeOwner(existingOwner = "jeff")
        self.multi_sign.removeOwner(signer="chris", existingOwner = "jeff")
        owner_list = ['sys', 'benjos', 'chris']
        ownerList = self.c.get_var("con_multi_sign", "owners")
        self.assertEqual(ownerList , owner_list)

    def test_removeOwner_owner_removing_existingOwner_without_support_of_otherOwners_should_fail(self):
        m = self.multi_sign.removeOwner(signer="chris", existingOwner = "benjos")
        #self.multi_sign.addOwner(signer="benjos", newOwner = "traderrob")
        self.assertEqual(m , "there was no concensus to remove benjos")

    def test_removeOwner_user_removing_owner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.removeOwner(signer = "user123", existingOwner = "jeff")

    def test_removeOwner_owner_removing_a_nonExistingOwner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.removeOwner(existingOwner = "doug")
    
    def test_replaceOwner_owner_replacing_owner_should_succeed(self):
        #default number of required confirmations is 2
        #hence two owners/signers with the same chosen value is required to replace existingOwner

        self.multi_sign.replaceOwner(signer="chris", existingOwner = "jeff", newOwner = "yme")
        self.multi_sign.replaceOwner(signer="benjos", existingOwner = "jeff", newOwner = "yme")
        owner_list = ['sys', 'benjos', 'chris', 'yme']
        ownerList = self.c.get_var("con_multi_sign", "owners")
        self.assertEqual(ownerList, owner_list)

    def test_replaceOwner_replacing_existingOwner_without_support_of_otherOwners_should_fail(self):
        #default number of required confirmations is 2
        #hence two owners/signers with the same chosen value is required to replace existingOwner

        m = self.multi_sign.replaceOwner(signer="chris", existingOwner = "jeff", newOwner = "yme")
        self.assertEqual(m, "there was no concensus to replace jeff with yme")

    def test_replaceOwner_user_replacing_owner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.replaceOwner(signer = "user123", existingOwner = "jeff", newOwner = "user456")

    def test_replaceOwner_owner_replacing_a_nonExistingOwner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.replaceOwner(existingOwner = "doug", newOwner = "yme")

    def test_replaceOwner_owner_replacing_owner_with_an_existingOwner_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.replaceOwner(existingOwner = "jeff", newOwner = "benjos")
    
    def test_submitTransaction_owner_submiting_and_confirming_txn_should_succeed(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        txn = {
            'contract': 'currency',
            'amount': 20,
            'to': 'benjos',
            'executed': False
        }
        
        transaction = self.c.get_var("con_multi_sign", "transactions", arguments=[1])
        confirmation = self.c.get_var("con_multi_sign", "confirmations", arguments=[1, "sys"])
        self.assertEqual(txn, transaction)
        self.assertTrue(confirmation)

    def test_submitTransaction_owner_submiting_txn_with_a_lst001_non_compliant_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submitTransaction(contract="non_lst001", amount=20, to="doug")
    
    def test_submitTransaction_user_submiting_txn_should_fail(self):
        with self.assertRaises(AssertionError):
            self.multi_sign.submitTransaction(signer="user123", contract="currency", amount=20, to="doug")
    
    def test_confirmTransaction_other_owner_confirming_txn_should_succeed(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20.56, to="benjos")
        self.multi_sign.confirmTransaction(signer="jeff", transactionId = 1)
        confirmation = self.c.get_var("con_multi_sign", "confirmations", arguments=[1, "jeff"])
        self.assertTrue(confirmation)

    def test_confirmTransaction_other_owner_confirming_to_execute_txn_should_succeed(self):
        self.multi_sign.submitTransaction(signer="jeff", contract="currency", amount=20.56, to="mike")
        self.multi_sign.confirmTransaction(signer="chris", transactionId = 1)
        transaction = self.c.get_var("con_multi_sign", "transactions", arguments=[1])
        self.assertTrue(transaction['executed'])

    def test_confirmTransaction_a_user_confirming_a_txn_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        with self.assertRaises(AssertionError):
            self.multi_sign.confirmTransaction(signer="user123", transactionId = 1)
    
    def test_confirmTransaction_other_owner_confirming_an_executedTxn_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        self.multi_sign.confirmTransaction(signer="chris", transactionId = 1)
        with self.assertRaises(AssertionError):
            self.multi_sign.confirmTransaction(signer="jeff", transactionId = 1)

    def test_confirmTransaction_owner_reconfirming_txn_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        with self.assertRaises(AssertionError):
            self.multi_sign.confirmTransaction(transactionId = 1)
    
    def test_confirmTransaction_other_owner_confirming_a_nonExistingTxn_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        with self.assertRaises(AssertionError):
            self.multi_sign.confirmTransaction(signer="jeff", transactionId = 2)
            
    def test_revokeTransaction_owner_revoking_txn_should_succeed(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        self.multi_sign.revokeTransaction(transactionId = 1)
        confirmation = self.c.get_var("con_multi_sign", "confirmations", arguments=[1, "sys"])
        self.assertFalse(confirmation)

    def test_revokeTransaction_a_user_revoking_a_txn_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        with self.assertRaises(AssertionError):
            self.multi_sign.revokeTransaction(signer="user123", transactionId = 1)

    def test_revokeTransaction_other_owner_revoking_txn_without_previous_confirmation_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        with self.assertRaises(AssertionError):
            self.multi_sign.revokeTransaction(signer="jeff", transactionId = 1)

    #this test does not apply when required confirmations is 2
    #
    #def test_revokeTransaction_other_owner_revoking_txn_with_previous_confirmation_should_succeed(self):
    #    self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
    #    self.multi_sign.confirmTransaction(signer="jeff", transactionId = 1)
    #    self.multi_sign.revokeTransaction(signer="jeff", transactionId = 1)
    #    confirmation = self.c.get_var("con_multi_sign", "confirmations", arguments=[1, "jeff"])
    #    self.assertFalse(confirmation)
    
    def test_revokeTransaction_other_owner_revoking_a_nonExistingTxn_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        with self.assertRaises(AssertionError):
            self.multi_sign.revokeTransaction(signer="jeff", transactionId = 2)
    
    def test_executeTransaction_owner_executing_an_already_executed_txn_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        self.multi_sign.confirmTransaction(signer="jeff", transactionId = 1)
        with self.assertRaises(AssertionError):
            self.multi_sign.executeTransaction(transactionId = 1)

    def test_executeTransaction_owner_executing_a_txn_without_the_required_confirmations_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        executed = self.multi_sign.executeTransaction(transactionId = 1)
        transaction = self.c.get_var("con_multi_sign", "transactions", arguments=[1])
        self.assertFalse(executed)
        self.assertFalse(transaction['executed'])

    def test_executeTransaction_a_user_executing_txn_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        with self.assertRaises(AssertionError):
            self.multi_sign.executeTransaction(signer="user123", transactionId = 1)

    def test_executeTransaction_owner_spending_beyond_dailylimit_should_fail(self):
        self.multi_sign.submitTransaction(contract="currency", amount=1001, to="benjos")
        executed = self.multi_sign.confirmTransaction(signer="jeff", transactionId = 1)
        transaction = self.c.get_var("con_multi_sign", "transactions", arguments=[1])
        self.assertFalse(executed)
        self.assertFalse(transaction['executed'])
    
    def test_getConfirmationCount_user_checking_confirmation_count_should_succeed(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        self.multi_sign.confirmTransaction(signer="chris", transactionId = 1)
        confirmations = self.multi_sign.getConfirmationCount(signer="user123", transactionId = 1) 
        self.assertEqual(confirmations, 2)
    
    def test_getTransactionCount_user_checking_pending_txns_should_succeed(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        self.multi_sign.submitTransaction(signer="jeff", contract="currency", amount=20, to="mike")
        self.multi_sign.submitTransaction(signer="chris", contract="currency", amount=20, to="doug")
        transactions = self.multi_sign.getTransactionCount(signer="user123", pending = True, executed = False)
        self.assertEqual(transactions, 3)

    def test_getTransactionCount_user_checking_executed_txns_should_succeed(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        self.multi_sign.confirmTransaction(signer="chris", transactionId = 1)
        self.multi_sign.submitTransaction(signer="jeff", contract="currency", amount=20, to="mike")
        self.multi_sign.confirmTransaction(transactionId = 2)
        self.multi_sign.submitTransaction(signer="chris", contract="currency", amount=20, to="doug")
        self.multi_sign.confirmTransaction(signer="benjos", transactionId = 3)
        transactions = self.multi_sign.getTransactionCount(signer="user123", pending = False, executed = True)
        self.assertEqual(transactions, 3)

    def test_getTransactionCount_user_checking_pending_and_executed_txns_should_succeed(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        self.multi_sign.submitTransaction(signer="jeff", contract="currency", amount=20, to="mike")
        self.multi_sign.confirmTransaction(transactionId = 2)
        self.multi_sign.submitTransaction(signer="chris", contract="currency", amount=20, to="doug")
        self.multi_sign.confirmTransaction(signer="benjos", transactionId = 3)
        self.multi_sign.submitTransaction(signer="benjos", contract="currency", amount=20, to="doug")
        transactions = self.multi_sign.getTransactionCount(signer="user123", pending = True, executed = True)
        self.assertEqual(transactions, 4)

    def test_getTransactionCount_user_checking_for_no_pending_and_executed_txns_should_succeed(self):
        self.multi_sign.submitTransaction(contract="currency", amount=20, to="benjos")
        self.multi_sign.submitTransaction(signer="jeff", contract="currency", amount=20, to="mike")
        self.multi_sign.confirmTransaction(transactionId = 2)
        self.multi_sign.submitTransaction(signer="chris", contract="currency", amount=20, to="doug")
        self.multi_sign.confirmTransaction(signer="benjos", transactionId = 3)
        self.multi_sign.submitTransaction(signer="benjos", contract="currency", amount=20, to="doug")
        transactions = self.multi_sign.getTransactionCount(signer="user123", pending = False, executed = False)
        self.assertEqual(transactions, 0)
    
if __name__ == "__main__":
        unittest.main()
