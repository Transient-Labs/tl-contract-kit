// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "OpenZeppelin/openzeppelin-contracts@4.7.0/contracts/token/ERC20/ERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@4.7.0/contracts/access/Ownable.sol";

contract ERC20TL is ERC20, Ownable {

    constructor(string memory name, string memory symbol, address recipient, uint256 mintAmount)
        ERC20(name, symbol)
        Ownable()
    {
        _mint(recipient, mintAmount);
    }
}