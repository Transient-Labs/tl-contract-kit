const keccak256 = require("keccak256");
const { MerkleTree } = require("merkletreejs");

const allowlistAddr = ["0x46C0a5326E643E4f71D3149d50B48216e174Ae84",
                        "0x807c47A89F720fe4Ee9b8343c286Fc886f43191b",
                        "0x844ec86426F076647A5362706a04570A5965473B"];

const leafNodes = allowlistAddr.map(addr => keccak256(addr));
const merkleTree = new MerkleTree(leafNodes, keccak256, { sortPairs: true});

console.log("Merkle Tree Root: 0x%s", merkleTree.getRoot().toString("hex"));
allowlistAddr.forEach((addr) => {
    console.log(merkleTree.getHexProof(keccak256(addr)));
});