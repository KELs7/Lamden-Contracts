I = importlib

# LST001 contract interface
LST001_interface = [
    I.Func('transfer', args=('amount', 'to')),
    I.Func('approve', args=('amount', 'to')),
    I.Func('transfer_from', args=('amount', 'to', 'main_account'))
]

# action contract interface
action_core_interface = [
    I.Func('interact', args=('action', 'payload'))
]

# action interface
action_interface = [
    I.Func('interact', args=('payload', 'state', 'caller')),
]

owners = Variable()
required = Variable()
proposal = Hash()
proposal_count = Variable()
confirmations = Hash(default_value=False)
owner_confirmed = Hash(default_value=[])
metadata = Hash()
daily_limit = Hash(default_value=0)
last_day = Variable()
spent_today = Variable()
actions = Hash()
S = Hash()


@construct
def seed():
    owners.set(['sys', 'benjos', 'jeff', 'chris'])
    required.set(2)
    proposal_count.set(0)
    daily_limit['currency'] = decimal('1000')
    last_day.set(datetime.datetime(year=2022, month=3, day=26))
    spent_today.set(0)
    #initial action
    actions['sToken']  = 'action_token'


def valid_requirements(owner_count: int, req: int):
    assert req < owner_count and req > 0 and owner_count > 0, 'invalid confirmation reqirements!'

# @export
# def change_metadata(key: str, value: Any):
#     user = ctx.caller
#     owner_list = owners.get()
#     assert user in owner_list, 'only owner can call this method!'
#     assert value > 0, 'cannot enter negative value!'

#     keys = ['req', 'dailylimit']
#     if key in keys:
#         v = []
#         if key == keys[0]:
#             if isinstance(value, int):
#                 metadata[key, user] = value
#                 for owner in owner_list:
#                     if metadata[key, user] == metadata[key, owner]:
#                         v.append(value)
#                 if len(v) == required.get():
#                     valid_requirements(len(owner_list) , value)
#                     required.set(value)
#                     for owner in owner_list:
#                         if metadata[key, owner]:
#                             metadata[key, owner] = hashlib.sha256(str(now))
#                     return True

#                 else:
#                     return 'there was no concensus to change required confirmations'

#         if key == keys[1]:
#             if isinstance(value, decimal):
#                 metadata[key, user] = value
#                 #get value
#                 for owner in owner_list:
#                     if metadata[key, user] == metadata[key, owner]:
#                         v.append(value)
#                 #check if a certain number of owners have ...same value
#                 if len(v) == required.get():
#                     daily_limit.set(value)
#                     for owner in owner_list:
#                         if metadata[key, owner]:
#                             metadata[key, owner] = hashlib.sha256(str(now))
#                     return True
#                 else:
#                     return 'there was no concensus to change dailylimit'
#     else:
#         return 'key does not exist!'


def add_owner(proposal_id: str):
    new_owner = proposal[proposal_id]['add_owner']
    owner_list = owners.get()
    assert new_owner not in owner_list, 'owner already exist!'

    if is_confirmed(proposal_id=proposal_id):
        valid_requirements(len(owner_list) + 1, required.get())
        owner_list.append(new_owner)
        owners.set(owner_list)
        return True
    else:
        return f'there was no concensus to add {new_owner}'


def remove_owner(proposal_id: str):
    existing_owner = proposal[proposal_id]['remove_owner']
    owner_list = owners.get()
    assert existing_owner in owner_list, 'owner does not exist!'

    if is_confirmed(proposal_id=proposal_id):
        valid_requirements(len(owner_list) - 1, required.get())
        owner_list.remove(existing_owner)
        owners.set(owner_list)
        return True
    else:
        return f'there was no concensus to remove {existing_owner}'


def replace_owner(proposal_id: str):
    new_owner = proposal[proposal_id]['replace_owner']['new_owner']
    existing_owner = proposal[proposal_id]['replace_owner']['existing_owner']
    owner_list = owners.get()
    assert existing_owner in owner_list, 'owner does not exist!'
    assert new_owner not in owner_list, 'new_owner already part of owners!'

    if is_confirmed(proposal_id=proposal_id):
        valid_requirements(len(owner_list), required.get())
        owner_list.remove(existing_owner)
        owner_list.append(new_owner)
        owners.set(owner_list)
        return True
    else:
        return f'there was no concensus to replace {existing_owner} with {new_owner}'


@export
def submit_proposal(propsl: dict):
    user = ctx.caller
    owner_list = owners.get()
    assert user in owner_list, 'only owner can call this method!'
    proposal_count.set(proposal_count.get() + 1)
    proposal_id = proposal_count.get()

    proposal_dict = route_proposal(propsl)

    # return proposal_dict

    # support for state changes proposal
    if proposal_dict['type'] == 'state_update':
        # checks, should there be strict length checking?
        keys = list(proposal_dict.keys())
        if 'add_owner' in keys:
            assert isinstance(
                proposal_dict['add_owner'], str), 'entry must be string!'
        if 'remove_owner' in keys:
            assert isinstance(
                proposal_dict['remove_owner'], str), 'entry must be string!'
        if 'replace_owner' in keys:
            assert isinstance(
                proposal_dict['replace_owner']['new_owner'], str), 'entry must be string!'
            assert isinstance(
                proposal_dict['replace_owner']['existing_owner'], str), 'entry must be string!'
        if 'register_action' in keys:
            assert isinstance(
                proposal_dict['register_action']['action'], str), 'entry must be string!'
            assert isinstance(
                proposal_dict['register_action']['contract'], str), 'entry must be string!'
        if 'unregister_action' in keys:
            assert isinstance(
                proposal_dict['unregister_action'], str), 'entry must be string!'
        if 'change_requirement' in keys:
            assert isinstance(
                proposal_dict['change_requirement'], int), 'entry must be int!'
        if 'change_dailylimit' in keys:
            d_keys = list(proposal_dict['change_dailylimit'].keys())
            # float or ContractingDecimal?
            if 'token' in d_keys:
                assert isinstance(
                    proposal_dict['change_dailylimit']['token'], str), 'entry must be string!'
                assert isinstance(
                    proposal_dict['change_dailylimit']['amount'], decimal), 'entry must be decimal!'
            if 'action' in d_keys:
                assert isinstance(
                    proposal_dict['change_dailylimit']['action'], str), 'entry must be string!'
                assert isinstance(
                    proposal_dict['change_dailylimit']['amount'], decimal), 'entry must be decimal!'
            if 'external_action' in d_keys:
                assert isinstance(
                    proposal_dict['change_dailylimit']['external_action'], str), 'entry must be string!'
                assert isinstance(
                    proposal_dict['change_dailylimit']['amount'], decimal), 'entry must be decimal!'
        proposal[proposal_id] = proposal_dict
        return confirm_proposal(proposal_id=proposal_id)
        # return proposal[proposal_id]

    # support for LST001 proposal
    # if proposal_dict['type'] == 'lst001_txn':
    #     assert proposal_dict['payload']['amount'] > 0, 'cannot enter negative value!'
    #     token = I.import_module(proposal_dict[['token'])
    #     assert I.enforce_interface(token, LST001_interface), 'invalid token interface!'
    #     proposal[proposal_id] = proposal_dict
    #     confirm_proposal(proposal_id = proposal_id)
    #     return proposal[proposal_id]

    # support for action proposal
    # if proposal_dict['type'] == 'action_txn':
    #     if proposal_dict['payload']['amount']:
    #         assert proposal_dict['payload']['amount'] > 0, 'cannot enter negative value!'
    #     proposal[proposal_id] = proposal_dict
    #     confirm_proposal(proposal_id = proposal_id)
    #     return proposal[proposal_id]

    # support for external action proposal
    # if proposal_dict['type'] == 'external_action_txn':
    #     if proposal_dict['payload']['amount']:
    #         assert proposal_dict['payload']['amount'] > 0, 'cannot enter negative value!'
    #     action_core_contract = I.import_module(proposal_dict['action_core'])
    #     assert I.enforce_interface(action_core_contract, action_core_interface), 'invalid token interface!'
    #     proposal[proposal_id] = proposal_dict
    #     confirm_proposal(proposal_id = proposal_id)
    #     return proposal[proposal_id]


@export
def confirm_proposal(proposal_id: int):
    user = ctx.caller
    owner_list = owners.get()
    propsl = proposal[proposal_id]
    assert user in owner_list, 'only owner can call this method!'
    assert propsl, 'proposal does not exist!'
    assert propsl['executed'] is False, 'proposal already executed!'
    assert confirmations[proposal_id,
        user] is False, 'proposal is already confirmed by you!'
    confirmations[proposal_id, user] = True
    owner_confirmed[proposal_id] += [user]
    # REMOVE RETURN JUST FOR DEBUGGING PURPOSES
    return execute_proposal(proposal_id=proposal_id)


@export
def revoke_proposal(proposal_id: int):
    user = ctx.caller
    owner_list = owners.get()
    proposal = proposal[proposal_id]
    assert user in owner_list, 'only owner can call this method!'
    assert proposal, 'proposal does not exist!'
    assert proposal['executed'] is False, 'proposal already executed!'
    assert confirmations[proposal_id,
        user] is True, 'proposal is not confirmed by you!'
    confirmations[proposal_id, user] = False
    owner_confirmed[proposal_id].remove(user)


def is_confirmed(proposal_id: int):
    if len(owner_confirmed[proposal_id]) == required.get():
        return True


def is_under_limit(amount: float):
    assert amount > 0, 'cannot enter negative value!'
    if now > last_day.get() + datetime.timedelta(days=1):
            last_day.set(now)
            spent_today.set(0)
    if spent_today.get() + amount > daily_limit.get():
        return False
    return True


@export
def execute_proposal(proposal_id: int):
    user = ctx.caller
    owner_list = owners.get()
    propsl = proposal[proposal_id]
    assert user in owner_list, 'only owner can call this method!'
    assert propsl['executed'] is False, 'proposal already executed!'

    if propsl['type'] == 'state_update':
        keys = list(propsl.keys())
        if 'add_owner' in keys:
            return add_owner(proposal_id=proposal_id)
        if 'remove_owner' in keys:
            return remove_owner(proposal_id=proposal_id)
        if 'replace_owner' in keys:
            return replace_owner(proposal_id=proposal_id)
        if 'register_action' in keys:
            return register_action(proposal_id=proposal_id)
        if 'unregister_action' in keys:
            return unregister_action(proposal_id=proposal_id)
        if 'change_requirement' in keys:
            return change_requirement(proposal_id=proposal_id)
        if 'change_dailylimit' in keys:
            return change_dailylimit(proposal_id=proposal_id)
        return 'invalid key!'

    # if proposal['type'] == 'lst001_proposal':
    #     if is_confirmed(proposal_id = proposal_id) and is_under_limit(proposal['amount']):
    #         if proposal_dict['payload']['transfer']:
    #             contract.transfer(amount = proposal['amount'], to = proposal['to'])
    #             spent_today.set(spent_today.get() + proposal['amount'])
    #             proposal[proposal_id]['executed'] = True
    #             return True
    #         else:
    #             return False

    #         if proposal['payload']['transfer_approve']:
    #             contract.approve(amount = proposal['amount'], to = proposal['to'])
    #             #spent_today.set(spent_today.get() + proposal['amount'])
    #             proposal[proposal_id]['executed'] = True
    #             return True
    #         else:
    #             return False

    #         if proposal['payload']['transfer_from']:
    #             contract.transfer(amount=proposal['amount'], to=proposal['to'], main_account=proposal['main_account'])
    #             #spent_today.set(spent_today.get() + proposal['amount'])
    #             proposal[proposal_id]['executed'] = True
    #             return True
    #         else:
    #             return False

    # if proposal['type'] == 'action_proposal':
    #     if proposal['payload']['amount']:
    #         if is_confirmed(proposal_id = proposal_id) or is_under_limit(proposal['payload']['amount']):
    #             interact(action=proposal['action'], payload=proposal['payload'])
    #             spent_today.set(spent_today.get() + proposal['payload']['amount'])
    #             proposal[proposal_id]['executed'] = True
    #             return True
    #         else:
    #             return False
    #     interact(action=proposal['action'], payload=proposal['payload']) #what to do with return?
    #     proposal[proposal_id]['executed'] = True
    #     return True

    # if proposal['type'] == 'external_action_proposal':
    #     action_core = I.import_module(proposal['action_core'])
    #     #in case action contract is a monetary asset, control spend limit
    #     if proposal['payload']['amount']:
    #         if is_confirmed(proposal_id = proposal_id) and is_under_limit(proposal['payload']['amount']):
    #             action_core.interact(action=proposal['action'], payload=proposal['payload'])
    #             spent_today.set(spent_today.get() + proposal['payload']['amount'])
    #             proposal[proposal_id]['executed'] = True
    #             return True
    #         else:
    #             return False
    #     action_core.interact(action=proposal['action'], payload=proposal['payload'])
    #     proposal[proposal_id]['executed'] = True
    #     return True

# don't see much usefullness of this method if there's a small number of confirmations required.
# a web call and counting the owner list would suffice.


@export
def get_confirmation_count(proposal_id: int):
    return len(owner_confirmed[proposal_id])


@export
def get_transaction_count(pending: bool, executed: bool):
    count = 0
    for i in range(1, proposal_count.get() + 1):
        if pending and not proposal[i]['executed'] or executed and proposal[i]['executed']:
            count += 1
    return count


def route_proposal(proposal_dict: dict):  # find a better name for parameter
    # use a better error description
    assert proposal_dict, 'proposal is empty or invalid!'

    keys = list(proposal_dict.keys())
    # return keys

    # Metadata state changes
    state_changes = [
        'add_owner',
        'remove_owner',
        'replace_owner',
        'register_action',
        'unregister_action',
        'change_requirement',
        'change_dailylimit',
    ]

    # LST001 token proposal
    lst001_transactions = ['token', 'payload']

    # Action proposal
    action_transaction = ['action', 'payload']
    external_action_transactions = ['action_core', 'action', 'payload']

    if len(keys) == 1:
        if keys[0] in state_changes:
            if keys[0] == 'change_dailylimit':
                # will check if relevent
                assert proposal_dict['change_dailylimit'], 'a payload was not provided!'
            proposal_dict['type'] = 'state_update'
            proposal_dict['executed'] = False
            return proposal_dict
        else:
            return 'invalid key!'

#     if keys == lst001_transaction:
#         assert proposal_dict['payload'], 'a payload was not provided!'
#         proposal_dict['type'] = 'lst001_proposal'
#         proposal_dict['executed'] = False
#         return proposal_dict

#     if keys == action_transaction:
#         assert proposal_dict['payload'], 'a payload was not provided!'
#         proposal_dict['type'] = 'action_proposal'
#         proposal_dict['executed'] = False
#         return proposal_dict

#     if keys == external_action_transaction:
#         assert proposal_dict['payload'], 'a payload was not provided!'
#         proposal_dict['type'] = 'external_action_proposal'
#         proposal_dict['executed'] = False
#         return proposal_dict

#     return 'invalid key(s) entry' #check for better error wording

# # action core


def register_action(proposal_id: int):
    propsl = proposal[proposal_id]['register_action']
    action = propsl['action']
    contract = propsl['contract']

    assert actions[action] is None, 'Action already registered!'

    if is_confirmed(proposal_id=proposal_id):

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


def unregister_action(proposal_id: int):
    action = proposal[proposal_id]['unregister_action']
    assert actions[action] is not None, 'Action does not exist!'

    if is_confirmed(proposal_id=proposal_id):
        actions[action] = None
        return True
    else:    
        return f"there was no concensus to unregister {action}"
    

# def interact(action: str, payload: dict):
#     contract = actions[action]
#     assert contract is not None, 'invalid action!'

#     module = I.import_module(contract)
#     result = module.interact(payload, S, user)
#     return result   

# def bulk_interact(action: str, payloads: list):
#     for payload in payloads:
#         interact(action, payload)

def change_requirement(proposal_id: str):
    owner_list = owners.get()
    value = proposal[proposal_id]['change_requirement']
    if is_confirmed(proposal_id=proposal_id):
        valid_requirements(len(owner_list) , value)
        required.set(value)    
        return True
    else:    
        return f'there was no concensus to change required confirmations to {value}'

def change_dailylimit(proposal_id: str):
    propsl = proposal[proposal_id]['change_dailylimit']
    keys = list(propsl.keys())
    if 'token' in keys:
        if is_confirmed(proposal_id=proposal_id):
            daily_limit[propsl['token']] = propsl['amount']    
            return True
        else:    
            return f"there was no concensus to change dailylimit to {propsl['amount']}"

    if 'action' in keys:
        if is_confirmed(proposal_id=proposal_id):
            daily_limit[propsl['action']] = propsl['amount']    
            return True
        else:    
            return f"there was no concensus to change dailylimit to {propsl['amount']}"

    if 'external_action' in keys:
        if is_confirmed(proposal_id=proposal_id):
            daily_limit[propsl['external_action']] = propsl['amount']    
            return True
        else:    
            return f"there was no concensus to change dailylimit to {propsl['amount']}"

    


    

