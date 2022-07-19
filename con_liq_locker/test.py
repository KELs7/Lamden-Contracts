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

        with open("../dex.py") as f:
            code = f.read()
            self.c.submit(code, name="dex")

        with open("./con_liq_locker.py") as f:
            code = f.read()
            self.c.submit(code, name="con_liq_locker")

        self.dex = self.c.get_contract("dex")
        self.currency = self.c.get_contract("currency")
        self.basic_token = self.c.get_contract("basic_token")
        self.liq_locker = self.c.get_contract("con_liq_locker")
        
        self.setupApprovals()

        self.dex.create_market(contract="basic_token", currency_amount=1000, token_amount=2000)

    def setupApprovals(self):
        self.currency.approve(amount=999999999, to="dex")
        self.basic_token.approve(amount=999999999, to="dex")
        self.dex.approve_liquidity(contract="basic_token", to="con_liq_locker", amount=999999999)


    def tearDown(self):
        self.c.flush()


    def test_lock_lp_entering_a_negative_amount_should_fail(self):
        #user entering a negative amount
        with self.assertRaises(AssertionError):
            self.liq_locker.lock_lp(contract="basic_token", amount=-50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
              
        
    def test_lock_lp_locking_first_time_without_a_date_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
    	 
        #user locking first time without a date
        with self.assertRaises(AssertionError):
            self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50)
            
            
    def test_lock_lp_locking_first_time_with_a_set_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}  
        
        #user locking first time with a set date
        l = self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #checks
        self.assertEqual(l["amount"],50)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        
        
    def test_lock_lp_locking_more_lp_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user locking more lp
        l = self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=30)
        #checks
        self.assertEqual(l["amount"],80)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))
     
    
    def test_lock_lp_locking_more_lp_with_a_set_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user locking more again with a set date. however previous date does not change
        l = self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=30, date=Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        #checks
        self.assertEqual(l["amount"],80)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        	

    def test_extend_lock_zero_lp_extending_date_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        #user with zero lp extending lock period
        with self.assertRaises(AssertionError):
            self.liq_locker.extend_lock(signer="Benji", environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=20))
            
            
    def test_extend_lock_extending_date_with_lp_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user with lp extending lock period
        l = self.liq_locker.extend_lock(environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=20))
        #checks
        self.assertEqual(l["amount"],50)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=8, day=5, hour=23, minute=20))
        

    def test_extend_lock_setting_an_earlier_and_same_lock_date_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=8, day=5, hour=23, minute=20))
        #user setting earlier and same lock date
        with self.assertRaises(AssertionError):
            self.liq_locker.extend_lock(environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=19))
        with self.assertRaises(AssertionError):
            self.liq_locker.extend_lock(environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=20) )

    
    def test_burn_lp_zero_lp_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        #user with zero lps tries to burn
        with self.assertRaises(AssertionError):
            self.liq_locker.burn_lp(signer="Benji", contract="basic_token")
    
    
    def test_burn_lp_having_lp_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))            
        #user with lp burns
        l = self.liq_locker.burn_lp(contract="basic_token")
        #checks
        self.assertEqual(l["amount"],0)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))

  
    def test_withdraw_zero_lp_withdrawing_should_fail(self): 
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
           
        #user with zero lp tries to make a withdrawal
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw(signer="Benji", contract="basic_token")
            
    def test_withdraw_earlier_withdrawal_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_earlier = {"now": Datetime(year=2022, month=2, day=3, hour=14, minute=39)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user with lp tries to make an earlier withdrawal 
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw(environment=withdrawal_earlier, contract="basic_token")
        
    def test_withdraw_withdrawal_on_exact_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_exact = {"now": Datetime(year=2022, month=2, day=3, hour=14, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user with lp makes a withdrawal on exact unlock date
        l = self.liq_locker.withdraw(environment=withdrawal_exact, contract="basic_token")
        #checks
        self.assertEqual(l["amount"],0)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))


    def test_withdraw_part_entering_a_negative_amount_should_fail(self):
        #user enters a negative amount
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw_part(contract="basic_token", amount=-10)
    
    
    def test_withdraw_part_zero_lp_withdrawing_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        #user with zero lp tries to make a withdrawal
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw_part(signer="Benji", contract="basic_token", amount=10)
            
    def test_withdraw_part_lp_withdrawing_earlier_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_earlier = {"now": Datetime(year=2022, month=2, day=3, hour=14, minute=39)}  
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))         
        #user with lp tries to make an earlier withdrawal 
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw_part(environment=withdrawal_earlier, contract="basic_token", amount=10)
        
    def test_withdraw_part_lp_withdrawing_on_exact_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_exact = {"now": Datetime(year=2022, month=2, day=3, hour=14, minute=40)}  
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))    
        #user with lp tries to make a withdrawal on exact date
        l = self.liq_locker.withdraw_part(environment=withdrawal_exact, contract="basic_token", amount=10)
        #checks
        self.assertEqual(l["amount"],40)
        


if __name__ == "__main__":
    unittest.main()
