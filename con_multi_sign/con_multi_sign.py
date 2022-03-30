I = importlib

token_interface = [
    I.Func('transfer', args=('amount', 'to')),
    I.Func('approve', args=('amount', 'to')),
    I.Func('transfer_from', args=('amount', 'to', 'main_account'))
]

owners = Variable()
required = Variable()
transactions = Hash()
transactionCount = Variable()
confirmations = Hash(default_value=False)
ownerConfirmed = Hash(default_value=[])
dailyLimit = Variable()
lastDay = Variable()
spentToday = Variable()


@construct
def seed():
    owners.set(['sys', 'benjos', 'jeff', 'chris'])
    required.set(2)
    transactionCount.set(0)
    dailyLimit.set(1000)
    lastDay.set(datetime.datetime(year=2022, month=3, day=26))
    spentToday.set(0)




def validRequirements(ownerCount: int, req: int):
    assert req < ownerCount and req > 0 and ownerCount > 0, "invalid confirmation reqirements!"

@export
def addOwner(owner: str):
    user = ctx.caller
    ownerList = owners.get()
    assert user in ownerList, "only owner can call this method!"
    assert owner not in ownerList, "owner already exist!"
    validRequirements(len(ownerList) + 1, required.get())
    ownerList.append(owner)
    owners.set(ownerList)

@export
def removeOwner(owner: str):
    user = ctx.caller
    ownerList = owners.get()
    assert user in ownerList, "only owner can call this method!"
    assert owner in ownerList, "owner does not exist!"
    validRequirements(len(ownerList) - 1 , required.get())
    ownerList.remove(owner)
    owners.set(ownerList)

@export
def replaceOwner(owner: str, newOwner: str):
    user = ctx.caller
    ownerList = owners.get()
    assert user in ownerList, "only owner can call this method!"
    assert owner in ownerList, "owner does not exist!"
    assert newOwner not in ownerList, "newOwner already exist!"
    ownerList.remove(owner)
    ownerList.append(newOwner)
    owners.set(ownerList)

@export
def submitTransaction(contract: str, amount: float, to: str):
    assert amount > 0, "cannot enter negative value!"
    user = ctx.caller
    ownerList = owners.get()
    token = I.import_module(contract)
    assert user in ownerList, "only owner can call this method!"
    assert I.enforce_interface(token, token_interface), 'invalid token interface!'
    transactionCount.set(transactionCount.get() + 1)
    transactionId = transactionCount.get()
    transactions[transactionId] = {
        'contract': contract,
        'amount': amount,
        'to': to,
        'executed': False
    }
    confirmTransaction(transactionId = transactionId)

@export
def confirmTransaction(transactionId: int):
    user = ctx.caller
    ownerList = owners.get()
    transaction = transactions[transactionId]
    assert user in ownerList, "only owner can call this method!"
    assert transaction, "transaction does not exist!"
    assert transaction['executed'] is False, "txn already executed!"
    assert confirmations[transactionId, user] is False, "transaction is already confirmed by you!"
    confirmations[transactionId, user] = True
    ownerConfirmed[transactionId] += [user]
    executeTransaction(transactionId = transactionId)

@export
def revokeTransaction(transactionId: int):
    user = ctx.caller
    ownerList = owners.get()
    transaction = transactions[transactionId]
    assert user in ownerList, "only owner can call this method!"
    assert transaction, "transaction does not exist!"
    assert transaction['executed'] is False, "txn already executed!"
    assert confirmations[transactionId, user] is True, "transaction is not confirmed by you!"
    confirmations[transactionId, user] = False
    ownerConfirmed[transactionId].remove(user)

def isConfirmed(transactionId: int):
    if len(ownerConfirmed[transactionId]) == required.get():
        return True

def isUnderLimit(amount: int):
    assert amount > 0, "cannot enter negative value!"
    if now > lastDay.get() + datetime.timedelta(days=1):
            lastDay.set(now)
            spentToday.set(0)
    if spentToday.get() + amount > dailyLimit.get():
        return False
    return True

@export
def executeTransaction(transactionId: int):
    user = ctx.caller
    ownerList = owners.get()
    txn = transactions[transactionId]
    assert user in ownerList, "only owner can call this method!"
    assert txn['executed'] is False, "txn already executed!"
    if isConfirmed(transactionId = transactionId) and isUnderLimit(txn['amount']):
        token = I.import_module(txn['contract'])
        token.transfer(amount = txn['amount'], to = txn['to'])
        spentToday.set(spentToday.get() + txn['amount'])
        transactions[transactionId]['executed'] = True
        return True
    else: 
        return False

#don't see much usefullness of this method if there's a small number of confirmations required.
#a web call and counting the owner list would suffice.
@export
def getConfirmationCount(transactionId: int):
    return len(ownerConfirmed[transactionId])

@export
def getTransactionCount(pending: bool, executed: bool):
    count = 0
    for i in range(1, transactionCount.get() + 1):
        if pending and not transactions[i]['executed'] or executed and transactions[i]['executed']:
            count += 1
    return count

@export
def changeRequirement(req: int):
    user = ctx.caller
    ownerList = owners.get()
    assert user in ownerList, "only owner can call this method!"
    validRequirements(len(ownerList) , req)
    required.set(req)

@export
def changeDailyLimit(dailylimit : float):
    user = ctx.caller
    ownerList = owners.get()
    assert user in ownerList, "only owner can call this method!"
    dailyLimit.set(dailylimit)
    

