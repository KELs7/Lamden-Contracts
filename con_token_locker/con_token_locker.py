I = importlib
lock_info = Hash()
locked_tokens = Hash(default_value=0)


@export
def lock(contract: str, amount: float, date: datetime.datetime = None):
    assert amount > 0, "negative value not allowed!"
    user = ctx.caller
    if locked_tokens[contract, user] > 0:
        token = I.import_module(contract)
        token.transfer_from(amount=amount, to=ctx.this, main_account=user)
        locked_tokens[contract, user] += amount
        lock_info[contract, user]["amount"] += amount
        lock_info[contract, user] = lock_info[contract, user]
        return lock_info[contract, user]
    else:
        assert date, "set a lock date!"
        assert isinstance(date, datetime.datetime), "date is not a datetime type"
        unlock_date = date
        assert unlock_date > now, "unlock_date must be set ahead from now!"
        token = I.import_module(contract)
        token.transfer_from(amount=amount, to=ctx.this, main_account=user)
        locked_tokens[contract, user] += amount
        lock_info[contract, user] = {
            "lock_date": now,
            "amount": locked_tokens[contract, user],
            "unlock_date": unlock_date,
        }
        return lock_info[contract, user]


@export
def extend_lock(contract: str, date: datetime.datetime):
    '''extend locking period whilst your tokens remain ontouched'''
    user = ctx.caller
    assert date, "set a lock date!"
    assert isinstance(date, datetime.datetime), 'date is not a datetime type!'
    assert locked_tokens[contract, user] > 0, "no locked tokens found."
    lock_data = lock_info[contract, user]
    unlock_date = lock_data["unlock_date"]
    extended_date = date
    assert extended_date > unlock_date, "extended date cannot be earlier or previous unlock date."
    lock_info[contract, user]["unlock_date"] = extended_date
    lock_info[contract, user] = lock_info[contract, user]
    return lock_info[contract, user]


@export
def burn(contract: str):
    '''burn all tokens at a go'''
    user = ctx.caller
    token_amount = locked_tokens[contract, user]
    assert token_amount > 0, "no tokens to burn."
    lock_data = lock_info[contract, user]
    token = I.import_module(contract)
    token.transfer(amount=token_amount, to="burn")
    locked_tokens[contract, user] = 0
    lock_info[contract, user]["amount"] = 0
    lock_info[contract, user] = lock_info[contract, user]
    return lock_info[contract, user]


@export
def withdraw(contract: str):
    '''withdraw all tokens at a go'''
    user = ctx.caller
    token_amount = locked_tokens[contract, user]
    assert token_amount > 0, "no locked tokens to withdraw."
    lock_data = lock_info[contract, user]
    assert now >= lock_data["unlock_date"], "cannot withdraw before unlock date."
    token = I.import_module(contract)
    token.transfer(amount=token_amount, to=user)
    locked_tokens[contract, user] = 0
    lock_info[contract, user]["amount"] = 0
    lock_info[contract, user] = lock_info[contract, user]
    return lock_info[contract, user]


@export
def withdraw_part(contract: str, amount: float):
    '''withdraw part of locked tokens'''
    assert amount > 0, "negative value not allowed!"
    user = ctx.caller
    token_amount = locked_tokens[contract, user]
    assert token_amount > 0, "no locked tokens to withdraw"
    lock_data = lock_info[contract, user]
    assert now >= lock_data["unlock_date"], "cannot withdraw before unlock date."
    assert token_amount > amount, f"you have {token_amount} but trying to withdraw {amount}"
    token = I.import_module(contract)
    token.transfer(amount=amount ,to=user)
    locked_tokens[contract, user] -= amount
    lock_info[contract, user]["amount"] -= amount
    lock_info[contract, user] = lock_info[contract, user]
    return lock_info[contract, user]
