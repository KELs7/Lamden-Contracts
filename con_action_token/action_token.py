@export
def interact(payload: dict, state: Any, caller: str):
	#total token supply 
	state['balances', 'sys'] = 1000000
	
	if payload['function'] == 'transfer':
		transfer(caller=caller, amount=payload['amount'], to=payload['to'], state=state)
	elif payload['function'] == 'approve':
		approve(caller=caller, amount=payload['amount'], to=payload['to'], state=state)
	elif payload['function'] == 'transfer_from':
		transfer_from(caller=caller, amount=payload['amount'], to=payload['to'], main_account=payload['main_acc'], state=state)
	else:
		raise Exception('Invalid function name')
		
def transfer(caller: str, amount: float, to: str, state: Any):
	assert amount > 0, 'Cannot send negative balances!'
	assert state['balances', caller] >= amount, 'Not enough CURRENCY to send!'

	state['balances', caller] -= amount
	state['balances', to] = amount

def approve(caller: str, amount: float, to: str, state: Any):
	assert amount > 0, 'Cannot send negative balances!'

	state['balances', caller, to] += amount
	return state['balances', caller, to]

def transfer_from(caller: str, amount: float, to: str, main_account: str, state: Any):
	assert amount > 0, 'Cannot send negative balances!'
	assert state['balances', main_account, caller] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'.format(state['balances', main_account, caller], amount)
	assert state['balances', main_account] >= amount, 'Not enough coins to send!'
	
	state['balances', main_account, caller] -= amount
	state['balances', main_account] -= amount
	state['balances', to] += amount



