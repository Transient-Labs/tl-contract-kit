const keccak256 = require("keccak256");
const { MerkleTree } = require("merkletreejs");

const allowlistAddr1 = ["0x46C0a5326E643E4f71D3149d50B48216e174Ae84",
                        "0x807c47A89F720fe4Ee9b8343c286Fc886f43191b",
                        "0x844ec86426F076647A5362706a04570A5965473B"];

const leafNodes1 = allowlistAddr1.map(addr => keccak256(addr));
const merkleTree1 = new MerkleTree(leafNodes1, keccak256, { sortPairs: true});

console.log("Merkle Tree Root 1: 0x%s", merkleTree1.getRoot().toString("hex"));
allowlistAddr1.forEach((addr) => {
    console.log(merkleTree1.getHexProof(keccak256(addr)));
});

const allowlistAddr2 = ["0x23BB2Bb6c340D4C91cAa478EdF6593fC5c4a6d4B",
                        "0xA868bC7c1AF08B8831795FAC946025557369F69C",
                        "0x1CEE82EEd89Bd5Be5bf2507a92a755dcF1D8e8dc"];

const leafNodes2 = allowlistAddr2.map(addr => keccak256(addr));
const merkleTree2 = new MerkleTree(leafNodes2, keccak256, { sortPairs: true});

console.log("Merkle Tree Root 2: 0x%s", merkleTree2.getRoot().toString("hex"));
allowlistAddr2.forEach((addr) => {
    console.log(merkleTree2.getHexProof(keccak256(addr)));
});