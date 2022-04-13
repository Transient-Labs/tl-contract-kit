from brownie import ERC721TLCreator, a, Wei
import brownie
import pytest

@pytest.fixture(scope="module")
def owner():
    return a[0]

@pytest.fixture(scope="module")
def admin():
    return a[1]

@pytest.fixture(scope="module")
def royaltyAddr():
    return a[3]

@pytest.fixture(scope="class")
def contract(owner, admin, royaltyAddr):
    return ERC721TLCreator.deploy("CreatorTest", "CT", royaltyAddr.address, 1000, admin.address, {"from": owner})

class Test_Setup:

    def test_name(self, contract):
        assert contract.name() == "CreatorTest"

    def test_symbol(self, contract):
        assert contract.symbol() == "CT"

    def test_royalty_info(self, contract, royaltyAddr):
        [recp, amt] = contract.royaltyInfo(1, "1 ether")
        assert recp == royaltyAddr.address and amt == Wei(f"{1000/10000} ether")

    def test_admin_address(self, contract, admin):
        assert contract.adminAddress() == admin.address
    
    def test_owner(self, contract, owner):
        assert contract.owner() == owner.address

class Test_Non_Owner_Admin_No_Access:
    revertStr = "ERC721TLCreator: Address not admin or owner"

    def test_set_royalty_info(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setRoyaltyInfo(a[4].address, 5000, {"from": a[4]})

    def test_mint(self, contract):
        with brownie.reverts(self.revertStr):
            contract.mint("testMint", {"from": a[4]})    
    
    def test_set_token_uri(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setTokenURI(1, "testsMint", {"from": a[4]})

class Test_Non_Owner_No_Access:
    revertStr = "Ownable: caller is not the owner"

    def test_set_admin_address_user(self, contract):
        with brownie.reverts(self.revertStr):
            contract.setAdminAddress(a[4].address, {"from": a[4]})

    def test_set_admin_address_admin(self, contract, admin):
        with brownie.reverts(self.revertStr):
            contract.setAdminAddress(a[4].address, {"from": admin})

class Test_Admin_Access:
    def test_royalty_info(self, contract, admin):
        contract.setRoyaltyInfo(a[4].address, 700, {"from": admin})
        [recp, amt] = contract.royaltyInfo(1, "1 ether")
        assert recp == a[4].address and amt == Wei(f"{700/10000} ether")

    def test_mint(self, contract, admin):
        contract.mint("tests", {"from": admin})
        assert contract.tokenURI(1) == "tests"

    def test_set_token_uri(self, contract, admin):
        contract.setTokenURI(1, "testtest", {"from": admin})
        assert contract.tokenURI(1) == "testtest"

class Test_Owner_Access:
    def test_royalty_info(self, contract, owner):
        contract.setRoyaltyInfo(a[5].address, 800, {"from": owner})
        [recp, amt] = contract.royaltyInfo(1, "1 ether")
        assert recp == a[5].address and amt == Wei(f"{800/10000} ether")

    def test_mint(self, contract, owner):
        contract.mint("testss", {"from": owner})
        assert contract.tokenURI(1) == "testss"

    def test_set_token_uri(self, contract, owner):
        contract.setTokenURI(1, "teststests", {"from": owner})
        assert contract.tokenURI(1) == "teststests"

    def test_burn(self, contract, owner):
        contract.burn(1, {"from": owner})
        with brownie.reverts("ERC721TLCreator: URI query for nonexistent token"):
            contract.tokenURI(1)

    def test_set_admin_address(self, contract, owner):
        contract.setAdminAddress(a[4].address, {"from": owner})
        assert contract.adminAddress() == a[4].address

class Test_Reverts:
    def test_set_royalty_info(self, contract, admin):
        with brownie.reverts("ERC721TLCreator: Cannot set royalty percentage above 10000"):
            contract.setRoyaltyInfo(a[4].address, 10000, {"from": admin})

    def test_set_token_uri(self, contract, admin):
        with brownie.reverts("ERC721TLCreator: URI set of nonexistent token"):
            contract.setTokenURI(1, "test", {"from": admin})

    def test_set_token_uri(self, contract):
        with brownie.reverts("ERC721TLCreator: URI query for nonexistent token"):
            contract.tokenURI(1)

class Test_Token:
    def test_mint_many(self, contract, admin):
        for i in range(1,4):
            contract.mint(f"token/{i}", {"from": admin})
        assert contract.tokenURI(1) == "token/1" and contract.tokenURI(2) == "token/2" and contract.tokenURI(3) == "token/3"
