import con_rocketswap_official_v1_1
DEX = con_rocketswap_official_v1_1
lock_info = Hash()
lp_points = Hash(default_value=0)


@export
def lock_lp(contract: str, amount: float, date: dict = None):
    assert amount > 0, "negative value not allowed!"
    user = ctx.caller
    if lp_points[contract, user] > 0:
        DEX.transfer_liquidity_from(
            contract=contract, to=ctx.this, main_account=user, amount=amount)
        lock_info[contract, user]["amount"] =+ amount
        lock_info[contract, user] = lock_info[contract, user]
        return lock_info[contract, user]
    else:
        assert date, "set a lock date!"
        unlock_date = datetime.datetime(
            year=date["year"], month=date["month"], day=date["day"], hour=date["hour"], minute=date["minute"])
        assert unlock_date > now, "unlock_date must be set ahead from now!"
        DEX.transfer_liquidity_from(
            contract=contract, to=ctx.this, main_account=user, amount=amount)
        lp_points[contract, user] += amount
        lock_info[contract, user] = {
            "lock_date": now,
            "amount": lp_points[contract, user],
            "unlock_date": unlock_date,
        }
        return lock_info[contract, user]


@export
def extend_lock(contract: str, year: int, month: int, day: int, hour: int = 0, minute: int = 0):
    '''extend locking period whilst your LPs remain ontouched'''
    user = ctx.caller
    assert lp_points[contract, user] > 0, "no locked LPs found."
    lock_data = lock_info[contract, user]
    unlock_date = lock_data["unlock_date"]
    extended_date = datetime.datetime(
        year=year, month=month, day=day, hour=hour, minute=minute)
    assert extended_date > unlock_date, "extended date cannot be earlier or previous unlock date."
    lock_info[contract, user]["unlock_date"] = extended_date
    lock_info[contract, user] = lock_info[contract, user]
    return lock_info[contract, user]


@export
def burn_lp(contract: str):
    '''burn all LPs at a go'''
    user = ctx.caller
    lp_amount = lp_points[contract, user]
    assert lp_amount > 0, "no LPs to burn."
    lock_data = lock_info[contract, user]
    DEX.transfer_liquidity(contract=contract, to="burn", amount=lp_amount)
    lp_points[contract, user] = 0
    lock_info[contract, user]["amount"] -= lp
    lock_info[contract, user] = lock_info[contract, user]
    return lock_info[contract, user]


@export
def withdraw(contract: str):
    '''withdraw all LPs at a go'''
    user = ctx.caller
    lp_amount = lp_points[contract, user]
    assert lp_amount > 0, "no LPs to withdraw."
    lock_data = lock_info[contract, user]
    assert now >= lock_data["unlock_date"], "cannot withdraw before unlock date."
    DEX.transfer_liquidity(contract=contract, to=user, amount=lp_amount)
    lp_points[contract, user] = 0
    lock_info[contract, user]["amount"] -= lp_amount
    lock_info[contract, user] = lock_info[contract, user]
    return lock_info[contract, user]


@export
def withdraw_part(contract: str, amount: float):
    '''withdraw part of locked LPs'''
    assert amount > 0, "negative value not allowed!"
    user = ctx.caller
    lp_amount = lp_points[contract, user]
    assert lp_amount > 0, "no LPs to withdraw"
    lock_data = lock_info[contract, user]
    assert now >= lock_data["unlock_date"], "cannot withdraw before unlock date."
    DEX.transfer_liquidity(contract=contract, to=user, amount=amount)
    lp_points[contract, user] -= amount
    lock_info[contract, user]["amount"] -= amount
    lock_info[contract, user] = lock_info[contract, user]
    return lock_info[contract, user]
