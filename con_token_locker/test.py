import unittest
from contracting.stdlib.bridge.time import Datetime
from contracting.client import ContractingClient

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.c = ContractingClient()
        self.c.flush()

        with open("../con_basic_token.py") as f:
            contract = f.read()
            self.c.submit(contract, 'basic_token', constructor_args={"vk": "sys"})
            
        with open("./con_token_locker.py") as f:
            code = f.read()
            self.c.submit(code, name="con_token_locker")

        self.basic_token = self.c.get_contract("basic_token")
        self.token_locker = self.c.get_contract("con_token_locker")
        
        #basic token transfers to users to lock
        self.basic_token.transfer(amount=1000, to='user2_to_lock')
        self.basic_token.transfer(amount=1000, to='user3_to_lock')
        self.basic_token.transfer(amount=1000, to='user4_to_lock')
        
        self.setupApprovals()


    def setupApprovals(self):
        #approvals for token_locker contract to spend basic token
        self.basic_token.approve(amount=999999999, to="con_token_locker")
        self.basic_token.approve(signer='user2_to_lock', amount=999999999, to="con_token_locker")
        self.basic_token.approve(signer='user3_to_lock', amount=999999999, to="con_token_locker")
        self.basic_token.approve(signer='user4_to_lock', amount=999999999, to="con_token_locker")


    def tearDown(self):
        self.c.flush()


    def test_lock_entering_a_negative_amount_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)} 

        #user entering a positive amount raises no error
        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))
        
        #user entering a negative amount raises an error
        with self.assertRaises(AssertionError):
            self.token_locker.lock(contract="basic_token", amount=-50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40)) 
              
        
    def test_lock_locking_first_time_without_a_date_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
    	 
        #user locking first time without a date
        with self.assertRaises(AssertionError):
            self.token_locker.lock(environment=env, contract="basic_token", amount=50)
            
            
    def test_lock_locking_first_time_with_a_set_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}  
        
        #user locking first time with a set date
        l = self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #checks
        self.assertEqual(l["amount"],50)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        
        
    def test_lock_locking_more_tokens_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user locking more tokens
        l = self.token_locker.lock(environment=env, contract="basic_token", amount=30)
        #checks
        self.assertEqual(l["amount"],80)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))
     
    
    def test_lock_locking_more_tokens_with_a_set_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user locking more again with a set date. however previous date does not change
        l = self.token_locker.lock(environment=env, contract="basic_token", amount=30, date=Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        #checks
        self.assertEqual(l["amount"],80)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        	

    def test_extend_lock_no_locked_tokens_extending_date_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        #user with zero tokens extending lock period
        with self.assertRaises(AssertionError):
            self.token_locker.extend_lock(signer="Benji", environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=20)) 
            
            
    def test_extend_lock_extending_date_with_locked_tokens_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user with locked tokens extending lock period
        l = self.token_locker.extend_lock(environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=20))
        #checks
        self.assertEqual(l["amount"],50)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=8, day=5, hour=23, minute=20))
        

    def test_extend_lock_setting_an_earlier_and_same_lock_date_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=8, day=5, hour=23, minute=20))
        #user setting earlier and same lock date
        with self.assertRaises(AssertionError):
            self.token_locker.extend_lock(environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=19))
        with self.assertRaises(AssertionError):
            self.token_locker.extend_lock(environment=env, contract="basic_token", date=Datetime(year=2022, month=8, day=5, hour=23, minute=20)) 

    
    def test_burn_no_locked_tokens_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        #user with no locked tokens tries to burn
        with self.assertRaises(AssertionError):
            self.token_locker.burn(signer="Benji", contract="basic_token")
    
    
    def test_burn_having_locked_tokens_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))            
        #user with locked tokens burns
        l = self.token_locker.burn(contract="basic_token")
        #checks
        self.assertEqual(l["amount"],0)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))

  
    def test_withdraw_no_locked_tokens_withdrawing_should_fail(self): 
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
           
        #user with no locked tokens tries to make a withdrawal
        with self.assertRaises(AssertionError):
            self.token_locker.withdraw(signer="Benji", contract="basic_token")
            
    def test_withdraw_earlier_withdrawal_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_earlier = {"now": Datetime(year=2022, month=2, day=3, hour=14, minute=39)}
        
        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user with locked tokens tries to make an earlier withdrawal 
        with self.assertRaises(AssertionError):
            self.token_locker.withdraw(environment=withdrawal_earlier, contract="basic_token")
        
    def test_withdraw_withdrawal_on_exact_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_exact = {"now": Datetime(year=2022, month=2, day=3, hour=14, minute=40)}
        
        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))
        #user with locked tokens makes a withdrawal on exact unlock date
        l = self.token_locker.withdraw(environment=withdrawal_exact, contract="basic_token")
        #checks
        self.assertEqual(l["amount"],0)
        self.assertEqual(l["unlock_date"], Datetime(year=2022, month=2, day=3, hour=14, minute=40))


    def test_withdraw_part_entering_a_negative_amount_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_date = {"now": Datetime(year=2022, month=3, day=3, hour=14, minute=40)}

        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))    

        #user enters a positive amount raises no error
        self.token_locker.withdraw_part(environment=withdrawal_date, contract="basic_token", amount=10)

        
        #user enters a negative amount raises an error
        with self.assertRaises(AssertionError):
            self.token_locker.withdraw_part(contract="basic_token", amount=-10)
    
    
    def test_withdraw_part_no_locked_tokens_withdrawing_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        
        #user with no locked tokens tries to make a withdrawal
        with self.assertRaises(AssertionError):
            self.token_locker.withdraw_part(signer="Benji", contract="basic_token", amount=10)
            
    def test_withdraw_part_locked_tokens_withdrawing_earlier_should_fail(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_earlier = {"now": Datetime(year=2022, month=2, day=3, hour=14, minute=39)}  
        
        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))         
        #user with locked tokens tries to make an earlier withdrawal 
        with self.assertRaises(AssertionError):
            self.token_locker.withdraw_part(environment=withdrawal_earlier, contract="basic_token", amount=10)
        
    def test_withdraw_part_locked_tokens_withdrawing_on_exact_date_should_succeed(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        withdrawal_exact = {"now": Datetime(year=2022, month=2, day=3, hour=14, minute=40)}  
        
        self.token_locker.lock(environment=env, contract="basic_token", amount=50, date=Datetime(year=2022, month=2, day=3, hour=14, minute=40))    
        #user with locked tokens tries to make a withdrawal on exact date
        l = self.token_locker.withdraw_part(environment=withdrawal_exact, contract="basic_token", amount=10)
        #checks
        self.assertEqual(l["amount"],40)
        
    def test_multiple_interactions_with_token_locker(self):
        env = {"now": Datetime(year=2022, month=2, day=3, hour=10, minute=40)}
        user2_lock_date = {"now": Datetime(year=2022, month=3, day=3, hour=14, minute=40)}
        user3_lock_date = {"now": Datetime(year=2022, month=4, day=3, hour=14, minute=40)}
        user4_lock_date = {"now": Datetime(year=2022, month=5, day=3, hour=14, minute=40)}

        #users lock token
        self.token_locker.lock(signer='user2_to_lock', environment=env, contract="basic_token", amount=20, date=Datetime(year=2022, month=3, day=3, hour=14, minute=40))
        self.token_locker.lock(signer='user3_to_lock', environment=env, contract="basic_token", amount=30, date=Datetime(year=2022, month=4, day=3, hour=14, minute=40)) 
        self.token_locker.lock(signer='user4_to_lock', environment=env, contract="basic_token", amount=40, date=Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        #checks for locked tokens
        self.assertEqual(self.token_locker.locked_tokens['basic_token', 'user2_to_lock'], 20)
        self.assertEqual(self.token_locker.locked_tokens['basic_token', 'user3_to_lock'], 30)
        self.assertEqual(self.token_locker.locked_tokens['basic_token', 'user4_to_lock'], 40)

        #user2 withdraws 10 basic tokens
        self.token_locker.withdraw_part(signer='user2_to_lock', environment=user2_lock_date, contract="basic_token", amount=10)
        #user3 extends locking period to month 5
        self.token_locker.extend_lock(signer='user3_to_lock', environment=env, contract="basic_token", date=Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        #user4 locks additional 10 basic tokens
        self.token_locker.lock(signer='user4_to_lock', environment=env, contract="basic_token", amount=10, date=Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        #user4 tries to withdraw more than in posession
        with self.assertRaises(AssertionError):
            self.token_locker.withdraw_part(signer='user4_to_lock', environment=user4_lock_date, contract="basic_token", amount=51)

        #checks for new states
        self.assertEqual(self.token_locker.locked_tokens['basic_token', 'user2_to_lock'], 10)
        self.assertEqual(self.token_locker.lock_info['basic_token', 'user3_to_lock']["unlock_date"], Datetime(year=2022, month=5, day=3, hour=14, minute=40))
        self.assertEqual(self.token_locker.locked_tokens['basic_token', 'user4_to_lock'], 50)


if __name__ == "__main__":
    unittest.main()
