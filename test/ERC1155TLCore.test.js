const { expect } = require("chai");
const { ethers } = require("hardhat");
const BN = ethers.BigNumber;
const keccak256 = require("keccak256");
const { MerkleTree } = require("merkletreejs");

describe("ERC-1155 TL Core", function() {
    // 4 tokens to be tested
    // 0 - airdrop only
    // 1 - mint only
    // 3 - airdrop + mint
    // 4 - free claim
    let contract;
    let owner;
    let admin;
    let payout;
    let royaltyRecp1;
    let royaltyRecp2;
    let royaltyRecp3;
    let royaltyRecp4;
    let a;
    let args;
    let allowlistAddr2 = [];
    let allowlistAddr3 = [];
    let merkleRoot2;
    let merkleRoot3;
    let merkleProofs2 = [];
    let merkleProofs3 = [];
    let token1;
    let token2;
    let token3;
    let token4;

    before(async function() {

        [owner, admin, payout, royaltyRecp1, royaltyRecp2, royaltyRecp3, royaltyRecp4, ...a] = await ethers.getSigners();
        a.slice(0, 5).forEach((addr) => {
            allowlistAddr2.push(addr.address);
        });
        const leafNodes2 = allowlistAddr2.map(addr => keccak256(addr));
        const merkleTree2 = new MerkleTree(leafNodes2, keccak256, { sortPairs: true});
        merkleRoot2 = merkleTree2.getHexRoot();
        allowlistAddr2.forEach((addr) => {
            merkleProofs2.push(merkleTree2.getHexProof(keccak256(addr)));
        });

        a.slice(5, 10).forEach((addr) => {
            allowlistAddr3.push(addr.address);
        });
        const leafNodes3 = allowlistAddr3.map(addr => keccak256(addr));
        const merkleTree3 = new MerkleTree(leafNodes3, keccak256, { sortPairs: true});
        merkleRoot3 = merkleTree3.getHexRoot();
        allowlistAddr3.forEach((addr) => {
            merkleProofs3.push(merkleTree3.getHexProof(keccak256(addr)));
        });

        token1 = [0, 20, false, 1, 0, "test1/", ethers.utils.formatBytes32String(""), royaltyRecp1.address, 500];
        token2 = [1, 30, false, 1, ethers.utils.parseEther("1"), "test2/", merkleRoot2, royaltyRecp2.address, 750];
        token3 = [2, 40, false, 1, ethers.utils.parseEther("0.5"), "test3/", merkleRoot3, royaltyRecp3.address, 1000];
        token4 = [3, 20, false, 1, 0, "test4/", ethers.utils.formatBytes32String(""), royaltyRecp4.address, 1250];

        args = {
            admin: admin.address,
            payout: payout.address,
            name: "ERC1155 Test"
        }

        let spreadArgs = Object.keys(args).map(key => {return(args[key])});

        let Contract = await ethers.getContractFactory("ERC1155TLCore", owner);
        contract = await Contract.deploy(...spreadArgs);
        await contract.deployed();
    });

    describe("Setup", async function() {
        it("Should be setup properly after deployment", async function() {
            expect(await contract.adminAddress()).to.equal(admin.address);
            expect(await contract.payoutAddress()).to.equal(payout.address);
            expect(await contract.name()).to.equal(args.name);
        });

        it("Should allow admin to create tokens", async function() {
            // Token 1
            await contract.connect(admin).createToken(...token1);
            expect(await contract.getTokenSupply(0)).to.equal(token1[1]);
            expect(await contract.getMintStatus(0)).to.equal(token1[2]);
            expect(await contract.getMintAllowance(0)).to.equal(token1[3]);
            expect(await contract.getTokenPrice(0)).to.equal(BN.from(token1[4]));
            expect(await contract.uri(0)).to.equal(token1[5]);
            expect(await contract.getMerkleRoot(0)).to.equal(token1[6]);
            let recp1, amt1;
            [recp1, amt1] = await contract.royaltyInfo(0, ethers.utils.parseEther("1"));
            expect(recp1).to.equal(token1[7]);
            expect(amt1).to.equal(ethers.utils.parseEther((1*token1[8]/10000).toString()));
            expect(await contract.getNumMinted(0, a[0].address)).to.equal(0);

            // Token 2
            await contract.connect(admin).createToken(...token2);
            expect(await contract.getTokenSupply(1)).to.equal(token2[1]);
            expect(await contract.getMintStatus(1)).to.equal(token2[2]);
            expect(await contract.getMintAllowance(1)).to.equal(token2[3]);
            expect(await contract.getTokenPrice(1)).to.equal(BN.from(token2[4]));
            expect(await contract.uri(1)).to.equal(token2[5]);
            expect(await contract.getMerkleRoot(1)).to.equal(token2[6]);
            let recp2, amt2;
            [recp2, amt2] = await contract.royaltyInfo(1, ethers.utils.parseEther("1"));
            expect(recp2).to.equal(token2[7]);
            expect(amt2).to.equal(ethers.utils.parseEther((1*token2[8]/10000).toString()));
            expect(await contract.getNumMinted(1, a[0].address)).to.equal(0);
        });

        it("Should allow owner to create tokens", async function() {
            // Token 1
            await contract.createToken(...token3);
            expect(await contract.getTokenSupply(2)).to.equal(token3[1]);
            expect(await contract.getMintStatus(2)).to.equal(token3[2]);
            expect(await contract.getMintAllowance(2)).to.equal(token3[3]);
            expect(await contract.getTokenPrice(2)).to.equal(BN.from(token3[4]));
            expect(await contract.uri(2)).to.equal(token3[5]);
            expect(await contract.getMerkleRoot(2)).to.equal(token3[6]);
            let recp3, amt3;
            [recp3, amt3] = await contract.royaltyInfo(2, ethers.utils.parseEther("1"));
            expect(recp3).to.equal(token3[7]);
            expect(amt3).to.equal(ethers.utils.parseEther((1*token3[8]/10000).toString()));
            expect(await contract.getNumMinted(2, a[0].address)).to.equal(0);

            // Token 2
            await contract.createToken(...token4);
            expect(await contract.getTokenSupply(3)).to.equal(token4[1]);
            expect(await contract.getMintStatus(3)).to.equal(token4[2]);
            expect(await contract.getMintAllowance(3)).to.equal(token4[3]);
            expect(await contract.getTokenPrice(3)).to.equal(BN.from(token4[4]));
            expect(await contract.uri(3)).to.equal(token4[5]);
            expect(await contract.getMerkleRoot(3)).to.equal(token4[6]);
            let recp4, amt4;
            [recp4, amt4] = await contract.royaltyInfo(3, ethers.utils.parseEther("1"));
            expect(recp4).to.equal(token4[7]);
            expect(amt4).to.equal(ethers.utils.parseEther((1*token4[8]/10000).toString()));
            expect(await contract.getNumMinted(3, a[0].address)).to.equal(0);
        });
    });

    describe("Access Control", async function() {
        it("Should not allow a non admin or owner to access", async function() {
            let revertStr = "ERC1155TLCore: Address not admin or owner";
            await expect(
                contract.connect(a[10]).createToken(...token1)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).setTokenSupply(0, 100)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).setMintAllowance(0, 2)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).freezeToken(0)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).setURI(0, "test")
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).setMintStatus(0, true)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).setTokenPrice(0, 0)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).setMerkleRoot(0, ethers.utils.formatBytes32String(""))
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).setRoyaltyRecipient(0, a[10].address)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).setRoyaltyPercentage(0, 5000)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).airdrop(0, Array(5).fill(a[10].address))
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).ownerMint(0, 5)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).withdrawEther()
            ).to.be.revertedWith(revertStr);
        });

        it("Should not allow a non owner to access", async function() {
            let revertStr = "Ownable: caller is not the owner";
            await expect(
                contract.connect(a[10]).setAdminAddress(a[10].address)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(a[10]).setPayoutAddress(a[10].address)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(admin).setAdminAddress(a[10].address)
            ).to.be.revertedWith(revertStr);

            await expect(
                contract.connect(admin).setPayoutAddress(a[10].address)
            ).to.be.revertedWith(revertStr);
        });

        it("Should allow the owner to access", async function() {
            await contract.setAdminAddress(owner.address);
            expect(await contract.adminAddress()).to.equal(owner.address);
            await contract.setAdminAddress(admin.address);
            expect(await contract.adminAddress()).to.equal(admin.address);

            await contract.setPayoutAddress(owner.address);
            expect(await contract.payoutAddress()).to.equal(owner.address);
            await contract.setPayoutAddress(payout.address);
            expect(await contract.payoutAddress()).to.equal(payout.address);
        });

        it("Should allow admin to execute", async function() {
            await contract.connect(admin).setTokenSupply(0, 30);
            expect(await contract.getTokenSupply(0)).to.equal(30);

            await contract.connect(admin).setMintAllowance(1, 2);
            expect(await contract.getMintAllowance(1)).to.equal(2);

            await contract.connect(admin).setURI(3, "test3");
            expect(await contract.uri(3)).to.equal("test3");

            await contract.connect(admin).setMintStatus(1, true);
            expect(await contract.getMintStatus(1)).to.be.true;

            await contract.connect(admin).setTokenPrice(0, ethers.utils.parseEther("1"));
            expect(await contract.getTokenPrice(0)).to.equal(ethers.utils.parseEther("1"));

            await contract.connect(admin).setMerkleRoot(0, ethers.utils.formatBytes32String("1"));
            expect(await contract.getMerkleRoot(0)).to.equal(ethers.utils.formatBytes32String("1"));

            await contract.connect(admin).setRoyaltyRecipient(0, royaltyRecp2.address);
            await contract.connect(admin).setRoyaltyPercentage(0, 1000);
            let recp, amt;
            [recp, amt] = await contract.royaltyInfo(0, ethers.utils.parseEther("1"));
            expect(recp).to.equal(royaltyRecp2.address);
            expect(amt).to.equal(ethers.utils.parseEther((0.1).toString()));            
        });

        it("Should allow owner to execute", async function() {
            await contract.setTokenSupply(1, 15);
            expect(await contract.getTokenSupply(1)).to.equal(15);

            await contract.setMintAllowance(2, 2);
            expect(await contract.getMintAllowance(2)).to.equal(2);

            await contract.setURI(3, "test3/");
            expect(await contract.uri(3)).to.equal("test3/");

            await contract.setMintStatus(1, false);
            expect(await contract.getMintStatus(1)).to.be.false;

            await contract.setTokenPrice(0, ethers.utils.parseEther("0.5"));
            expect(await contract.getTokenPrice(0)).to.equal(ethers.utils.parseEther("0.5"));

            await contract.setMerkleRoot(0, ethers.utils.formatBytes32String("2"));
            expect(await contract.getMerkleRoot(0)).to.equal(ethers.utils.formatBytes32String("2"));

            await contract.setRoyaltyRecipient(0, royaltyRecp1.address);
            await contract.setRoyaltyPercentage(0, 500);
            let recp, amt;
            [recp, amt] = await contract.royaltyInfo(0, ethers.utils.parseEther("1"));
            expect(recp).to.equal(royaltyRecp1.address);
            expect(amt).to.equal(ethers.utils.parseEther((0.05).toString()));
        });
    });

    describe("Royalty Info", async function() {
        it("Should retrieve royalty based on token", async function() {
            let recp, amt;
            let recipients = [royaltyRecp1.address, royaltyRecp2.address, royaltyRecp3.address, royaltyRecp4.address];
            let amounts = [token1[token1.length-1], token2[token2.length-1], token3[token3.length-1], token4[token4.length-1]]
            for (let i = 0; i < 4; i++) {
                [recp, amt] = await contract.royaltyInfo(i, ethers.utils.parseEther("1"));
                expect(recp).to.equal(recipients[i]);
                expect(amt).to.equal(ethers.utils.parseEther((amounts[i]/10000).toString()));
            }
        });
    });

    describe("Airdrop", async function() {
        it("Should allow admin to execute", async function() {
            await contract.connect(admin).airdrop(0, a.slice(0,10).map(function(addr) {return addr.address}));
            for (let i = 0; i < 10; i++) {
                expect(await contract.balanceOf(a[i].address, 0)).to.equal(1);
            }

            expect(await contract.getTokenSupply(0)).to.equal(20);

            await contract.connect(admin).airdrop(2, a.slice(0,10).map(function(addr) {return addr.address}));
            for (let i = 0; i < 10; i++) {
                expect(await contract.balanceOf(a[i].address, 2)).to.equal(1);
            }

            expect(await contract.getTokenSupply(2)).to.equal(30);
        }); 

        it("Should allow owner to execute", async function() {
            await contract.airdrop(0, a.slice(0,10).map(function(addr) {return addr.address}));
            for (let i = 0; i < 10; i++) {
                expect(await contract.balanceOf(a[i].address, 0)).to.equal(2);
            }

            expect(await contract.getTokenSupply(0)).to.equal(10);

            await contract.airdrop(2, a.slice(0,10).map(function(addr) {return addr.address}));
            for (let i = 0; i < 10; i++) {
                expect(await contract.balanceOf(a[i].address, 2)).to.equal(2);
            }

            expect(await contract.getTokenSupply(2)).to.equal(20);
        }); 
    });

    describe("Owner Mint", async function() {
        it("Should allow admin to execute", async function() {
            await contract.connect(admin).ownerMint(0, 5);
            expect(await contract.balanceOf(owner.address, 0)).to.equal(5);
        });

        it("Should allow owner to execute", async function() {
            await contract.ownerMint(0, 5);
            expect(await contract.balanceOf(owner.address, 0)).to.equal(10);
            expect(await contract.getTokenSupply(0)).to.equal(0);
        });
    });

    describe("Mint", async function() {
        it("Should not allow minting without mint open", async function() {
            await expect(
                contract.connect(a[0]).mint(1, 1, [])
            ).to.be.revertedWith("ERC1155TLCore: Mint not open");

            await expect(
                contract.connect(a[0]).mint(2, 1, [])
            ).to.be.revertedWith("ERC1155TLCore: Mint not open");

            await expect(
                contract.connect(a[0]).mint(2, 1, [])
            ).to.be.revertedWith("ERC1155TLCore: Mint not open");
        });

        it("Should not allow minting without enough ether", async function() {
            await contract.setMintStatus(1, true);
            await contract.setMintStatus(2, true);
            await contract.setMintStatus(3, true);

            await expect(
                contract.connect(a[0]).mint(1, 1, [])
            ).to.be.revertedWith("ERC1155TLCore: Not enough ether attached to the transaction");

            await expect(
                contract.connect(a[0]).mint(2, 1, [])
            ).to.be.revertedWith("ERC1155TLCore: Not enough ether attached to the transaction");
        });

        it("Should not allow minting if not on the allowlist", async function() {
            let price2 = await contract.getTokenPrice(1);
            await expect(
                contract.connect(a[5]).mint(1, 1, [], {value: price2})
            ).to.be.revertedWith("ERC1155TLCore: Not on allowlist");
            
            let price3 = await contract.getTokenPrice(2);
            await expect(
                contract.connect(a[0]).mint(2, 1, [], {value: price3})
            ).to.be.revertedWith("ERC1155TLCore: Not on allowlist");
        });

        it("Should not allow minting more than allowed", async function() {
            let price2 = await contract.getTokenPrice(1);
            await expect(
                contract.connect(a[0]).mint(1, 10, merkleProofs2[0], {value: price2.mul(10)})
            ).to.be.revertedWith("ERC1155TLCore: Cannot mint more than allowed");
            
            let price3 = await contract.getTokenPrice(2);
            await expect(
                contract.connect(a[5]).mint(2, 10, merkleProofs3[0], {value: price3.mul(10)})
            ).to.be.revertedWith("ERC1155TLCore: Cannot mint more than allowed");
        });

        it("Should allow minting on the allowlist", async function() {
            let price2 = await contract.getTokenPrice(1);
            let allowance2 = await contract.getMintAllowance(1);
            await contract.connect(a[0]).mint(1, 1, merkleProofs2[0], {value: price2});
            await contract.connect(a[1]).mint(1, allowance2, merkleProofs2[1], {value: price2.mul(allowance2)})
            expect(await contract.balanceOf(a[0].address, 1)).to.equal(1);
            expect(await contract.balanceOf(a[1].address, 1)).to.equal(allowance2);

            await contract.connect(a[0]).mint(1, 1, merkleProofs2[0], {value: price2});
            expect(await contract.balanceOf(a[0].address, 1)).to.equal(2);

            let price3 = await contract.getTokenPrice(2);
            let allowance3 = await contract.getMintAllowance(2);
            await contract.connect(a[5]).mint(2, 1, merkleProofs3[0], {value: price3});
            await contract.connect(a[6]).mint(2, allowance3, merkleProofs3[1], {value: price3.mul(allowance3)})
            expect(await contract.balanceOf(a[5].address, 2)).to.equal(3);
            expect(await contract.balanceOf(a[6].address, 2)).to.equal(2 + allowance3);
        });

        it("Should not allow minting more than allowed after minting", async function() {
            let price2 = await contract.getTokenPrice(1);
            await expect(
                contract.connect(a[1]).mint(1, 1, merkleProofs2[1], {value: price2})
            ).to.be.revertedWith("ERC1155TLCore: Cannot mint more than allowed");

            let price3 = await contract.getTokenPrice(2);
            await expect(
                contract.connect(a[6]).mint(2, 1, merkleProofs3[1], {value: price3})
            ).to.be.revertedWith("ERC1155TLCore: Cannot mint more than allowed");
        });

        it("Should allow claiming by anyone", async function() {
            await contract.connect(a[0]).mint(3, 1, []);
            await contract.connect(a[1]).mint(3, 1, []);
            expect(await contract.balanceOf(a[0].address, 3)).to.equal(1);
            expect(await contract.balanceOf(a[1].address, 3)).to.equal(1);
        });

        it("Should not allow claiming more than allowed", async function() {
            await expect(
                contract.connect(a[0]).mint(3, 1, [])
            ).to.be.revertedWith("ERC1155TLCore: Cannot mint more than allowed");
        });
    });

    describe("Token Supply Reached", async function() {
        it("Should revert for airdrop", async function() {
            await expect(
                contract.airdrop(0, [a[0].address])
            ).to.be.revertedWith("ERC1155TLCore: Not enough token supply available");
        });

        it("Should revert for owner mint", async function() {
            await expect(
                contract.ownerMint(0, 1)
            ).to.be.revertedWith("ERC1155TLCore: Not enough token supply available");
        });
    });

    describe("Invalid Token", async function() {
        it("Should revert for a token that hasn't been created", async function() {
            await expect(
                contract.setTokenSupply(5, 1)
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.setMintAllowance(5, 1)
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.freezeToken(5)
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.setURI(5, "test")
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.setMintStatus(5, true)
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.setTokenPrice(5, 1)
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.setMerkleRoot(5, ethers.utils.formatBytes32String("0"))
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.setRoyaltyRecipient(5, a[0].address)
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.setRoyaltyPercentage(5, 100)
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.airdrop(5, [a[0].address])
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.ownerMint(5, 1)
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");

            await expect(
                contract.mint(5, 1, [])
            ).to.be.revertedWith("ERC1155TLCore: Token ID not valid");
        });

        it("Should revert for token already created", async function() {
            await expect(
                contract.createToken(...token1)
            ).to.be.revertedWith("ERC1155TLCore: Token ID already exists");
        });
    });

    describe("Frozen", async function() {
        it("Should revert after freezing", async function() {
            await contract.freezeToken(0);
            await expect(
                contract.setURI(0, "frozen")
            ).to.be.revertedWith("ERC1155TLCore: Token metadata frozen");
        });
    });

    describe("Reentrancy", async function() {
        it("Should fail airdrop reentrancy", async function() {
            let Reenter = await ethers.getContractFactory("ERC1155TLCoreAirdropReentrancy", a[10]);
            let reenter = await Reenter.deploy(contract.address, 3);
            await reenter.deployed();

            await expect(
                contract.airdrop(3, [reenter.address])
            ).to.be.revertedWith("ERC1155TLCore: Address not admin or owner");
        });

        it("Should fail mint reentrancy", async function() {
            let Reenter = await ethers.getContractFactory("ERC1155TLCoreMintReentrancy", a[10]);
            let reenter = await Reenter.deploy(contract.address, 0, 3);
            await reenter.deployed();

            await expect(
                reenter.mintToken()
            ).to.be.revertedWith("ERC1155TLCore: Cannot mint more than allowed");
        });
    });
});