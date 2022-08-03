from brownie import ERC721ATLCore, ERC20TL, a, Wei
import brownie
import pytest

merkleRoot = "0x1d8c3fe103f58db27a9a8e824b1af9ec98a7fb3434ea37750f6206c0da288903"

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
    return ["ERC721 Test", "TL", royaltyAddr.address, 750, Wei("1 ether"), 15, merkleRoot, admin.address, payout.address]

@pytest.fixture(scope="class")
def contract(owner, args):
    return ERC721ATLCore.deploy(*args, {"from": owner})

@pytest.fixture(scope="class")
def token(owner, contract):
    return ERC20TL.deploy("test", "tst", contract.address, 500, {"from": owner})

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

class TestNonOwnerOrAdminNoAccess:
    revertStr = "ERC721ATLCore: Address not admin or owner"

    def test_set_allowlist_sale(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setAllowlistSaleStatus(True, {"from": a[4]})

    def test_set_public_sale(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setPublicSaleStatus(True, {"from": a[4]})
    
    def test_freeze_metadata(self, contract):
        with brownie.reverts(self.revertStr):
            contract.freezeMetadata({"from": a[4]})

    def test_set_mint_allowance(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setMintAllowance(2, {"from": a[4]})

    def test_set_base_uri(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setBaseURI("test", {"from": a[4]})

    def test_set_royalty_info(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setRoyaltyInfo(a[4].address, 1000, {"from": a[4]})

    def test_withdraw_erc20(self, contract, token):
        with brownie.reverts(self.revertStr):
            contract.withdrawERC20(token.address, token.balanceOf(contract.address), {"from": a[4]})

    def test_withdraw_ether(self, contract):
        with brownie.reverts(self.revertStr):
            contract.withdrawEther(contract.balance(), {"from": a[4]})

class TestNonOwnerNoAccess:
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

class TestAdminAccess:
    def test_set_allowlist_sale_status(self, contract, admin):
        contract.setAllowlistSaleStatus(True, {"from": admin})
        assert contract.allowlistSaleOpen()

    def test_set_public_sale_status(self, contract, admin):
        contract.setPublicSaleStatus(True, {"from": admin})
        assert contract.publicSaleOpen()

    def test_set_mint_allowance(self, contract, admin):
        contract.setMintAllowance(2, {"from": admin})
        assert contract.mintAllowance() == 2

    def test_set_base_uri(self, contract, admin):
        contract.setBaseURI("tests/", {"from": admin})

    def test_set_royalty_info(self, contract, admin):
        contract.setRoyaltyInfo(a[4].address, 1000, {"from": admin})
        [recp, amt] = contract.royaltyInfo(1, Wei("1 ether"))
        assert recp == a[4].address and amt == Wei(f"{1000/10000} ether")

    def test_withdraw_erc20(self, contract, admin, token):
        contract.withdrawERC20(token.address, token.balanceOf(contract.address), {"from": admin})

    def test_withdraw_ether(self, contract, admin):
        contract.withdrawEther(contract.balance(), {"from": admin})

    def test_freeze_metadata(self, contract, admin):
        contract.freezeMetadata({"from": admin})
        assert contract.frozen()

class TestOwnerAccess:
    def test_set_allowlist_sale_status(self, contract, owner):
        contract.setAllowlistSaleStatus(True, {"from": owner})
        assert contract.allowlistSaleOpen()

    def test_set_public_sale_status(self, contract, owner):
        contract.setPublicSaleStatus(True, {"from": owner})
        assert contract.publicSaleOpen()

    def test_set_mint_allowance(self, contract, owner):
        contract.setMintAllowance(2, {"from": owner})
        assert contract.mintAllowance() == 2

    def test_set_base_uri(self, contract, owner):
        contract.setBaseURI("test/", {"from": owner})

    def test_set_royalty_info(self, contract, owner):
        contract.setRoyaltyInfo(a[4].address, 1000, {"from": owner})
        [recp, amt] = contract.royaltyInfo(1, Wei("1 ether"))
        assert recp == a[4].address and amt == Wei(f"{1000/10000} ether")

    def test_withdraw_erc20(self, contract, owner, token):
        contract.withdrawERC20(token.address, token.balanceOf(contract.address), {"from": owner})

    def test_withdraw_ether(self, contract, owner):
        contract.withdrawEther(contract.balance(), {"from": owner})

    def test_freeze_metadata(self, contract, owner):
        contract.freezeMetadata({"from": owner})
        assert contract.frozen()

    def test_set_admin_address(self, contract, owner):
        contract.setAdminAddress(a[4].address, {"from": owner})
        assert contract.adminAddress() == a[4].address

    def test_set_payout_address(self, contract, owner):
        contract.setPayoutAddress(a[4].address, {"from": owner})
        assert contract.payoutAddress() == a[4].address