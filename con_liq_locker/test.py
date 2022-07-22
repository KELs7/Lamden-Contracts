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
        
        #currency transfers to users to add liquidity to pool
        self.currency.transfer(amount=1000, to='user2_with_lp')
        self.currency.transfer(amount=1000, to='user3_with_lp')
        self.currency.transfer(amount=1000, to='user4_with_lp')

        #basic_token transfers to users to add liquidity to pool
        self.basic_token.transfer(amount=2000, to='user2_with_lp')
        self.basic_token.transfer(amount=2000, to='user3_with_lp')
        self.basic_token.transfer(amount=2000, to='user4_with_lp')

        self.setupApprovals()

        self.dex.create_market(contract="basic_token", currency_amount=1000, token_amount=2000)
        #users add liquidity to basic_token/currency pool
        self.dex.add_liquidity(signer='user2_with_lp', contract="basic_token", currency_amount=500)
        self.dex.add_liquidity(signer='user3_with_lp', contract="basic_token", currency_amount=600)
        self.dex.add_liquidity(signer='user4_with_lp', contract="basic_token", currency_amount=800)


    def setupApprovals(self):
        #approvals for dex to spend currency
        self.currency.approve(amount=999999999, to="dex")
        self.currency.approve(signer='user2_with_lp', amount=999999999, to="dex")
        self.currency.approve(signer='user3_with_lp', amount=999999999, to="dex")
        self.currency.approve(signer='user4_with_lp', amount=999999999, to="dex")

        #approvals for dex to spend basic_token
        self.basic_token.approve(amount=999999999, to="dex")
        self.basic_token.approve(signer='user2_with_lp', amount=999999999, to="dex")
        self.basic_token.approve(signer='user3_with_lp', amount=999999999, to="dex")
        self.basic_token.approve(signer='user4_with_lp', amount=999999999, to="dex")
        
        #approvals for liq_locker contract to spend LPs
        self.dex.approve_liquidity(contract="basic_token", to="con_liq_locker", amount=999999999)
        self.dex.approve_liquidity(signer='user2_with_lp', contract="basic_token", to="con_liq_locker", amount=999999999)
        self.dex.approve_liquidity(signer='user3_with_lp', contract="basic_token", to="con_liq_locker", amount=999999999)
        self.dex.approve_liquidity(signer='user4_with_lp', contract="basic_token", to="con_liq_locker", amount=999999999)

    def tearDown(self):
        self.c.flush()


    def test_lock_lp_entering_a_negative_amount_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)} 

        #user entering a positive amount raises no error
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))

        #user entering a negative amount raises an error
        with self.assertRaises(AssertionError):
            self.liq_locker.lock_lp(signer='user2', environment=env, contract="basic_token", amount=-50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))

    def test_lock_lp_locking_first_time_with_a_set_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}  
        
        #user locking first time with a set date
        l = self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))
        #checks
        self.assertEqual(l["amount"],50)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=3, day=3, hour=14, minute=40))
             
    def test_lock_lp_locking_first_time_without_a_date_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}  

        #user locking first time without a date raises an error
        with self.assertRaises(AssertionError):
            self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50)
                           
    def test_lock_lp_locking_more_lp_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))
        #user locking more lp
        l = self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=30)
        #checks
        self.assertEqual(l["amount"],80)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=3, day=3, hour=14, minute=40))
     
    def test_lock_lp_locking_more_lp_with_a_set_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user locking more again with a set date. however previous date does not change
        l = self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=30, date=Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        #checks
        self.assertEqual(l["amount"],80)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))

    
    def test_extend_lock_extending_date_with_lp_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user with lp extending lock period
        l = self.liq_locker.extend_lock(environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=20))
        #checks
        self.assertEqual(l["amount"],50)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=8, day=5, hour=23, minute=20))
    	

    def test_extend_lock_zero_lp_extending_date_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        #user with zero lp extending lock period
        with self.assertRaises(AssertionError):
            self.liq_locker.extend_lock(signer="Benji", environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=20))        

    def test_extend_lock_setting_an_earlier_or_same_lock_date_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        #user setting a latter lock date raises no error
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=8, day=5, hour=23, minute=20))

        #user setting earlier and same lock date raises error
        with self.assertRaises(AssertionError):
            self.liq_locker.extend_lock(signer='user2', environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=19))
        with self.assertRaises(AssertionError):
            self.liq_locker.extend_lock(signer='user3', environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=20) )

    def test_burn_lp_having_lp_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))            
        #user with lp burns
        l = self.liq_locker.burn_lp(contract="basic_token")
        #checks
        self.assertEqual(l["amount"],0)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=3, day=3, hour=14, minute=40))

    def test_burn_lp_zero_lp_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        #user with zero lps tries to burn
        with self.assertRaises(AssertionError):
            self.liq_locker.burn_lp(signer="Benji", contract="basic_token")

    def test_withdraw_withdrawal_on_exact_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_exact = {"now": Datetime(year=2022, month=3, day=3, hour=14, minute=40)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))
        #user with lp makes a withdrawal on exact unlock date
        l = self.liq_locker.withdraw(environment=withdrawal_exact, contract="basic_token")
        #checks
        self.assertEqual(l["amount"],0)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=3, day=3, hour=14, minute=40))

    def test_withdraw_zero_lp_withdrawing_should_fail(self): 
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
           
        #user with zero lp tries to make a withdrawal
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw(signer="Benji", environment=env, contract="basic_token")
            
    def test_withdraw_earlier_withdrawal_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        earlier_lock_date = {"now": Datetime(year=2022, month=2, day=3, hour=14, minute=39)}
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user with lp tries to make an earlier withdrawal 
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw(environment=earlier_lock_date, contract="basic_token")

    def test_withdraw_part_entering_a_negative_amount_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_date = {"now": Datetime(year=2022, month=3, day=3, hour=14, minute=40)}

        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))    

        #user enters a positive amount raises no error
        self.liq_locker.withdraw_part(environment=withdrawal_date, contract="basic_token", amount=10)

        #user enters a negative amount raises an error
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw_part(signer='user2', environment=withdrawal_date, contract="basic_token", amount=-10)

    def test_withdraw_part_lp_withdrawing_on_exact_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_exact = {"now": Datetime(year=2022, month=3, day=3, hour=14, minute=40)}  
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))    
        #user with lp tries to make a withdrawal on exact date
        l = self.liq_locker.withdraw_part(environment=withdrawal_exact, contract="basic_token", amount=10)
        #checks
        self.assertEqual(l["amount"],40)
    
    def test_withdraw_part_zero_lp_withdrawing_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        #user with zero lp tries to make a withdrawal
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw_part(signer="Benji", environment=env, contract="basic_token", amount=10)
            
    def test_withdraw_part_lp_withdrawing_earlier_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_earlier = {"now": Datetime(year=2022, month=3, day=3, hour=14, minute=39)}  
        
        self.liq_locker.lock_lp(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))         
        #user with lp tries to make an earlier withdrawal 
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw_part(environment=withdrawal_earlier, contract="basic_token", amount=10)

    def test_multiple_interactions_with_lp_locker(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        user2_lock_date = {"now": Datetime(year=2022, month=3, day=3, hour=14, minute=40)}
        user3_lock_date = {"now": Datetime(year=2022, month=4, day=3, hour=14, minute=40)}
        user4_lock_date = {"now": Datetime(year=2022, month=5, day=3, hour=14, minute=40)}

        #users with lp lock lp
        self.liq_locker.lock_lp(signer='user2_with_lp', environment=env, contract="basic_token", amount=20, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))
        self.liq_locker.lock_lp(signer='user3_with_lp', environment=env, contract="basic_token", amount=30, date=Datetime(year=2022, month=4, day=3, hour=14, minute=40)) 
        self.liq_locker.lock_lp(signer='user4_with_lp', environment=env, contract="basic_token", amount=40, date=Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        #checks for locked lps
        self.assertEqual(self.liq_locker.lp_points['basic_token', 'user2_with_lp'], 20)
        self.assertEqual(self.liq_locker.lp_points['basic_token', 'user3_with_lp'], 30)
        self.assertEqual(self.liq_locker.lp_points['basic_token', 'user4_with_lp'], 40)

        #user2 withdraws 10LP
        self.liq_locker.withdraw_part(signer='user2_with_lp', environment=user2_lock_date, contract="basic_token", amount=10)
        #user3 extends locking period to month 5
        self.liq_locker.extend_lock(signer='user3_with_lp', environment=env, contract="basic_token", date=Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        #user4 locks additional 10LP
        self.liq_locker.lock_lp(signer='user4_with_lp', environment=env, contract="basic_token", amount=10, date=Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        #user4 tries to withdraw more than LPs
        with self.assertRaises(AssertionError):
            self.liq_locker.withdraw_part(signer='user4_with_lp', environment=user4_lock_date, contract="basic_token", amount=51)

        #checks for new states
        self.assertEqual(self.liq_locker.lp_points['basic_token', 'user2_with_lp'], 10)
        self.assertEqual(self.liq_locker.lock_info['basic_token', 'user3_with_lp']["unlock_date"], Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        self.assertEqual(self.liq_locker.lp_points['basic_token', 'user4_with_lp'], 50)


if __name__ == "__main__":
    unittest.main()
