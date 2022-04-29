# Lamden Multisig Contract

A multisignature (multisig) contract enables multiple `owners/signers` to review and agree on a course of action before executing a transaction on the blockchain.

This multisig contract is written for the highly performant Python blockchain [Lamden](https://www.lamden.io) and it was initially based on the Ethereum multisig implementation [here](https://github.com/ConsenSysMesh/MultiSigWallet/blob/master/MultiSigWalletWithDailyLimit.sol). 

## Features

* supports any number of `owners/signers`

* add, remove, replace owners/signers (requires consensus of other `owners/signers`)

* required number of confirmations can be changed
(requires consensus of other `owners/signers`)

* daily limit is applied and can be changed
(requires consensus of other `owners/signers`)

* supports LST001 token standard, and the use of action contracts both internally and externally

## Usage

To submit a proposal, `owner/signer` must call the `submit_proposal` method of the multisig contract and pass a python dictionary to the `propsl` parameter.

eg:
```
submit_proposal(propsl={'change_requirement': 5})
```

There are 3 types of proposals that can be made.
* State updates
* LST001 Token Transactions
* Action Transactions

### State Updates
There are 7 kinds of proposals that can be submitted under this category
* add owner
* remove owner
* replace owner
* register action contract
* unregister action contract
* change required number of confirmations
* change daily limit


#### add owner
```
submit_proposal(propsl={'add_owner': 'some_wallet'})
```

#### remove owner
```
submit_proposal(propsl={'remove_owner': 'some_wallet'})
```

#### replace owner
```
submit_proposal(propsl={
	'replace_owner': {
		'new_owner': 'some_wallet',
		'existng_owner': 'some_wallet'}})
```
#### register action contract
```
submit_proposal(propsl={'register_action': 'some_action_contract'})
```
#### unregister action contract
```
submit_proposal(propsl={'unregister_action': 'some_action_contract'})
```
#### change required number of confirmations
```
submit_proposal(propsl={'change_requirement': 5})
```
#### change daily limit
```
submit_proposal(propsl={
	'change_dailylimit': {
		'token': 'currency', 
		'amount': 1000}})
```
for an action contract of monetary value
```
submit_proposal(propsl={
	'change_dailylimit': {
		'action': 'gToken',
		 'amount': 1000}})
```
action contract of an external action core contract
```
submit_proposal(propsl={
	'change_dailylimit': {
		'external_action': 'eToken',
		 'amount': 1000}})
```

### LST001 token transactions
```
submit_proposal(propsl={
	'token': 'currency',
	'payload': {
		'method': 'transfer',
		'amount': 200,
		'to': 'some_wallet'}}) 
```

`aprrove` and `transfer_from` methods are supported as well.
Example for `transfer_from`:

```
submit_proposal(propsl = {
    'token': 'currency',
    'payload': {
        'method': 'transfer_from',
        'amount': 456,
        'to': 'test_test',
        'main_account': 'vault'}})
```

### Action transactions
There are 2 kinds of proposals that can be made under this category
* internal action transaction
* external action transaction

#### internal action transactions
This is a call to an action contract controlled by the multisig contract

```
submit_proposal(propsl={
	'action': 'some_action_contract', 
	'bulk': False,
	'payload':payload})
```
`payload` must be a dictionary

#### external action transactions
This is a call to other action core contracts to execute a particular action method
```
submit_proposal(propsl={
	'action_core': 'some_external_action_core_contract', 
	'action': 'some_action_contract', 
	'bulk': False,
	'payload':payload})
```



