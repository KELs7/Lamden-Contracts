I = importlib

S = Hash(default_value=0)
actions = Hash()
owner = Variable()

# Policy interface
action_interface = [
    I.Func('interact', args=('payload', 'state', 'caller')),
]

@construct
def seed():
    owner.set(ctx.caller)

@export
def change_owner(new_owner: str):
    assert ctx.caller == owner.get(), 'Only owner can call!'
    owner.set(new_owner)

@export
def register_action(action: str, contract: str):
    assert ctx.caller == owner.get(), 'Only owner can call!'
    assert actions[action] is None, 'Action already registered!'
    # Attempt to import the contract to make sure it is already submitted
    p = I.import_module(contract)

    # Assert ownership is election_house and interface is correct
    assert I.owner_of(p) == ctx.this, \
        'This contract must control the action contract!'

    assert I.enforce_interface(p, action_interface), \
        'Action contract does not follow the correct interface!'

    actions[action] = contract

@export
def unregister_action(action: str):
    assert ctx.caller == owner.get(), 'Only owner can call!'
    assert actions[action] is not None, 'Action does not exist!'

    actions[action] = None

@export
def interact(action: str, payload: dict):
    contract = actions[action]
    assert contract is not None, 'Invalid action!'

    module = I.import_module(contract)

    result = module.interact(payload, S, ctx.caller)
    return result

@export
def bulk_interact(action: str, payloads: list):
    for payload in payloads:
        interact(action, payload)
            	    
                   
            
