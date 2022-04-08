const { expect } = require("chai");
const { ethers } = require("hardhat");
const keccak256 = require("keccak256");
const { MerkleTree } = require("merkletreejs");


describe("ERC721 TL Core", function() {
    let contract;
    let owner;
    let admin;
    let payout;
    let royaltyRecp;
    let a;

    let args;
    let merkleRoot;

    let merkleProofs = [];

    before(async function() {

        [owner, admin, payout, royaltyRecp, ...a] = await ethers.getSigners();
        const allowlistAddr = [];
        a.slice(0, 10).forEach((addr) => {
            allowlistAddr.push(addr.address);
        });
        const leafNodes = allowlistAddr.map(addr => keccak256(addr));
        const merkleTree = new MerkleTree(leafNodes, keccak256, { sortPairs: true});
        merkleRoot = merkleTree.getHexRoot();
        allowlistAddr.forEach((addr) => {
            merkleProofs.push(merkleTree.getHexProof(keccak256(addr)));
        });

        args = {
            name: "ERC721 Test",
            symbol: "TL",
            royaltyRecipient: royaltyRecp.address,
            royaltyPercentage: 750,
            price: ethers.utils.parseEther("1"),
            supply: 60,
            merkleRoot: merkleRoot,
            admin: admin.address,
            payout: payout.address
        }

        let spreadArgs = Object.keys(args).map(key => {return(args[key])});

        let Contract = await ethers.getContractFactory("ERC721TLCore", owner);
        contract = await Contract.deploy(...spreadArgs);
        await contract.deployed();
    });

    describe("General", async function() {
        it("Should pass initial setup from constructor", async function() {
            expect(await contract.name()).to.equal(args.name);
            expect(await contract.symbol()).to.equal(args.symbol);
            let recp;
            let amt;
            [recp, amt] = await contract.royaltyInfo(1, ethers.utils.parseEther("1"));
            expect(recp).to.equal(args.royaltyRecipient);
            expect(ethers.utils.formatEther(amt)).to.equal((1*0.075).toString());
            expect(await contract.mintPrice()).to.equal(args.price);
            expect(await contract.totalSupply()).to.equal(args.supply);
            expect(await contract.allowlistMerkleRoot()).to.equal(args.merkleRoot);
            expect(await contract.adminAddress()).to.equal(args.admin);
            expect(await contract.payoutAddress()).to.equal(args.payout);
        });

        it("Should get number minted", async function () {
            expect(await contract.getNumMinted(a[0].address)).to.equal(0);
        });
    });

    describe("Access Control", async function () {
        it("Should fail when tx sender is not the owner or admin", async function() {
            let revertString = "ERC721TLCore: Address not admin or owner";
            contract = contract.connect(a[0]);

            await expect(
                contract.setAllowlistSaleStatus(true)
            ).to.be.revertedWith(revertString);

            await expect(
                contract.setPublicSaleStatus(true)
            ).to.be.revertedWith(revertString);

            await expect(
                contract.freezeMetadata()
            ).to.be.revertedWith(revertString);

            await expect(
                contract.setMintAllowance(2)
            ).to.be.revertedWith(revertString);

            await expect(
                contract.setBaseURI(true)
            ).to.be.revertedWith(revertString);

            await expect(
                contract.setRoyaltyInfo(a[1].address, 1000)
            ).to.be.revertedWith(revertString);

            await expect(
                contract.airdrop([a[0].address, a[1].address, a[2].address])
            ).to.be.revertedWith(revertString);

            await expect(
                contract.ownerMint(5)
            ).to.be.revertedWith(revertString);

            await expect(
                contract.withdrawEther()
            ).to.be.revertedWith(revertString);

            contract = contract.connect(owner);
        });

        it("Should fail for only owner functions", async function() {
            let revertString = "Ownable: caller is not the owner";
            contract = contract.connect(a[0]);

            await expect(
                contract.setNewAdmin(a[0].address)
            ).to.be.revertedWith(revertString);

            await expect(
                contract.setPayoutAddress(a[0].address)
            ).to.be.revertedWith(revertString);

            contract = contract.connect(owner);
        });


        it("Should not allow the admin to access", async function() {
            let revertString = "Ownable: caller is not the owner";
            contract = contract.connect(admin);

            await expect(
                contract.setNewAdmin(admin.address)
            ).to.be.revertedWith(revertString);

            await expect(
                contract.setPayoutAddress(admin.address)
            ).to.be.revertedWith(revertString);

            contract = contract.connect(owner);
        });

        it("Should allow the admin to access", async function() {
            contract = contract.connect(admin);

            await contract.setAllowlistSaleStatus(true);
            expect(await contract.allowlistSaleOpen()).to.be.true;

            await contract.setPublicSaleStatus(true);
            expect(await contract.publicSaleOpen()).to.be.true;

            await contract.setMintAllowance(2);
            expect(await contract.mintAllowance()).to.equal(2);

            // will freeze metadata later

            await contract.setBaseURI("test/");
            // will verify after minting

            await contract.setRoyaltyInfo(a[0].address, 1000);
            let recp;
            let amt;
            [recp, amt] = await contract.royaltyInfo(1, ethers.utils.parseEther("1"));
            expect(recp).to.equal(a[0].address);
            expect(ethers.utils.formatEther(amt)).to.equal((1*0.1).toString());

            await contract.airdrop(a.slice(0,15).map(addr => {return addr.address}));
            a.slice(0,15).forEach(async (item) => {
                expect(await contract.balanceOf(item.address)).to.equal(1);
            });

            await contract.ownerMint(5);
            expect(await contract.balanceOf(owner.address)).to.equal(5);

            expect(await contract.tokenURI(1)).to.equal("test/1");

            contract = contract.connect(owner);
        });

        it("Should allow the owner to access", async function() {

            await contract.setAllowlistSaleStatus(false);
            expect(await contract.allowlistSaleOpen()).to.be.false;

            await contract.setPublicSaleStatus(false);
            expect(await contract.publicSaleOpen()).to.be.false;

            await contract.setMintAllowance(1);
            expect(await contract.mintAllowance()).to.equal(1);

            // will freeze metadata later

            await contract.setBaseURI("tests/");
            // will verify after minting

            await contract.setRoyaltyInfo(royaltyRecp.address, 750);
            let recp;
            let amt;
            [recp, amt] = await contract.royaltyInfo(1, ethers.utils.parseEther("1"));
            expect(recp).to.equal(royaltyRecp.address);
            expect(ethers.utils.formatEther(amt)).to.equal((1*0.075).toString());

            await contract.airdrop(a.slice(0,15).map(addr => {return addr.address}));
            a.slice(0,15).forEach(async (item) => {
                expect(await contract.balanceOf(item.address)).to.equal(2);
            });

            await contract.ownerMint(5);
            expect(await contract.balanceOf(owner.address)).to.equal(10);

            expect(await contract.tokenURI(1)).to.equal("tests/1");
        });

        it("Should allow admin or owner to freeze", async function() {
            contract = contract.connect(admin);
            await contract.freezeMetadata();
            expect(await contract.frozen()).to.be.true;
            contract = contract.connect(owner);

            await contract.freezeMetadata();
            expect(await contract.frozen()).to.be.true;
        });

        it("Should allow only the owner to change addresses", async function() {
            await contract.setNewAdmin(a[0].address);
            expect(await contract.adminAddress()).to.equal(a[0].address);

            await contract.setPayoutAddress(a[0].address);
            expect(await contract.payoutAddress()).to.equal(a[0].address);

            // set it back to what it should be
            await contract.setNewAdmin(admin.address);
            await contract.setPayoutAddress(payout.address);
        });
    });

    describe("Token Interaction", async function() {
        it("Should not allow anyone to mint", async function() {
            let zip = a.slice(0, 10).map((e, i) => {
                return [e, merkleProofs[i]];
            });
            zip.forEach(async item => {
                contract = contract.connect(item[0]);
                await expect(
                    contract.mint(item[1], {value: ethers.utils.parseEther("1")})
                ).to.be.revertedWith("ERC721TLCore: Mint not open");
            });
            a.slice(10,15).forEach(async addr => {
                contract = contract.connect(addr);
                await expect(
                    contract.mint([], {value: ethers.utils.parseEther("1")})
                ).to.be.revertedWith("ERC721TLCore: Mint not open");
            });
        });

        it("Should revert with no value attached", async function() {
            let zip = a.slice(0, 10).map((e, i) => {
                return [e, merkleProofs[i]];
            });
            zip.forEach(async item => {
                contract = contract.connect(item[0]);
                await expect(
                    contract.mint(item[1])
                ).to.be.revertedWith("ERC721TLCore: Not enough ether attached to the transaction");
            });
        });

        it("Should allow addresses on the allowlist to mint once", async function() {
            contract = contract.connect(owner);
            await contract.setAllowlistSaleStatus(true);
            let zip = a.slice(0, 10).map((e, i) => {
                return [e, merkleProofs[i]];
            });
            zip.forEach(async item => {
                contract = contract.connect(item[0]);
                await contract.mint(item[1], {value: ethers.utils.parseEther("1")});
                expect(await contract.balanceOf(item[0].address)).to.equal(3);
            });
        });

        it("Should not allow addresses on the allowlist to mint twice with mint allowance at one", async function() {
            let zip = a.slice(0, 10).map((e, i) => {
                return [e, merkleProofs[i]];
            });
            zip.forEach(async item => {
                contract = contract.connect(item[0]);
                await expect(
                    contract.mint(item[1])
                ).to.be.revertedWith("ERC721TLCore: Mint allowance reached");
            });
        });

        it("Should not allow public minters to mint", async function() {
            a.slice(10,15).forEach(async addr => {
                contract = contract.connect(addr);
                await expect(
                    contract.mint([], {value: ethers.utils.parseEther("1")})
                ).to.be.revertedWith("ERC721TLCore: Not on allowlist");
            });
        });

        it("Should allow public minters to mint once", async function() {
            contract = contract.connect(owner);
            await contract.setAllowlistSaleStatus(false);
            await contract.setPublicSaleStatus(true);
            a.slice(10,15).forEach(async addr => {
                contract = contract.connect(addr);
                await contract.mint([], {value: ethers.utils.parseEther("1")});
                expect(await contract.balanceOf(addr.address)).to.equal(3);
            });
        });

        it("Should not allow public minters to mint twice with mint allowance at one", async function() {
            a.slice(10,15).forEach(async addr => {
                contract = contract.connect(addr);
                await expect(
                    contract.mint([], {value: ethers.utils.parseEther("1")})
                ).to.be.revertedWith("ERC721TLCore: Mint allowance reached");
            });
        });

        it("Should not allow reentrancy", async function() {
            let AirdropReenter = await ethers.getContractFactory("ERC721TLCoreAirdropReentrancy", a[15]);
            let maliciousAirdropReceiver = await AirdropReenter.deploy(contract.address);
            await maliciousAirdropReceiver.deployed();

            await expect(
                contract.airdrop([maliciousAirdropReceiver.address])
            ).to.be.revertedWith("ERC721TLCore: Address not admin or owner");

            let MintReenter = await ethers.getContractFactory("ERC721TLCoreMintReentrancy", a[15]);
            let maliciousMintReceiver = await MintReenter.deploy(contract.address, ethers.utils.parseEther("1"));
            await maliciousMintReceiver.deployed();
            
            await a[15].sendTransaction({to: maliciousMintReceiver.address, value: ethers.utils.parseEther("2")});
            await expect(
                maliciousMintReceiver.mintToken()
            ).to.be.revertedWith("ERC721TLCore: Mint allowance reached");
        });

        it("Should allow all minters to mint again", async function() {
            contract.setMintAllowance(2);
            a.slice(0, 15).forEach(async addr => {
                contract = contract.connect(addr);
                await contract.mint([], {value: ethers.utils.parseEther("1")});
                expect(await contract.balanceOf(addr.address)).to.equal(4);
            });
        });

        it("Should not allow minters to mint again", async function() {
            a.slice(0, 15).forEach(async addr => {
                contract = contract.connect(addr);
                await expect(
                    contract.mint([], {value: ethers.utils.parseEther("1")})
                ).to.be.revertedWith("ERC721TLCore: Mint allowance reached");
            });

            contract = contract.connect(owner);

            expect(await contract.getRemainingSupply()).to.equal(5);
        });

        it("Should run out of tokens", async function() {
            contract = contract.connect(owner);
            await contract.ownerMint(5);
            expect(await contract.getRemainingSupply()).to.equal(0);
            contract = contract.connect(a[15]);
            await expect(
                contract.mint([], {value: ethers.utils.parseEther("1")})
            ).to.be.revertedWith("ERC721TLCore: No token supply left");
        })
    });
});
