// SPDX-License-Identifier: GPL-3.0-or-later

/**
*   @title ERC-721A TL Core
*   @author transientlabs.xyz
*/

/*
   ___       _ __   __  ___  _ ______                 __ 
  / _ )__ __(_) /__/ / / _ \(_) _/ _/__ _______ ___  / /_
 / _  / // / / / _  / / // / / _/ _/ -_) __/ -_) _ \/ __/
/____/\_,_/_/_/\_,_/ /____/_/_//_/ \__/_/  \__/_//_/\__/                                                          
 ______                  _          __    __        __     
/_  __/______ ____  ___ (_)__ ___  / /_  / /  ___ _/ /  ___
 / / / __/ _ `/ _ \(_-</ / -_) _ \/ __/ / /__/ _ `/ _ \(_-<
/_/ /_/  \_,_/_//_/___/_/\__/_//_/\__/ /____/\_,_/_.__/___/ 
*/

pragma solidity >0.8.9 <0.9.0;

import "chiru-labs/ERC721A@4.1.0/contracts/ERC721A.sol";
import "OpenZeppelin/openzeppelin-contracts@4.7.0/contracts/token/ERC20/IERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@4.7.0/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.7.0/contracts/utils/cryptography/MerkleProof.sol";
import "../../royalty/EIP2981AllToken.sol";

contract ERC721ATLCore is ERC721A, EIP2981AllToken, Ownable {

    bool public allowlistSaleOpen;
    bool public publicSaleOpen;
    bool public frozen;
    uint256 public mintAllowance;
    uint256 public mintPrice;
    uint256 public maxSupply;
    
    address payable public payoutAddress;
    address public adminAddress;

    bytes32 public allowlistMerkleRoot;
    
    string internal _baseTokenURI;

    modifier isNotFrozen {
        require(!frozen, "ERC721ATLCore: Metadata is frozen");
        _;
    }

    modifier adminOrOwner {
        require(msg.sender == adminAddress || msg.sender == owner(), "ERC721ATLCore: Address not admin or owner");
        _;
    }

    modifier isEOA {
        require(msg.sender == tx.origin, "ERC721ATLCore: Function must be called by an EOA");
        _;
    }

    /**
    *   @param name is the name of the contract
    *   @param symbol is the symbol
    *   @param royaltyRecipient is the royalty recipient
    *   @param royaltyPercentage is the royalty percentage to set
    *   @param price is the mint price
    *   @param supply is the total token supply for minting
    *   @param merkleRoot is the allowlist merkle root
    *   @param admin is the admin address
    *   @param payout is the payout address
    */
    constructor (
        string memory name,
        string memory symbol,
        address royaltyRecipient,
        uint256 royaltyPercentage,
        uint256 price,
        uint256 supply,
        bytes32 merkleRoot,
        address admin,
        address payout
    )
        ERC721A(name, symbol)
        Ownable()
        EIP2981AllToken(royaltyRecipient, royaltyPercentage)
    {
        mintPrice = price;
        maxSupply = supply;
        allowlistMerkleRoot = merkleRoot;
        adminAddress = admin;
        payoutAddress = payable(payout);
        maxSupply = supply;
    }

    /**
    *   @notice function to set the allowlist mint status
    *   @param status is the true/false flag for the allowlist mint status
    */
    function setAllowlistSaleStatus(bool status) external virtual adminOrOwner {
        allowlistSaleOpen = status;
    }

    /**
    *   @notice function to set the public mint status
    *   @param status is the true/false flag for the allowlist mint status
    */
    function setPublicSaleStatus(bool status) external virtual adminOrOwner {
        publicSaleOpen = status;
    }

    /**
    *   @notice freezes the metadata for the token
    *   @dev requires admin or owner
    */
    function freezeMetadata() external virtual adminOrOwner {
        frozen = true;
    }

    /**
    *   @notice sets the mint allowance for each address
    *   @dev requires admin or owner
    *   @param allowance is the new allowance
    */
    function setMintAllowance(uint256 allowance) external virtual adminOrOwner {
        mintAllowance = allowance;
    }

    /**
    *   @notice sets the base URI
    *   @dev requires admin or owner
    *   @param newURI is the base URI set for each token
    */
    function setBaseURI(string memory newURI) external virtual adminOrOwner isNotFrozen {
        _baseTokenURI = newURI;
    }

    /**
    *   @notice function to change the royalty info
    *   @dev requires admin or owner
    *   @dev this is useful if the amount was set improperly at contract creation.
    *   @param newAddr is the new royalty payout addresss
    *   @param newPerc is the new royalty percentage, in basis points (out of 10,000)
    */
    function setRoyaltyInfo(address newAddr, uint256 newPerc) external virtual adminOrOwner {
        _setRoyaltyInfo(newAddr, newPerc);
    }

    /**
    *   @notice function to withdraw ERC20 tokens from the contract
    *   @dev requires admin or owner
    *   @dev requires payout address to be abel to receive ERC20 tokens
    *   @param tokenAddress is the ERC20 contract address
    *   @param amount is the amount to withdraw
    */
    function withdrawERC20(address tokenAddress, uint256 amount) external virtual adminOrOwner {
        IERC20 erc20 = IERC20(tokenAddress);
        require(amount <= erc20.balanceOf(address(this)), "ERC721ATLCore: cannot withdraw more than balance");
        erc20.transfer(payoutAddress, amount);
    }

    /**
    *   @notice function to withdraw ether from the contract
    *   @dev requires admin or owner
    *   @dev recipient MUST be an EOA or contract that does not require more than 2300 gas
    *   @param amount is the amount to withdraw
    */
    function withdrawEther(uint256 amount) external virtual adminOrOwner {
        require(amount <= address(this).balance, "ERC721ATLCore: cannot withdraw more than balance");
        payoutAddress.transfer(amount);
    }

    /**
    *   @notice function to set the admin address on the contract
    *   @dev requires owner
    *   @param newAdmin is the new admin address
    */
    function setAdminAddress(address newAdmin) external virtual onlyOwner {
        require(newAdmin != address(0), "ERC721ATLCore: New admin cannot be the zero address");
        adminAddress = newAdmin;
    }

    /**
    *   @notice function to set the payout address
    *   @dev requires owner
    *   @param payoutAddr is the new payout address
    */
    function setPayoutAddress(address payoutAddr) external virtual onlyOwner {
        require(payoutAddr != address(0), "ERC721ATLCore: Payout address cannot be the zero address");
        payoutAddress = payable(payoutAddr);
    }

    /**
    *   @notice function to get number minted
    *   @param addr address to query
    *   @return uint256 for number minted
    */
    function getNumMinted(address addr) external view virtual returns (uint256) {
        return _numberMinted(addr);
    }

    /**
    *   @notice function to view remaining supply
    */
    function getRemainingSupply() external view virtual returns (uint256) {
        return maxSupply + 1 - _nextTokenId();
    }
   
    /**
    *   @notice overrides supportsInterface function
    *   @param interfaceId is supplied from anyone/contract calling this function, as defined in ERC 165
    *   @return a boolean saying if this contract supports the interface or not
    */
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721A, EIP2981AllToken) returns (bool) {
        return ERC721A.supportsInterface(interfaceId) || EIP2981AllToken.supportsInterface(interfaceId);
    }

    /**
    *   @notice override standard ERC721 base URI
    *   @dev doesn't require access control since it's internal
    *   @return string representing base URI
    */
    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }

    /**
     * @dev Returns the starting token ID. 
     * To change the starting token ID, please override this function.
     */
     function _startTokenId() internal view virtual override returns (uint256) {
        return 1;
    }
}