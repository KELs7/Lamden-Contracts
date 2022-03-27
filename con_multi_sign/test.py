import unittest
from contracting.stdlib.bridge.time import Datetime
from contracting.client import ContractingClient

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.c = ContractingClient()
        self.c.flush()

        with open("../currency.s.py") as f:
            contract = f.read()
            self.c.submit(contract, 'currency', constructor_args={"vk": "sys"})

        with open("../con_basic_token.py") as f:
            contract = f.read()
            self.c.submit(contract, 'basic_token', constructor_args={"vk": "sys"})

        with open("./con_multi_sign.py") as f:
            code = f.read()
            self.c.submit(code, name="con_multi_sign.py")

        self.currency = self.c.get_contract("currency")
        self.basic_token = self.c.get_contract("basic_token")
        self.multi_sign = self.c.get_contract("con_multi_sign")
        
        self.setupApprovals()


    def setupApprovals(self):
        self.currency.approve(amount=999999999, to="con_multi_sign")
        self.basic_token.approve(amount=999999999, to="con_multi_sign")


    def tearDown(self):
        self.c.flush()

    def test_addOwner_adding_owner_must_succeed(self):
        self.multi_sign.addOwner("123abc")
        self.assertEqual(self.c.get_var("con_multi_sign", owners), 2)
        print('not cool')
