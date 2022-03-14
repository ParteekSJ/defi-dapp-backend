import pytest
from brownie import Token, dBank, accounts as a, Wei, reverts, chain
import time


interestPerSecond = 31668017  # (10% APY) for min. deposit (0.01 ETH)


@pytest.fixture
def contracts(Token, dBank):
    # Deploy Token with an initial supply of a million DBC tokens
    token = Token.deploy({"from": a[0]})
    # Deploy dBank contract (with Token's address for future minting)
    bank = dBank.deploy(token, {"from": a[0]})
    # Pass the minter role to the dBank contract
    token.passMinterRole(bank, {"from": a[0]})
    return [token, bank]


# TOKEN TESTS
def test_token_name(contracts):
    token = contracts[0]
    assert token.name() == "Decentralized Bank Currency"


def test_token_symbol(contracts):
    token = contracts[0]
    assert token.symbol() == "DBC"


def test_token_initial_supply(contracts):
    token = contracts[0]
    assert token.totalSupply() == 0


def test_token_minter_role(contracts):
    token, dBank = contracts[0], contracts[1]
    assert token.minter() == dBank


def test_token_invalid_minter_role(contracts):
    token, dBank = contracts[0], contracts[1]
    with reverts("ERROR: Address not allowed to change minter address."):
        # a[1] is not the owner
        token.passMinterRole(dBank, {"from": a[1]})


def test_token_unauthorized_minter(contracts):
    token = contracts[0]
    with reverts("ERROR: Address not allowed to mint tokens."):
        # a[1] is not authorized to mint DBC tokens
        token.mint(a[2], Wei("100 ether"), {"from": a[1]})


# BANK TESTS

# DEPOSIT TESTS
def test_ether_balance_increases(contracts):
    dBank = contracts[1]
    dBank.deposit({"from": a[1], "value": Wei("1 ether")})

    assert dBank.etherBalanceOf(a[1]) == Wei("1 ether")


def test_deposit_time_increases(contracts):
    dBank = contracts[1]
    dBank.deposit({"from": a[1], "value": Wei("1 ether")})
    time.sleep(1)

    assert dBank.depositStart(a[1]) > 0


def test_deposit_status(contracts):
    dBank = contracts[1]
    dBank.deposit({"from": a[1], "value": Wei("1 ether")})

    assert dBank.isDeposited(a[1]) == True


def test_deposit_event_fires(contracts):
    dBank = contracts[1]
    tx = dBank.deposit({"from": a[1], "value": Wei("1 ether")})

    assert len(tx.events) == 1
    assert "Deposit" in tx.events


def test_invalid_redeposits(contracts):
    dBank = contracts[1]
    dBank.deposit({"from": a[1], "value": Wei("1 ether")})

    with reverts("ERROR: Deposit already active."):
        dBank.deposit({"from": a[1], "value": Wei("1 ether")})


def test_invalid_deposit_amount(contracts):
    dBank = contracts[1]

    with reverts("ERROR: Deposit Amount must be greater than 0.01 ETH."):
        dBank.deposit({"from": a[1], "value": Wei("0.001 ether")})


# WITHDRAW TESTS
def test_ether_balance_decreases(contracts):
    dBank = contracts[1]
    dBank.deposit({"from": a[1], "value": Wei("1 ether")})
    dBank.withdraw({"from": a[1]})

    assert dBank.etherBalanceOf(a[1]) == 0


def test_depositer_receives_ether(contracts):
    prev_balance = a[1].balance()  # 100 ETH

    dBank = contracts[1]
    dBank.deposit({"from": a[1], "value": Wei("1 ether")})  # 99 ETH

    dBank.withdraw({"from": a[1]})  # 100 ETH
    after_balance = a[1].balance()

    assert after_balance == prev_balance


def test_depositer_data_resets(contracts):
    dBank = contracts[1]
    dBank.deposit({"from": a[1], "value": Wei("1 ether")})
    dBank.withdraw({"from": a[1]})

    assert dBank.depositStart(a[1]) == 0
    assert dBank.etherBalanceOf(a[1]) == 0
    assert dBank.isDeposited(a[1]) == False


def test_depositer_receives_interest(contracts):
    token, dBank = contracts[0], contracts[1]

    dBank.deposit({"from": a[1], "value": Wei("1 ether")})
    time.sleep(2)
    dBank.withdraw({"from": a[1]})

    token_balance = token.balanceOf(a[1])

    assert token_balance == 0.2


def test_invalid_withdrawal(contracts):
    token, dBank = contracts[0], contracts[1]

    dBank.deposit({"from": a[1], "value": Wei("1 ether")})
    time.sleep(2)
    dBank.withdraw({"from": a[1]})
