// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "./Token.sol";

contract dBank {
    /** Assign Token contract to a variable */
    Token private token;

    // MAPPINGS

    /** @dev Tracks the ETH balance of all addresses */
    mapping(address => uint256) public etherBalanceOf;

    /** @dev Tracks the time [how long has an address deposited ETH for] */
    mapping(address => uint256) public depositStart;

    /** @dev Tracks the deposit status for an address */
    mapping(address => bool) public isDeposited;

    // EVENTS
    event Deposit(address indexed user, uint256 etherAmount, uint256 timeStart);
    event Withdraw(
        address indexed user,
        uint256 etherAmount,
        uint256 depositTime,
        uint256 interest
    );

    /** @dev _token - Address of the DBC token */
    constructor(Token _token) {
        token = _token;
    }

    /**
     * @notice Deposit ETH into the bank and earn interest
     */
    function deposit() public payable {
        require(
            isDeposited[msg.sender] == false,
            "ERROR: Deposit already active."
        );
        require(
            msg.value >= 0.01 * 10**18,
            "ERROR: Deposit Amount must be greater than 0.01 ETH."
        );
        etherBalanceOf[msg.sender] += msg.value;
        depositStart[msg.sender] += block.timestamp;
        isDeposited[msg.sender] = true; // activates deposit status
        emit Deposit(msg.sender, msg.value, block.timestamp);
    }

    /**
     * @notice Withdraw deposited ETH and the DBC tokens (based on the interest)
 
     */
    function withdraw() public payable {
        require(isDeposited[msg.sender] == true, "ERROR: No previous deposit.");

        // Caching the user-balance
        uint256 userBalance = etherBalanceOf[msg.sender];

        // Check user's HODL time
        uint256 depositTime = block.timestamp - depositStart[msg.sender];
        // Pay the user based on each second of his depositTime.
        uint256 interest = depositTime * 10**17; // In WEI

        // Transfer ETH to the user
        payable(msg.sender).transfer(userBalance);
        // Transfer interest earned in terms of DBC tokens to the user
        token.mint(msg.sender, interest);

        // Reset depositer data
        depositStart[msg.sender] = 0;
        etherBalanceOf[msg.sender] = 0;
        isDeposited[msg.sender] = false;

        // Emit Event
        emit Withdraw(msg.sender, userBalance, depositTime, interest);
    }
}
