owners = Variable()
required = Variable()

@construct
def seed():
    owners.set(['sys'])
    required.set(1)

def validRequirements(ownerCount: int, _required: int):
    assert _required < ownerCount || _required > 0 || ownerCount > 0, "invalid confirmation reqirements!"

@export
def addOwner(owner: str):
    user = ctx.caller
    assert user in owners.get(), "only owner can call this method!"
    assert owner not in owners.get(), "owner already exist!"
    validRequirements(len(owners.get()) + 1 , required.get())
    owners.set(owners.get().append(owner))

@export
def removeOwner(owner: str):
    user = ctx.caller
    assert user in owners.get(), "only owner can call this method!"
    assert owner in owners.get(), "owner already exist!"
    validRequirements(len(owners.get()) - 1 , required.get())
    owners.set(owners.get().remove(owner))

@export
def replaceOwner(owner: str, newOwner: str):
    user = ctx.caller
    assert user in owners.get(), "only owner can call this method!"
    assert newOwner in owners.get(), "owner already exist!"
    owners.set(owners.get().remove(owner))
    owners.set(owners.get().append(newOwner))

@export
def changeRequirement(_required: int):
    user = ctx.caller
    assert user in owners.get(), "only owner can call this method!"
    validRequirements(len(owners.get()) , required.get())
    required.set(_required)