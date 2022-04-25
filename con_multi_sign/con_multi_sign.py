I = importlib

#LST001 contract interface
LST001_interface = [
    I.Func('transfer', args=('amount', 'to')),
    I.Func('approve', args=('amount', 'to')),
    I.Func('transfer_from', args=('amount', 'to', 'main_account'))
]

#action contract interface
action_core_interface = [
    I.Func('interact', args=('action', 'payload'))
]

owners = Variable()
required = Variable()
transactions = Hash()
transactionCount = Variable()
confirmations = Hash(default_value=False)
ownerConfirmed = Hash(default_value=[])
metadata = Hash()
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
def change_metadata(key: str, value: Any):
    user = ctx.caller
    ownerList = owners.get()
    assert user in ownerList, "only owner can call this method!"
    assert value > 0, "cannot enter negative value!"
    
    keys = ["req", "dailylimit"]
    if key in keys:
        v = []
        if key == keys[0]:
            if isinstance(value, int):
                metadata[key, user] = value
                for owner in ownerList:
                    if metadata[key, user] == metadata[key, owner]:
                        v.append(value)
                if len(v) == required.get():
                    validRequirements(len(ownerList) , value)
                    required.set(value)
                    for owner in ownerList:
                        metadata[key, user] = hashlib.sha256(str(now))
                    return True

                else:    
                    return "there was no concensus to change required confirmations"
        
        if key == keys[1]:
            if isinstance(value, decimal):
                metadata[key, user] = value
                #get value
                for owner in ownerList:
                    if metadata[key, user] == metadata[key, owner]:
                        v.append(value)
                #check if a certain number of owners have ...same value
                if len(v) == required.get():
                    dailyLimit.set(value)
                    for owner in ownerList:
                        metadata[key, user] = hashlib.sha256(str(now))
                    return True
                else:    
                    return "there was no concensus to change dailylimit"
    else:
        return "key does not exist!"       

@export
def addOwner(newOwner: str):
    user = ctx.caller
    ownerList = owners.get()
    assert user in ownerList, "only owner can call this method!"
    assert newOwner not in ownerList, "owner already exist!"
    m = []
    metadata["addOwner", user] = newOwner
    for owner in ownerList:
        if metadata["addOwner", user] == metadata["addOwner", owner]:
            m.append(newOwner)
    if len(m) == required.get():
        validRequirements(len(ownerList) + 1, required.get())
        for owner in ownerList:
            metadata["addOwner", user] = hashlib.sha256(str(now))
        ownerList.append(newOwner)
        owners.set(ownerList)
        return True
    else:    
        return f"there was no concensus to add {newOwner}"

@export
def removeOwner(existingOwner: str):
    user = ctx.caller
    ownerList = owners.get()
    assert user in ownerList, "only owner can call this method!"
    assert existingOwner in ownerList, "owner does not exist!"
    m = []
    metadata["removeOwner", user] = existingOwner
    for owner in ownerList:
        if metadata["removeOwner", user] == metadata["removeOwner", owner]:
            m.append(existingOwner)
    if len(m) == required.get():
        validRequirements(len(ownerList) - 1 , required.get())
        for owner in ownerList:
            metadata["removeOwner", user] = hashlib.sha256(str(now))
        ownerList.remove(existingOwner)
        owners.set(ownerList)
        return True
    else:    
        return f"there was no concensus to remove {existingOwner}" 

@export
def replaceOwner(existingOwner: str, newOwner: str):
    user = ctx.caller
    ownerList = owners.get()
    assert user in ownerList, "only owner can call this method!"
    assert existingOwner in ownerList, "owner does not exist!"
    assert newOwner not in ownerList, "newOwner already part of owners!"
    m = []
    metadata["replaceOwner", user] = newOwner
    for owner in ownerList:
        if metadata["replaceOwner", user] == metadata["replaceOwner", owner]:
            m.append(newOwner)
    if len(m) == required.get():
        validRequirements(len(ownerList), required.get())
        for owner in ownerList:
            metadata["replaceOwner", user] = hashlib.sha256(str(now))
        ownerList.remove(existingOwner)
        ownerList.append(newOwner)
        owners.set(ownerList)
        return True
    else:    
        return f"there was no concensus to replace {existingOwner} with {newOwner}"

@export
def submitTransaction(contract: str, amount: float, to: str, action_core: str, action: str, method: str):
    assert amount > 0, "cannot enter negative value!"
    user = ctx.caller
    ownerList = owners.get()

    assert user in ownerList, "only owner can call this method!" 
    transactionCount.set(transactionCount.get() + 1)
    transactionId = transactionCount.get()

    if action_core and action:
        action_core_contract = I.import_module(action_core)
        assert I.enforce_interface(action_core_contract, action_core_interface), 'invalid token interface!'
        transactions[transactionId] = {
            'contract': action_core,
            'action': action,
            'function': method,
            'amount': amount,
            'to': to,
            'executed': False
        }
        confirmTransaction(transactionId = transactionId)
        return

    token = I.import_module(contract)
    assert I.enforce_interface(token, LST001_interface), 'invalid token interface!'
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

def isUnderLimit(amount: float):
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
    contract = I.import_module(txn['contract'])

    if I.enforce_interface(contract, action_core_interface):
        if isConfirmed(transactionId = transactionId) and isUnderLimit(txn['amount']): 
            contract.interact(action=txn['action'], payload={
                'function': txn['function'],
                'amount': txn['amount'],
                'to': txn['to']
            })
            spentToday.set(spentToday.get() + txn['amount'])
            transactions[transactionId]['executed'] = True
            return True
        else: 
            return False

    if isConfirmed(transactionId = transactionId) and isUnderLimit(txn['amount']):
        contract.transfer(amount = txn['amount'], to = txn['to'])
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
    

