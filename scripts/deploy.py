from brownie import Token, dBank, accounts as a, network, config

DEVELOPMENT_NETWORKS = ["ganache", "development"]
PRODUCTION_NETWORKS = ["rinkeby-alchemy"]


def get_account():
    if network.show_active() in PRODUCTION_NETWORKS:
        return a.add(config["wallets"]["from_key"])
    else:
        return a[0]


def main():
    # Getting the account based on the network
    account = get_account()
    # Deploy Token with no initial supply (we'll be minting tokens on the fly.)
    token = Token.deploy({"from": account})
    # Deploy dBank contract (with Token's address for future minting)
    dbank = dBank.deploy(token, {"from": account})
    # Pass the minter role to the dBank contract
    token.passMinterRole(dbank, {"from": account})

    print("TOKEN DEPLOYED AT", token)
    print("BANK DEPLOYED AT", dbank)
