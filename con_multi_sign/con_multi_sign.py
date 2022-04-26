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

#action interface
action_interface = [
    I.Func('interact', args=('payload', 'state', 'caller')),
]

owners = Variable()
required = Variable()
transactions = Hash()
transaction_count = Variable()
confirmations = Hash(default_value=False)
owner_confirmed = Hash(default_value=[])
metadata = Hash()
daily_limit = Variable()
last_day = Variable()
spent_today = Variable()
actions = Hash()
S = Hash()


@construct
def seed():
    owners.set(['sys', 'benjos', 'jeff', 'chris'])
    required.set(2)
    transaction_count.set(0)
    daily_limit.set(1000)
    last_day.set(datetime.datetime(year=2022, month=3, day=26))
    spent_today.set(0)


def valid_requirements(owner_count: int, req: int):
    assert req < owner_count and req > 0 and owner_count > 0, "invalid confirmation reqirements!"

@export
def change_metadata(key: str, value: Any):
    user = ctx.caller
    owner_list = owners.get()
    assert user in owner_list, "only owner can call this method!"
    assert value > 0, "cannot enter negative value!"
    
    keys = ["req", "dailylimit"]
    if key in keys:
        v = []
        if key == keys[0]:
            if isinstance(value, int):
                metadata[key, user] = value
                for owner in owner_list:
                    if metadata[key, user] == metadata[key, owner]:
                        v.append(value)
                if len(v) == required.get():
                    valid_requirements(len(owner_list) , value)
                    required.set(value)
                    for owner in owner_list:
                        if metadata[key, owner]:
                            metadata[key, owner] = hashlib.sha256(str(now))
                    return True

                else:    
                    return "there was no concensus to change required confirmations"
        
        if key == keys[1]:
            if isinstance(value, decimal):
                metadata[key, user] = value
                #get value
                for owner in owner_list:
                    if metadata[key, user] == metadata[key, owner]:
                        v.append(value)
                #check if a certain number of owners have ...same value
                if len(v) == required.get():
                    daily_limit.set(value)
                    for owner in owner_list:
                        if metadata[key, owner]:
                            metadata[key, owner] = hashlib.sha256(str(now))
                    return True
                else:    
                    return "there was no concensus to change dailylimit"
    else:
        return "key does not exist!"       

@export
def add_owner(new_owner: str):
    user = ctx.caller
    owner_list = owners.get()
    assert user in owner_list, "only owner can call this method!"
    assert new_owner not in owner_list, "owner already exist!"
    m = []
    metadata["add_owner", user] = new_owner
    for owner in owner_list:
        if metadata["add_owner", user] == metadata["add_owner", owner]:
            m.append(new_owner)
    if len(m) == required.get():
        valid_requirements(len(owner_list) + 1, required.get())
        for owner in owner_list:
            if metadata["add_owner", owner]:
                metadata["add_owner", owner] = hashlib.sha256(str(now))
        owner_list.append(new_owner)
        owners.set(owner_list)
        return True
    else:    
        return f"there was no concensus to add {new_owner}"

@export
def remove_owner(existing_owner: str):
    user = ctx.caller
    owner_list = owners.get()
    assert user in owner_list, "only owner can call this method!"
    assert existing_owner in owner_list, "owner does not exist!"
    m = []
    metadata["remove_owner", user] = existing_owner
    for owner in owner_list:
        if metadata["remove_owner", user] == metadata["remove_owner", owner]:
            m.append(existing_owner)
    if len(m) == required.get():
        valid_requirements(len(owner_list) - 1 , required.get())
        for owner in owner_list:
            if metadata["remove_owner", owner]:
                metadata["remove_owner", owner] = hashlib.sha256(str(now))
        owner_list.remove(existing_owner)
        owners.set(owner_list)
        return True
    else:    
        return f"there was no concensus to remove {existing_owner}" 

@export
def replace_owner(existing_owner: str, new_owner: str):
    user = ctx.caller
    owner_list = owners.get()
    assert user in owner_list, "only owner can call this method!"
    assert existing_owner in owner_list, "owner does not exist!"
    assert new_owner not in owner_list, "new_owner already part of owners!"
    m = []
    metadata["replace_owner", user] = new_owner
    for owner in owner_list:
        if metadata["replace_owner", user] == metadata["replace_owner", owner]:
            m.append(new_owner)
    if len(m) == required.get():
        valid_requirements(len(owner_list), required.get())
        for owner in owner_list:
            if metadata["replace_owner", owner]:
                metadata["replace_owner", owner] = hashlib.sha256(str(now))
        owner_list.remove(existing_owner)
        owner_list.append(new_owner)
        owners.set(owner_list)
        return True
    else:    
        return f"there was no concensus to replace {existing_owner} with {new_owner}"

@export
def submit_transaction(contract: str, amount: float, to: str, action_core: str, action: str, payload: dict):
    user = ctx.caller
    owner_list = owners.get()
    assert user in owner_list, "only owner can call this method!" 
    transaction_count.set(transaction_count.get() + 1)
    transaction_id = transaction_count.get()

    #support for external action transactions
    if action_core and action:
        assert payload, 'a payload was not provided!'
        action_core_contract = I.import_module(action_core)
        assert I.enforce_interface(action_core_contract, action_core_interface), 'invalid token interface!'
        transactions[transaction_id] = {
            'contract': action_core,
            'action': action,
            'payload': payload,
            'executed': False
        }
        confirm_transaction(transaction_id = transaction_id)
        return transactions[transaction_id]

    #support for LST001 transactions
    assert amount > 0, "cannot enter negative value!"
    token = I.import_module(contract)
    assert I.enforce_interface(token, LST001_interface), 'invalid token interface!'
    transactions[transaction_id] = {
         'contract': contract,
         'amount': amount,
         'to': to,
         'executed': False
    }
    confirm_transaction(transaction_id = transaction_id)
    return transactions[transaction_id]

@export
def confirm_transaction(transaction_id: int):
    user = ctx.caller
    owner_list = owners.get()
    transaction = transactions[transaction_id]
    assert user in owner_list, "only owner can call this method!"
    assert transaction, "transaction does not exist!"
    assert transaction['executed'] is False, "txn already executed!"
    assert confirmations[transaction_id, user] is False, "transaction is already confirmed by you!"
    confirmations[transaction_id, user] = True
    owner_confirmed[transaction_id] += [user]
    execute_transaction(transaction_id = transaction_id)

@export
def revoke_transaction(transaction_id: int):
    user = ctx.caller
    owner_list = owners.get()
    transaction = transactions[transaction_id]
    assert user in owner_list, "only owner can call this method!"
    assert transaction, "transaction does not exist!"
    assert transaction['executed'] is False, "txn already executed!"
    assert confirmations[transaction_id, user] is True, "transaction is not confirmed by you!"
    confirmations[transaction_id, user] = False
    owner_confirmed[transaction_id].remove(user)

def is_confirmed(transaction_id: int):
    if len(owner_confirmed[transaction_id]) == required.get():
        return True

def is_under_limit(amount: float):
    assert amount > 0, "cannot enter negative value!"
    if now > last_day.get() + datetime.timedelta(days=1):
            last_day.set(now)
            spent_today.set(0)
    if spent_today.get() + amount > daily_limit.get():
        return False
    return True

@export
def execute_transaction(transaction_id: int):
    user = ctx.caller
    owner_list = owners.get()
    txn = transactions[transaction_id]
    assert user in owner_list, "only owner can call this method!"
    assert txn['executed'] is False, "txn already executed!"
    contract = I.import_module(txn['contract'])

    if I.enforce_interface(contract, action_core_interface):
        #in case action contract is a monetary asset, control spend limit
        if txn['payload']['amount']:
            if is_confirmed(transaction_id = transaction_id) and is_under_limit(txn['payload']['amount']): 
                contract.interact(action=txn['action'], payload=txn['payload'])
                spent_today.set(spent_today.get() + txn['payload']['amount'])
                transactions[transaction_id]['executed'] = True
                return True
            else: 
                return False
        contract.interact(action=txn['action'], payload=txn['payload'])
        transactions[transaction_id]['executed'] = True
        return True
    
    if is_confirmed(transaction_id = transaction_id) and is_under_limit(txn['amount']):
        contract.transfer(amount = txn['amount'], to = txn['to'])
        spent_today.set(spent_today.get() + txn['amount'])
        transactions[transaction_id]['executed'] = True
        return True
    else: 
        return False


#don't see much usefullness of this method if there's a small number of confirmations required.
#a web call and counting the owner list would suffice.
@export
def get_confirmation_count(transaction_id: int):
    return len(owner_confirmed[transaction_id])

@export
def get_transaction_count(pending: bool, executed: bool):
    count = 0
    for i in range(1, transaction_count.get() + 1):
        if pending and not transactions[i]['executed'] or executed and transactions[i]['executed']:
            count += 1
    return count

# action core 
@export
def register_action(action: str, contract: str):
    user = ctx.caller
    owner_list = owners.get()
    assert user in owner_list, "only owner can call this method!"
    assert actions[action] is None, 'Action already registered!'

    a = []
    metadata["register_action", user] = action
    for owner in owner_list:
        if metadata["register_action", user] == metadata["register_action", owner]:
            a.append(action)
    if len(a) == required.get():
        for owner in owner_list:
            if metadata["register_action", owner]:
                metadata["register_action", owner] = hashlib.sha256(str(now))


        # Attempt to import the contract to make sure it is already submitted
        p = I.import_module(contract)

        # Assert ownership is election_house and interface is correct
        assert I.owner_of(p) == ctx.this, \
            'This contract must control the action contract!'

        assert I.enforce_interface(p, action_interface), \
            'Action contract does not follow the correct interface!'

        actions[action] = contract


        return True
    else:    
        return f"there was no concensus to register {action}"

@export
def unregister_action(action: str):
    user = ctx.caller
    owner_list = owners.get()
    assert user in owner_list, "only owner can call this method!"
    assert actions[action] is not None, 'Action does not exist!'

    a = []
    metadata["unregister_action", user] = action
    for owner in owner_list:
        if metadata["unregister_action", user] == metadata["unregister_action", owner]:
            a.append(action)
    if len(a) == required.get():
        for owner in owner_list:
            if metadata["unregister_action", owner]:
                metadata["unregister_action", owner] = hashlib.sha256(str(now))

        actions[action] = None

        return True
    else:    
        return f"there was no concensus to unregister {action}"

@export
def interact(action: str, payload: dict):
    contract = actions[action]
    user = ctx.caller
    owner_list = owners.get()
    assert user in owner_list, "only owner can call this method!"
    assert contract is not None, 'Invalid action!'

    a = []
    metadata["interact", user] = {'action':action, 'payload':payload}
    for owner in owner_list:
        if metadata["interact", user] == metadata["interact", owner]:
            a.append({'action':action, 'payload':payload})
    if len(a) == required.get():
        for owner in owner_list:
            if metadata["interact", owner]:
                metadata["interact", owner] = hashlib.sha256(str(now))

        module = I.import_module(contract)

        result = module.interact(payload, S, user)
        return result
    else:
        return False

@export
def bulk_interact(action: str, payloads: list):
    user = ctx.caller
    owner_list = owners.get()
    assert user in owner_list, "only owner can call this method!"

    b = []
    metadata["bulk_interact", user] = {'action':action, 'payload':payloads}
    for owner in owner_list:
        if metadata["bulk_interact", user] == metadata["bulk_interact", owner]:
            b.append({'action':action, 'payload':payloads})
    if len(a) == required.get():
        for owner in owner_list:
            if metadata["bulk_interact", owner]:
                metadata["bulk_interact", owner] = hashlib.sha256(str(now))

        for payload in payloads:
            interact(action, payload)

        return True
    else:
        return False
    

