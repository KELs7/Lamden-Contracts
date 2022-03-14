balances = Hash(default_value=0)

@construct
def seed(vk: str):
    balances[vk] = 1000000
    #balances['test'] = 1000000

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller

    assert balances[sender] >= amount, 'Not enough CURRENCY to send!'

    balances[sender] -= amount
    balances[to] += amount

@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller
    balances[sender, to] += amount
    return balances[sender, to]

@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller

    assert balances[main_account, sender] >= amount, '{} Not enough coins approved to send! You have {} and are trying to spend {}'\
        .format(balances[main_account], balances[main_account, sender], amount)
    assert balances[main_account] >= amount, f'Not enough coins to send! {balances[main_account]}'

    balances[main_account, sender] -= amount
    balances[main_account] -= amount

    balances[to] += amount
