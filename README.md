# Transient Labs Smart Contract Kit

This repository is meant to serve as an inheritable library of smart contracts. Development uses the eth-brownie framework (https://github.com/eth-brownie/brownie)

## Contracts
### Royalty
These contracts follow EIP-2981 for on chain royalty information. There are options for universal royalty configuration and multi-token royalty configuration. 

#### Universal Royalty Configuration (All Token)
This sets a standard royalty percentage and payout address that is the same across all tokens.

#### Multi-Token Royalty Configuration
This sets a royalty percentage and payout address that is unique for each token.

### Token
These contracts are generally the core, reusable, inheritable ERC 721 and ERC 1155 contracts that Transient Lab uses

### VulnerabilityTest
These contracts are used to test vulnerabilities in the test suite.

## Tests
These are the tests that the contracts pass. All tests must pass before committing.

## Utils
These are utility functions that are used in testing. Currently most are written in javascript, but there are plans to port to Python as it helps the Python ecosystem.

## License
All code is licensed per the GPL 3.0 License.