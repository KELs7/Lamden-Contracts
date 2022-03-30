I = importlib
metadata = Hash()

@construct
def seed():
    metadata['operator'] = ctx.caller    
    metadata['rate'] = decimal('0.01')

@export
def change_metadata(key: str, value: Any):
    assert ctx.caller == metadata['operator'], "only operator can set metadata"
    metadata[key] = value

@export
def burn(amount: float):
    assert amount > 0,"negative amount not allowed!"
    I.import_module('con_demoncoin').transfer_from(amount=amount, to='000000000000000000000000000000HELL000000000000000000000000000000', main_account=ctx.caller) 
    reward = amount *  metadata['rate'] 
    I.import_module('con_crusader_contract').transfer(amount=reward, to=ctx.caller)

