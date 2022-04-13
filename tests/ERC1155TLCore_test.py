from brownie import ERC1155TLCore, ERC1155TLCoreMintReentrancy, ERC1155TLCoreAirdropReentrancy, a, Wei
from web3 import Web3
import brownie
import pytest

''' Setup '''
# 4 tokens
#   Token 0: airdrop + owner mint
#   Token 1: mint + owner mint
#   Token 2: airdrop + mint
#   Token 3: claim
# Addresses
#   a[0] --> owner
#   a[1] --> admin
#   a[2] --> payout
#   a[3] --> royalty recipient for all tokens
#   a[4:10] --> airdrop token 0 and 2
#   a[4:7] --> mint token 1
#   a[7:10] --> mint token 2
#   a[4:10] --> claim token 3
#   run `node utils/ERC1155TLCore.merkleTree.js` to generate merkle data for tokens 1 and 2
merkleRoots = ["0x1d8c3fe103f58db27a9a8e824b1af9ec98a7fb3434ea37750f6206c0da288903", "0x1810231effaa044262b0deff02747c16879b59c0a00ebce71841379005c3a297"]
merkleProofs = [[
    [
    '0x50ba2086958d320d73135728ff30eae03ef09b45fea302102d844697eb2f4b6d',
    '0xf9e19de495b8998dfee29352ebd3bfe146263e1f8b3223187244cf38e03ab9c5'
    ],
    [
    '0x344d536da52f2f25e5f9e89b357952f4ed7fdf6a74025f4a9098dc355396695a',
    '0xf9e19de495b8998dfee29352ebd3bfe146263e1f8b3223187244cf38e03ab9c5'
    ],
    [
    '0xe9c363ac8b15db69db1f132015672432dae2ca766a668862d5371379ce145d38'
    ]
],[
    [
    '0xa66853c8a78e907a4a2acdc3e487c44c7a209f08c51b10fb0716cd88933deb77',
    '0x68821ccb3ea1d9a1499c2969de326dc67891ea8f1207df68e5e85b4b38c1df7e'
    ],
    [
    '0x56b42d1222f4ba527d5e45f1b99bdce76dbcc85a7c51d00d3c9da035345f5968',
    '0x68821ccb3ea1d9a1499c2969de326dc67891ea8f1207df68e5e85b4b38c1df7e'
    ],
    [
    '0x104f7877145a4f580cb1a52f7f48b3be349730dde0dbc957181755e34ad23f4b'
    ]
]]

@pytest.fixture(scope="module")
def owner():
    return a[0]

@pytest.fixture(scope="module")
def admin():
    return a[1]

@pytest.fixture(scope="module")
def payout():
    return a[2]

@pytest.fixture(scope="module")
def royaltyAddr():
    return a[3]

@pytest.fixture(scope="module")
def token0(royaltyAddr):
    return [0, 10, False, 0, 0, "test0", Web3.toHex(b''), royaltyAddr.address, 500]

@pytest.fixture(scope="module")
def token1(royaltyAddr):
    return [1, 10, False, 1, Wei("0.5 ether"), "test1", merkleRoots[0], royaltyAddr.address, 750]

@pytest.fixture(scope="module")
def token2(royaltyAddr):
    return [2, 10, False, 1, Wei("0.2 ether"), "test2", merkleRoots[1], royaltyAddr.address, 1000]

@pytest.fixture(scope="module")
def token3(royaltyAddr):
    return [3, 10, False, 2, 0, "test3", Web3.toHex(b''), royaltyAddr.address, 1250]

@pytest.fixture(scope="class")
def contract(owner, admin, payout):
    return ERC1155TLCore.deploy(admin.address, payout.address, "ERC1155 Test", {"from": owner})

class Test_Setup:
    def test_name(self, contract, admin, payout):
        assert contract.name() == "ERC1155 Test"

    def test_admin(self, contract, admin, payout):
        assert contract.adminAddress() == admin.address
    
    def test_payout(self, contract, admin, payout):
        assert contract.payoutAddress() == payout.address

class Test_Non_Owner_Admin_No_Access:
    revertStr = "ERC1155TLCore: Address not admin or owner"
    def test_create_token(self, contract, token0):
        with brownie.reverts(self.revertStr):
            contract.createToken(*token0, {"from": a[4]})

    def test_set_mint_allowance(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setMintAllowance(0, 1, {"from": a[4]})

    def test_freeze_token(self, contract):
        with brownie.reverts(self.revertStr):
            contract.freezeToken(0, {"from": a[4]})

    def test_set_uri(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setURI(0, "test", {"from": a[4]})

    def test_set_mint_status(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setMintStatus(0, True, {"from": a[4]})

    def test_set_royalty_recipient(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setRoyaltyRecipient(0, a[4].address, {"from": a[4]})

    def test_set_royalty_percentage(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setRoyaltyPercentage(0, 1000, {"from": a[4]})

    def test_airdrop(self, contract):
        with brownie.reverts(self.revertStr):
            contract.airdrop(0, [a[4].address]*3, {"from": a[4]})

    def test_owner_mint(self, contract):
        with brownie.reverts(self.revertStr):
            contract.ownerMint(0, 5, {"from": a[4]})

    def test_withdraw_ether(self, contract):
        with brownie.reverts(self.revertStr):
            contract.withdrawEther({"from": a[4]})

class Test_Non_Owner_No_Access:
    revertStr = "Ownable: caller is not the owner"

    def test_set_admin_address_user(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setAdminAddress(a[4].address, {"from": a[4]})

    def test_set_admin_address_admin(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.setAdminAddress(a[4].address, {"from": admin})

    def test_set_payout_address_user(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setPayoutAddress(a[4].address, {"from": a[4]})

    def test_set_payout_address_admin(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.setPayoutAddress(a[4].address, {"from": admin})

class Test_Admin_Access:
    def test_create_token(self, contract, admin, token0):
        contract.createToken(*token0, {"from": admin})
        supply = contract.getTokenSupply(0)
        allowance = contract.getMintAllowance(0)
        status = contract.getMintStatus(0)
        price = contract.getTokenPrice(0)
        root = contract.getMerkleRoot(0)
        [recp, amt] = contract.royaltyInfo(0, Wei("1 ether"))
        uri = contract.uri(0)
        assert [0, supply, status, allowance, price, uri, root, recp, amt*10000/Wei("1 ether")] == token0

    def test_duplicate_token(self, contract, admin, token0):
        with brownie.reverts("ERC1155TLCore: Token ID already exists"):
            contract.createToken(*token0, {"from": admin})

    def test_set_mint_allowance(self, contract, admin):
        contract.setMintAllowance(0, 1, {"from": admin})
        assert contract.getMintAllowance(0) == 1

    def test_set_uri(self, contract, admin):
        contract.setURI(0, "test", {"from": admin})
        assert contract.uri(0) == "test"

    def test_freeze_token(self, contract, admin):
        contract.freezeToken(0, {"from": admin})
        with brownie.reverts("ERC1155TLCore: Token metadata frozen"):
            contract.setURI(0, "tests", {"from": admin})

    def test_set_mint_status(self, contract, admin):
        contract.setMintStatus(0, True, {"from": admin})
        assert contract.getMintStatus(0)

    def test_set_royalty_recipient(self, contract, admin):
        contract.setRoyaltyRecipient(0, admin.address, {"from": admin})
        [recp, amt] = contract.royaltyInfo(0, Wei("1 ether"))
        assert recp == admin.address

    def test_set_royalty_percentage(self, contract, admin):
        contract.setRoyaltyPercentage(0, 1000, {"from": admin})
        [recp, amt] = contract.royaltyInfo(0, Wei("1 ether"))
        assert amt == Wei(f"{1000/10000} ether")

    def test_airdrop(self, contract, admin):
        contract.airdrop(0, [admin.address]*3, {"from": admin})
        assert contract.balanceOf(admin.address, 0) == 3

    def test_owner_mint(self, contract, admin, owner):
        contract.ownerMint(0, 5, {"from": admin})
        assert contract.balanceOf(owner.address, 0) == 5

    def test_withdraw_ether(self, contract, admin):
        contract.withdrawEther({"from": admin})

class Test_Owner_Access:
    def test_create_token(self, contract, owner, token1):
        contract.createToken(*token1, {"from": owner})
        supply = contract.getTokenSupply(1)
        allowance = contract.getMintAllowance(1)
        status = contract.getMintStatus(1)
        price = contract.getTokenPrice(1)
        root = contract.getMerkleRoot(1)
        [recp, amt] = contract.royaltyInfo(1, Wei("1 ether"))
        uri = contract.uri(1)
        assert [1, supply, status, allowance, price, uri, root, recp, amt*10000/Wei("1 ether")] == token1

    def test_duplicate_token(self, contract, owner, token1):
        with brownie.reverts("ERC1155TLCore: Token ID already exists"):
            contract.createToken(*token1, {"from": owner})

    def test_set_mint_allowance(self, contract, owner):
        contract.setMintAllowance(1, 1, {"from": owner})
        assert contract.getMintAllowance(1) == 1

    def test_set_uri(self, contract, owner):
        contract.setURI(1, "test", {"from": owner})
        assert contract.uri(1) == "test"

    def test_freeze_token(self, contract, owner):
        contract.freezeToken(1, {"from": owner})
        with brownie.reverts("ERC1155TLCore: Token metadata frozen"):
            contract.setURI(1, "tests", {"from": owner})

    def test_set_mint_status(self, contract, owner):
        contract.setMintStatus(1, True, {"from": owner})
        assert contract.getMintStatus(1)

    def test_set_royalty_recipient(self, contract, owner, admin):
        contract.setRoyaltyRecipient(1, admin.address, {"from": owner})
        [recp, amt] = contract.royaltyInfo(1, Wei("1 ether"))
        assert recp == admin.address

    def test_set_royalty_percentage(self, contract, owner):
        contract.setRoyaltyPercentage(1, 1000, {"from": owner})
        [recp, amt] = contract.royaltyInfo(1, Wei("1 ether"))
        assert amt == Wei(f"{1000/10000} ether")

    def test_airdrop(self, contract, admin, owner):
        contract.airdrop(1, [admin.address]*3, {"from": owner})
        assert contract.balanceOf(admin.address, 1) == 3

    def test_owner_mint(self, contract, admin, owner):
        contract.ownerMint(1, 5, {"from": owner})
        assert contract.balanceOf(owner.address, 1) == 5

    def test_withdraw_ether(self, contract, owner):
        contract.withdrawEther({"from": owner})

class Test_Non_Existent_Token_Id:
    revertStr = "ERC1155TLCore: Token ID not valid"

    def test_set_mint_allowance(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.setMintAllowance(0, 1, {"from": admin})

    def test_freeze_token(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.freezeToken(0, {"from": admin})

    def test_set_uri(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.setURI(0, "test", {"from": admin})

    def test_set_mint_status(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.setMintStatus(0, True, {"from": admin})

    def test_set_royalty_recipient(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.setRoyaltyRecipient(0, admin.address, {"from": admin})

    def test_set_royalty_percentage(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.setRoyaltyPercentage(0, 1000, {"from": admin})

    def test_airdrop(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.airdrop(0, [admin.address]*3, {"from": admin})

    def test_owner_mint(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.ownerMint(0, 5, {"from": admin})

    def test_mint(self, contract):
        with brownie.reverts(self.revertStr):
            contract.mint(0, 5, [], {"from": a[4]})

class Test_Token_0:
    def test_create_token(self, contract, admin, token0):
        contract.createToken(*token0, {"from": admin})
        supply = contract.getTokenSupply(0)
        allowance = contract.getMintAllowance(0)
        status = contract.getMintStatus(0)
        price = contract.getTokenPrice(0)
        root = contract.getMerkleRoot(0)
        [recp, amt] = contract.royaltyInfo(0, Wei("1 ether"))
        uri = contract.uri(0)
        assert [0, supply, status, allowance, price, uri, root, recp, amt*10000/Wei("1 ether")] == token0

    def test_mint(self, contract):
        with brownie.reverts("ERC1155TLCore: Mint not open"):
            contract.mint(0, 1, [], {"from": a[4]})

    def test_airdrop(self, contract, admin, token0):
        contract.airdrop(0, a[4:10], {"from": admin})
        assert contract.balanceOf(a[4].address, 0) == 1 and contract.balanceOf(a[5].address, 0) == 1 and contract.balanceOf(a[6].address, 0) == 1 \
            and contract.balanceOf(a[7].address, 0) == 1 and contract.balanceOf(a[8].address, 0) == 1 and contract.balanceOf(a[9].address, 0) == 1 \
            and contract.getTokenSupply(0) == token0[1] - 6
        
    def test_owner_mint(self, contract, admin, owner, token0):
        contract.ownerMint(0, token0[1] - 6, {"from": admin})
        assert contract.balanceOf(owner.address, 0) == token0[1] - 6 and contract.getTokenSupply(0) == 0

    def test_airdrop_no_supply(self, contract, admin):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.airdrop(0, [a[4].address]*3, {"from": admin})

    def test_owner_mint_no_supply(self, contract, admin):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.ownerMint(0, 3, {"from": admin})
    
    def test_mint_no_supply(self, contract):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.mint(0, 1, [], {"from": a[4]})

class Test_Token_1:
    def test_create_token(self, contract, admin, token1):
        contract.createToken(*token1, {"from": admin})
        supply = contract.getTokenSupply(1)
        allowance = contract.getMintAllowance(1)
        status = contract.getMintStatus(1)
        price = contract.getTokenPrice(1)
        root = contract.getMerkleRoot(1)
        [recp, amt] = contract.royaltyInfo(1, Wei("1 ether"))
        uri = contract.uri(1)
        assert [1, supply, status, allowance, price, uri, root, recp, amt*10000/Wei("1 ether")] == token1

    def test_mint_not_open(self, contract):
        with brownie.reverts("ERC1155TLCore: Mint not open"):
            contract.mint(1, 1, [], {"from": a[4]})

    def test_mint_no_ether(self, contract, admin):
        contract.setMintStatus(1, True, {"from": admin})
        with brownie.reverts("ERC1155TLCore: Not enough ether attached to the transaction"):
            contract.mint(1, 1, merkleProofs[0][0], {"from": a[4]})

    def test_mint(self, contract, token1):
        contract.mint(1, 1, merkleProofs[0][0], {"from": a[4], "value": token1[4]})
        contract.mint(1, 1, merkleProofs[0][1], {"from": a[5], "value": token1[4]})
        contract.mint(1, 1, merkleProofs[0][2], {"from": a[6], "value": token1[4]})
        assert contract.balanceOf(a[4].address, 1) == 1 and contract.balanceOf(a[5].address, 1) == 1 and contract.balanceOf(a[6].address, 1) == 1

    def test_mint_allowance_reached(self, contract, token1):
        with brownie.reverts("ERC1155TLCore: Cannot mint more than allowed"):
            contract.mint(1, 1, merkleProofs[0][0], {"from": a[4], "value": token1[4]})
    
    def test_mint_not_on_allowlist(self, contract, token1):
        with brownie.reverts("ERC1155TLCore: Not on allowlist"):
            contract.mint(1, 1, [], {"from": a[7], "value": token1[4]})

    def test_mint_again(self, contract, token1, admin):
        contract.setMintAllowance(1, 2, {"from": admin})
        contract.mint(1, 1, merkleProofs[0][0], {"from": a[4], "value": token1[4]})
        contract.mint(1, 1, merkleProofs[0][1], {"from": a[5], "value": token1[4]})
        contract.mint(1, 1, merkleProofs[0][2], {"from": a[6], "value": token1[4]})
        assert contract.balanceOf(a[4].address, 1) == 2 and contract.balanceOf(a[5].address, 1) == 2 and contract.balanceOf(a[6].address, 1) == 2

    def test_mint_no_supply(self, contract, token1):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.mint(1, 5, [], {"from": a[4], "value": token1[4]*5})
        
    def test_owner_mint(self, contract, admin, owner, token1):
        contract.ownerMint(1, token1[1] - 6, {"from": admin})
        assert contract.balanceOf(owner.address, 1) == token1[1] - 6 and contract.getTokenSupply(1) == 0

    def test_airdrop_no_supply(self, contract, admin):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.airdrop(1, [a[4].address]*3, {"from": admin})

    def test_owner_mint_no_supply(self, contract, admin):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.ownerMint(1, 3, {"from": admin})

class Test_Token_2:
    def test_create_token(self, contract, admin, token2):
        contract.createToken(*token2, {"from": admin})
        supply = contract.getTokenSupply(2)
        allowance = contract.getMintAllowance(2)
        status = contract.getMintStatus(2)
        price = contract.getTokenPrice(2)
        root = contract.getMerkleRoot(2)
        [recp, amt] = contract.royaltyInfo(2, Wei("1 ether"))
        uri = contract.uri(2)
        assert [2, supply, status, allowance, price, uri, root, recp, amt*10000/Wei("1 ether")] == token2

    def test_mint_not_open(self, contract):
        with brownie.reverts("ERC1155TLCore: Mint not open"):
            contract.mint(2, 1, [], {"from": a[7]})

    def test_mint_no_ether(self, contract, admin):
        contract.setMintStatus(2, True, {"from": admin})
        with brownie.reverts("ERC1155TLCore: Not enough ether attached to the transaction"):
            contract.mint(2, 1, merkleProofs[1][0], {"from": a[7]})

    def test_mint(self, contract, token2):
        contract.mint(2, 1, merkleProofs[1][0], {"from": a[7], "value": token2[4]})
        contract.mint(2, 1, merkleProofs[1][1], {"from": a[8], "value": token2[4]})
        contract.mint(2, 1, merkleProofs[1][2], {"from": a[9], "value": token2[4]})
        assert contract.balanceOf(a[7].address, 2) == 1 and contract.balanceOf(a[8].address, 2) == 1 and contract.balanceOf(a[9].address, 2) == 1

    def test_mint_allowance_reached(self, contract, token2):
        with brownie.reverts("ERC1155TLCore: Cannot mint more than allowed"):
            contract.mint(2, 1, merkleProofs[1][0], {"from": a[7], "value": token2[4]})
    
    def test_mint_not_on_allowlist(self, contract, token2):
        with brownie.reverts("ERC1155TLCore: Not on allowlist"):
            contract.mint(2, 1, [], {"from": a[4], "value": token2[4]})

    def test_mint_again(self, contract, token2, admin):
        contract.setMintAllowance(2, 2, {"from": admin})
        contract.mint(2, 1, merkleProofs[1][0], {"from": a[7], "value": token2[4]})
        contract.mint(2, 1, merkleProofs[1][1], {"from": a[8], "value": token2[4]})
        contract.mint(2, 1, merkleProofs[1][2], {"from": a[9], "value": token2[4]})
        assert contract.balanceOf(a[7].address, 2) == 2 and contract.balanceOf(a[8].address, 2) == 2 and contract.balanceOf(a[9].address, 2) == 2 \
            and contract.getNumMinted(2, a[7].address) == 2 and contract.getNumMinted(2, a[8].address) == 2 and contract.getNumMinted(2, a[9].address) == 2

    def test_mint_no_supply(self, contract, token2):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.mint(2, 5, [], {"from": a[7], "value": token2[4]*5})
        
    def test_airdop(self, contract, admin, token2):
        contract.airdrop(2, [admin.address]*(token2[1] - 6), {"from": admin})
        assert contract.balanceOf(admin.address, 2) == token2[1] - 6 and contract.getTokenSupply(2) == 0

    def test_airdrop_no_supply(self, contract, admin):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.airdrop(2, [a[4].address]*3, {"from": admin})

    def test_owner_mint_no_supply(self, contract, admin):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.ownerMint(2, 3, {"from": admin})

    def test_withdraw_ether(self, contract, admin, payout):
        init_balance = payout.balance()
        contract_balance = contract.balance()
        contract.withdrawEther({"from": admin})
        assert payout.balance() - init_balance == contract_balance

class Test_Token_3:
    def test_create_token(self, contract, admin, token3):
        contract.createToken(*token3, {"from": admin})
        supply = contract.getTokenSupply(3)
        allowance = contract.getMintAllowance(3)
        status = contract.getMintStatus(3)
        price = contract.getTokenPrice(3)
        root = contract.getMerkleRoot(3)
        [recp, amt] = contract.royaltyInfo(3, Wei("1 ether"))
        uri = contract.uri(3)
        assert [3, supply, status, allowance, price, uri, root, recp, amt*10000/Wei("1 ether")] == token3

    def test_mint_not_open(self, contract):
        with brownie.reverts("ERC1155TLCore: Mint not open"):
            contract.mint(3, 1, [], {"from": a[4]})

    def test_mint_more_than_allowed(self, contract, admin):
        contract.setMintStatus(3, True, {"from": admin})
        with brownie.reverts("ERC1155TLCore: Cannot mint more than allowed"):
            contract.mint(3, 5, [], {"from": a[4]})

    def test_mint_multi(self, contract):
        contract.mint(3, 2, [], {"from": a[4]})
        contract.mint(3, 2, [], {"from": a[5]})
        contract.mint(3, 2, [], {"from": a[6]})
        assert contract.balanceOf(a[4].address, 3) == 2 and contract.balanceOf(a[5].address, 3) == 2 and contract.balanceOf(a[6].address, 3) == 2

    def test_mint_single(self, contract):
        contract.mint(3, 1, [], {"from": a[7]})
        contract.mint(3, 1, [], {"from": a[8]})
        contract.mint(3, 1, [], {"from": a[9]})
        assert contract.balanceOf(a[7].address, 3) == 1 and contract.balanceOf(a[8].address, 3) == 1 and contract.balanceOf(a[9].address, 3) == 1

    def test_mint_again(self, contract):
        contract.mint(3, 1, [], {"from": a[7]})
        assert contract.balanceOf(a[7].address, 3) == 2 and contract.getNumMinted(3, a[7].address) == 2

    def test_mint_no_supply(self, contract):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.mint(3, 1, [], {"from": a[7]})

    def test_airdrop_no_supply(self, contract, admin):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.airdrop(3, [a[4].address]*3, {"from": admin})

    def test_owner_mint_no_supply(self, contract, admin):
        with brownie.reverts("ERC1155TLCore: Not enough token supply available"):
            contract.ownerMint(3, 3, {"from": admin})

class Test_Reentrancy:
    def test_create_token(self, contract, admin, token2):
        t = token2
        t[6] = Web3.toHex(b'')
        contract.createToken(*t, {"from": admin})
        supply = contract.getTokenSupply(2)
        allowance = contract.getMintAllowance(2)
        status = contract.getMintStatus(2)
        price = contract.getTokenPrice(2)
        root = contract.getMerkleRoot(2)
        [recp, amt] = contract.royaltyInfo(2, Wei("1 ether"))
        uri = contract.uri(2)
        assert [2, supply, status, allowance, price, uri, root, recp, amt*10000/Wei("1 ether")] == token2

    def test_airdrop(self, contract, admin):
        reenter = ERC1155TLCoreAirdropReentrancy.deploy(contract.address, 2, {"from": a[4]})
        with brownie.reverts("ERC1155TLCore: Address not admin or owner"):
            contract.airdrop(2, [reenter.address]*3, {"from": admin})\

    def test_mint(self, contract, admin, token2):
        contract.setMintStatus(2, True, {"from": admin})
        reenter = ERC1155TLCoreMintReentrancy.deploy(contract.address, token2[4], 2, {"from": a[4]})
        a[4].transfer(reenter, "5 ether")

        with brownie.reverts("ERC1155TLCore: Cannot mint more than allowed"):
            reenter.mintToken({"from": a[4]})