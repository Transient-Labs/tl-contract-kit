from brownie import ERC721ATLMerkle, ERC721ATLCoreMintReentrancy, a, Wei
import brownie
import pytest

# setup
# allowlist --> accounts 4 through 6
# public --> accounts 7 thorugh 9
# run `node utils/ERC721TLCore.merkleTree.js` to get
merkleRoot = "0x1d8c3fe103f58db27a9a8e824b1af9ec98a7fb3434ea37750f6206c0da288903"
merkleProofs = [
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
]

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
def args(admin, payout, royaltyAddr):
    return ["ERC721A Test", "TL", royaltyAddr.address, 750, Wei("1 ether"), 20, merkleRoot, admin.address, payout.address]

@pytest.fixture(scope="class")
def contract(owner, args):
    return ERC721ATLMerkle.deploy(*args, {"from": owner})

class TestInterface:

    def test_erc721_interface(self, contract):
        assert contract.supportsInterface("0x80ac58cd")

    def test_eip2981_interface(self, contract):
        assert contract.supportsInterface("0x2a55205a")

    def test_erc165_interface(self, contract):
        assert contract.supportsInterface("0x01ffc9a7")

    def test_erc721_metadata_interface(self, contract):
        assert contract.supportsInterface("0x5b5e139f")

class TestSetup:
    def test_name(self, contract, args):
        assert contract.name() == args[0]

    def test_symbol(self, contract, args):
        assert contract.symbol() == args[1]

    def test_royalty_config(self, contract, args):
        [recp, amt] = contract.royaltyInfo(1, Wei("1 ether"))
        assert recp == args[2] and amt == Wei(f"{args[3]/10000} ether")

    def test_mint_price(self, contract, args):
        assert contract.mintPrice() == args[4]
    
    def test_merkle_root(self, contract, args):
        assert contract.allowlistMerkleRoot() == args[6]
    
    def test_admin(self, contract, args):
        assert contract.adminAddress() == args[7]

    def test_payout(self, contract, args):
        assert contract.payoutAddress() == args[8]

    def test_owner(self, contract, owner):
        assert contract.owner() == owner.address

class Test_View_Functions:
    def test_num_minted_init(self, contract, owner):
        assert contract.getNumMinted(owner.address) == 0

    def test_remaining_supply_init(self, contract, args):
        assert contract.getRemainingSupply() == args[5]
    
    def test_remaining_supply(self, contract, owner, args):
        contract.ownerMint(5, {"from": owner})
        assert contract.getRemainingSupply() == args[5] - 5

class TestNonOwnerOrAdminNoAccess:
    revertStr = "ERC721ATLCore: Address not admin or owner"

    def test_open_allowlist_sale(self, contract):
        with brownie.reverts(self.revertStr):
            contract.openAllowlistSale({"from": a[4]})

    def test_open_public_sale(self, contract):
        with brownie.reverts(self.revertStr):
            contract.openPublicSale({"from": a[4]})

    def test_close_sales(self, contract):
        with brownie.reverts(self.revertStr):
            contract.closeSales({"from": a[4]})

    def test_set_merkle_root(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setAllowlistMerkleRoot(bytes(32), {"from": a[4]})

    def test_set_mint_price(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setMintPrice(0, {"from": a[4]})

    def test_set_mint_allowance(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setMintAllowance(2, {"from": a[4]})

    def test_set_base_uri(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setBaseURI("test", {"from": a[4]})

    def test_airdrop(self, contract):
        with brownie.reverts(self.revertStr):
            contract.airdrop([a[4]]*3, {"from": a[4]})

    def test_owner_mint(self, contract):
        with brownie.reverts(self.revertStr):
            contract.ownerMint(2, {"from": a[4]})

class TestAdminAccess:
    def test_open_allowlist_sale(self, contract, admin):
        contract.openAllowlistSale({"from": admin})
        assert contract.allowlistSaleOpen() and not contract.publicSaleOpen()

    def test_open_public_sale_(self, contract, admin):
        contract.openPublicSale({"from": admin})
        assert contract.publicSaleOpen() and not contract.allowlistSaleOpen()

    def test_close_sales(self, contract, admin):
        contract.closeSales({"from": admin})
        assert not contract.publicSaleOpen() and not contract.allowlistSaleOpen()

    def test_set_merkle_root(self, contract, admin):
        contract.setAllowlistMerkleRoot(bytes(32), {"from": admin})
        assert contract.allowlistMerkleRoot() == f"0x{bytes(32).hex()}"
    
    def test_set_mint_price(self, contract, admin):
        contract.setMintPrice(0, {"from": admin})
        assert contract.mintPrice() == 0

    def test_set_mint_allowance(self, contract, admin):
        contract.setMintAllowance(2, {"from": admin})
        assert contract.mintAllowance() == 2

    def test_airdrop(self, contract, admin):
        contract.airdrop([admin.address]*2, {"from": admin})
        assert contract.balanceOf(admin.address) == 2

    def test_owner_mint(self, contract, admin, owner):
        contract.ownerMint(2, {"from": admin})
        assert contract.balanceOf(owner.address) == 2

    def test_set_base_uri(self, contract, admin):
        contract.setBaseURI("tests/", {"from": admin})
        assert contract.tokenURI(1) == "tests/1"

class TestOwnerAccess:
    def test_open_allowlist_sale(self, contract, owner):
        contract.openAllowlistSale({"from": owner})
        assert contract.allowlistSaleOpen() and not contract.publicSaleOpen()

    def test_open_public_sale_(self, contract, owner):
        contract.openPublicSale({"from": owner})
        assert contract.publicSaleOpen() and not contract.allowlistSaleOpen()

    def test_close_sales(self, contract, owner):
        contract.closeSales({"from": owner})
        assert not contract.publicSaleOpen() and not contract.allowlistSaleOpen()

    def test_set_merkle_root(self, contract, owner):
        contract.setAllowlistMerkleRoot(bytes(32), {"from": owner})
        assert contract.allowlistMerkleRoot() == f"0x{bytes(32).hex()}"
    
    def test_set_mint_price(self, contract, owner):
        contract.setMintPrice(0, {"from": owner})
        assert contract.mintPrice() == 0

    def test_set_mint_allowance(self, contract, owner):
        contract.setMintAllowance(2, {"from": owner})
        assert contract.mintAllowance() == 2

    def test_airdrop(self, contract, admin, owner):
        contract.airdrop([admin.address]*2, {"from": owner})
        assert contract.balanceOf(admin.address) == 2

    def test_owner_mint(self, contract, owner):
        contract.ownerMint(2, {"from": owner})
        assert contract.balanceOf(owner.address) == 2

    def test_set_base_uri(self, contract, owner):
        contract.setBaseURI("test/", {"from": owner})
        assert contract.tokenURI(1) == "test/1"

class TestMint:

    def test_setup(self, contract, admin):
        contract.setMintAllowance(1, {"from": admin})

    def test_mint_not_enough_ether(self, contract):
        with brownie.reverts("ERC721ATLMerkle: Not enough ether attached to the transaction"):
            contract.mint(2, merkleProofs[0], {"from": a[4], "value": Wei("0.99 ether")})

    def test_mint_closed(self, contract):
        with brownie.reverts("ERC721ATLMerkle: Mint not open"):
            contract.mint(1, merkleProofs[0], {"from": a[4], "value": Wei("1 ether")})

    def test_zero_mint(self, contract):
        with brownie.reverts():
            contract.mint(1, merkleProofs[0], {"from": a[4], "value": Wei("1 ether")})

    def test_allowlist_sale(self, contract, admin):
        contract.openAllowlistSale({"from": admin})
        contract.mint(1, merkleProofs[0], {"from": a[4], "value": Wei("1 ether")})
        contract.mint(1, merkleProofs[1], {"from": a[5], "value": Wei("1 ether")})
        contract.mint(1, merkleProofs[2], {"from": a[6], "value": Wei("1 ether")})
        assert contract.ownerOf(1) == a[4].address and contract.ownerOf(2) == a[5].address and contract.ownerOf(3) == a[6].address

    def test_transfer_and_mint_again(self, contract):
        contract.safeTransferFrom(a[4].address, a[9].address, 1, {"from": a[4]})
        with brownie.reverts("ERC721ATLMerkle: Mint allowance reached"):
            contract.mint(1, merkleProofs[0], {"from": a[4], "value": Wei("1 ether")})

    def test_allowlist_mint_allowance_reached(self, contract):
        with brownie.reverts("ERC721ATLMerkle: Mint allowance reached"):
            contract.mint(1, merkleProofs[0], {"from": a[4], "value": Wei("1 ether")})
        with brownie.reverts("ERC721ATLMerkle: Mint allowance reached"):
            contract.mint(1, merkleProofs[1], {"from": a[5], "value": Wei("1 ether")})
        with brownie.reverts("ERC721ATLMerkle: Mint allowance reached"):
            contract.mint(1, merkleProofs[2], {"from": a[6], "value": Wei("1 ether")})
    
    def test_allowlist_mint_not_on_allowlist(self, contract):
        with brownie.reverts("ERC721ATLMerkle: Not on allowlist"):
            contract.mint(1, merkleProofs[0], {"from": a[7], "value": Wei("1 ether")})

    def test_public_sale(self, contract, admin):
        contract.openPublicSale({"from": admin})
        contract.mint(1, [], {"from": a[7], "value": Wei("1 ether")})
        contract.mint(1, [], {"from": a[8], "value": Wei("1 ether")})
        contract.mint(1, [], {"from": a[9], "value": Wei("1 ether")})
        assert contract.ownerOf(4) == a[7].address and contract.ownerOf(5) == a[8].address and contract.ownerOf(6) == a[9].address

    def test_public_sale_mint_allowance_reached(self, contract):
        with brownie.reverts("ERC721ATLMerkle: Mint allowance reached"):
            contract.mint(1, [], {"from": a[7], "value": Wei("1 ether")})
        with brownie.reverts("ERC721ATLMerkle: Mint allowance reached"):
            contract.mint(1, [], {"from": a[8], "value": Wei("1 ether")})
        with brownie.reverts("ERC721ATLMerkle: Mint allowance reached"):
            contract.mint(1, [], {"from": a[9], "value": Wei("1 ether")})

    def test_mint_again(self, contract, admin):
        contract.setMintAllowance(3, {"from": admin})
        contract.mint(2, merkleProofs[0], {"from": a[4], "value": Wei("2 ether")})
        contract.mint(2, merkleProofs[1], {"from": a[5], "value": Wei("2 ether")})
        contract.mint(2, merkleProofs[2], {"from": a[6], "value": Wei("2 ether")})
        contract.mint(2, [], {"from": a[7], "value": Wei("2 ether")})
        contract.mint(2, [], {"from": a[8], "value": Wei("2 ether")})
        contract.mint(2, [], {"from": a[9], "value": Wei("2 ether")})
        assert contract.ownerOf(7) == a[4].address and contract.ownerOf(8) == a[4].address \
            and contract.ownerOf(9) == a[5].address and contract.ownerOf(10) == a[5].address \
            and contract.ownerOf(11) == a[6].address and contract.ownerOf(12) == a[6].address \
            and contract.ownerOf(13) == a[7].address and contract.ownerOf(14) == a[7].address \
            and contract.ownerOf(15) == a[8].address and contract.ownerOf(16) == a[8].address \
            and contract.ownerOf(17) == a[9].address and contract.ownerOf(18) == a[9].address

    def test_num_minted(self, contract):
        assert contract.getNumMinted(a[4].address) == 3 and contract.getNumMinted(a[5].address) == 3 and contract.getNumMinted(a[6].address) == 3 \
            and contract.getNumMinted(a[7].address) == 3 and contract.getNumMinted(a[8].address) == 3 and contract.getNumMinted(a[9].address) == 3

    def test_contract_interaction(self, contract, admin):
        reenter = ERC721ATLCoreMintReentrancy.deploy(contract.address, Wei("1 ether"), {"from": a[9]})
        a[9].transfer(reenter.address, "2 ether")
        with brownie.reverts("ReentrancyGuard: reentrant call"):
            reenter.mintToken()

    def test_max_supply_reached(self, contract, admin):
        contract.setMintAllowance(5, {"from": admin})
        contract.mint(2, [], {"from": a[4], "value": Wei("2 ether")})
        with brownie.reverts("ERC721ATLMerkle: No token supply left"):
            contract.mint(1, [], {"from": a[5], "value": Wei("1 ether")})

    def test_withdraw_ether(self, contract, admin, payout):
        init_balance = payout.balance()
        contract_balance = contract.balance()
        contract.withdrawEther(contract.balance(), {"from": admin})
        assert payout.balance() - init_balance == contract_balance

class TestAirdrop:

    def test_airdrop(self, contract, admin):
        contract.airdrop([a[4].address, a[5].address, a[6].address], {"from": admin})
        assert contract.ownerOf(1) == a[4].address and contract.ownerOf(2) == a[5].address and contract.ownerOf(3) == a[6].address

class TestOwnerMint:

    def test_owner_mint(self, contract, admin, owner):
        contract.ownerMint(5, {"from": admin})
        assert contract.ownerOf(1) == owner.address and contract.ownerOf(2) == owner.address and contract.ownerOf(3) == owner.address \
            and contract.ownerOf(4) == owner.address and contract.ownerOf(5) == owner.address

class TestTokenSupplyReached:

    def test_owner_mint(self, contract, admin):
        contract.ownerMint(20, {"from": admin})
        assert contract.getRemainingSupply() == 0
    
    def test_airdrop_no_supply(self, contract, admin):
        with brownie.reverts("ERC721ATLMerkle: No token supply left"):
            contract.airdrop([a[4].address]*3, {"from": admin})

    def test_owner_mint_no_supply(self, contract, admin):
        with brownie.reverts("ERC721ATLMerkle: No token supply left"):
            contract.ownerMint(5, {"from": admin})

    def test_mint_no_supply(self, contract):
        with brownie.reverts("ERC721ATLMerkle: No token supply left"):
            contract.mint(1, [], {"from": a[4]})
    