# Lamden Multisig Contract

A multisignature (multisig) contract enables multiple owners/signers to review and agree on a course of action before executing a transaction on the blockchain.

This multisig contract is written for the highly performant Python blockchain [Lamden](https://www.lamden.io) and it's based on the Ethereum multisig implementation [here](https://github.com/ConsenSysMesh/MultiSigWallet/blob/master/MultiSigWalletWithDailyLimit.sol)

## Features

* supports any number of owners/signers

* add, remove, replace owners/signers (requires consensus of other owners/signers)

* required number of confirmations can be changed
(requires consensus of other owners/signers)

* daily limit is applied and can be changed
(requires consensus of other owners/signers)

* supports only LST001 token standard at the moment
