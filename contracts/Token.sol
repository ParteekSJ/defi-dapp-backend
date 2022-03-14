// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract Token is ERC20 {
    address public minter;

    event MinterChanged(
        address indexed currentMinter,
        address indexed newMinter
    );

    constructor() ERC20("Decentralized Bank Currency", "DBC") {
        minter = msg.sender;
    }

    /**
     * @notice Minting tokens. Function to create/mint tokens on the `FLY`
     * @param account - Address we're minting the tokens for
     * @param amount - Amount of tokens being minted
     */
    function mint(address account, uint256 amount) public {
        require(
            msg.sender == minter,
            "ERROR: Address not allowed to mint tokens."
        );
        _mint(account, amount);
    }

    /**
     * @notice Change the minter address.
     * @param dBank - Address of the new minter
     */
    function passMinterRole(address dBank) public returns (bool) {
        require(
            msg.sender == minter,
            "ERROR: Address not allowed to change minter address."
        );
        minter = dBank;

        emit MinterChanged(msg.sender, dBank);
        return true;
    }
}
