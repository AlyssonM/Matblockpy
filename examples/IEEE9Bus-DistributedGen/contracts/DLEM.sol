// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0; 

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DLEM is ERC20{

    struct Transaction {
        address owner;
        address counterparty; // O outro lado da transação, seja comprador ou vendedor
        uint tslot;
        uint256 quantity;
        uint256 price;
        bool settled;
    }

    struct Bid {
        uint bid_num;
        address bidder;
        string ipfsCid;
        bytes32 dataHash;
        bool valid;
    }

    Bid[] public bids;
    Transaction[] public Transactions;
    uint constant TEFsize = 24;
    enum Role{Consumer, Prosumer}
    enum Billstatus{Unpaid, Partialpaid, Fullpaid}
    address private DSO;
    event LEMstart(uint256 stime, uint256 etime);
    event LEMend(uint256[TEFsize] MCP, uint256[TEFsize] MCQ, uint256 etime);
    event NewBid(Bid bid);

    mapping(address => bool) user_bid;
    mapping(address => bool) user_reg;
    address[] wallets;

    struct Users_ID{
        address wallet;
        string ID;
        bytes32 _hash;
        Role _role;
    }

    struct energy_matched{ 
        address prosumer; 
        address consumer;
        uint256 demand; 
        uint256 amount;
        uint256 m_amount;  
        uint256 price;
        Billstatus billed;
    }

    uint endLEM;
    uint256[TEFsize] MCP;
    uint256[TEFsize] MCQ;
    uint256[] Rprice;
    mapping(address => Users_ID) Clients;
    mapping(uint => energy_matched[]) public energy_matches;

    constructor() ERC20("LEMtoken", "LET"){
        DSO = msg.sender;
        _mint(msg.sender, 10000000 * (10**decimals()));
    }

    modifier OnlyDSO(){
        require(msg.sender == DSO, "Caller is not DSO");
        _;
    }

    function Register(string memory _id, bytes32 _hash, Role _role) public{
        require(endLEM > block.timestamp + 1 minutes, "Market closed");
        require(user_reg[msg.sender] == false, "Address already registered");
        Clients[msg.sender] = Users_ID(msg.sender, _id, _hash, _role);
        wallets.push() = msg.sender;
        user_bid[msg.sender] = false;
        user_reg[msg.sender] = true;
    }

    function startLEM() public OnlyDSO { 
        for(uint k=0; k < wallets.length; k++){
            delete Clients[wallets[k]];
            delete user_bid[wallets[k]];
            delete user_reg[wallets[k]];
        }
        delete wallets;
        delete bids;
        delete Transactions;
        for(uint i=0; i < TEFsize; i++)
            delete energy_matches[i];
        uint t = 30 minutes; 
        endLEM = t + block.timestamp;
        emit LEMstart(block.timestamp,endLEM); 
    }

    function submitBid(int256[TEFsize] memory _amount, uint256[TEFsize] memory _price, string memory ipfsCid) public {
        if (block.timestamp > endLEM) revert("Cannot bid with LEM closed");
        require(user_reg[msg.sender], "Address must be registered");
        require(user_bid[msg.sender] == false, "Address already bid");
        uint256 totalbuy = 0;
        uint256 bid_num = 0;

        if(bids.length == 0){
            bid_num = 0;
        }
        else{
            bid_num = bids[bids.length -1].bid_num + 1;
        }
        for(uint i = 0; i <= (TEFsize - 1); i++){
            if(_amount[i] < 0){
                totalbuy += (uint256(abs(_amount[i]))*getRetailPrice(i)*(10**(decimals()-3)));
            }
        }
        //require(balanceOf(msg.sender) > totalbuy, "Not enough balances");
        //decreaseAllowance(DSO, allowance(msg.sender, DSO));
        //increaseAllowance(DSO,totalbuy);  
        bytes32 dataHash = keccak256(abi.encodePacked(_price, _amount));
        
   
        //Bid memory newBid = 
        // newBid.bid_num = bid_num; 
        // newBid.bidder = msg.sender;
        // newBid.ipfsCid = ipfsCid;
        // newBid.dataHash = dataHash;
        // newBid.valid = true;
        bids.push() = Bid(bid_num,msg.sender,ipfsCid,dataHash, true);
    }

    function RequestBidUpdate(uint bid_num, int256[TEFsize] memory _amount, uint256[TEFsize] memory _price, string memory newipfsCid) public{
        require(user_bid[msg.sender] == true, "Address not bidded");
        int256 index = -1;
        for(uint i = 0; i < bids.length; i++) {
            if(bids[i].bid_num == bid_num) {
                index = int256(i);
                break;
            }
        }
        require(index >= 0, "Bid not found");
        uint256 totalbuy = 0;
        for(uint i = 0; i <= (TEFsize - 1); i++){
            if(_amount[i] < 0){
                totalbuy += (uint256(abs(_amount[i]))*getRetailPrice(i)*(10**(decimals()-3)));
            }
        }
        require(balanceOf(msg.sender) > totalbuy, "Not enough balances");
        decreaseAllowance(DSO, allowance(msg.sender, DSO));
        increaseAllowance(DSO,totalbuy);  
        bids[uint256(index)].ipfsCid = newipfsCid;
        bids[uint256(index)].dataHash = keccak256(abi.encodePacked(_price, _amount));
    }

    function closeLEM() public OnlyDSO{
        endLEM = block.timestamp; 
    }

    function setRetailPrice(uint256[TEFsize] memory _rprice) public OnlyDSO{
        if(msg.sender != DSO) revert(); 
        if(Rprice.length > 0)
            delete Rprice;
        for(uint i = 0; i <= (TEFsize - 1); i++){
            Rprice.push() = _rprice[i];
        }
    }


    function getRetailPrice(uint tslot)  public view returns(uint256){
        return Rprice[tslot];
    }

    function setLastMCP(uint256[TEFsize] memory mcp) public OnlyDSO {
        require(mcp.length == TEFsize);
        for(uint i = 0; i <= (TEFsize - 1); i++){
            MCP[i] = mcp[i];
        }
    }

    function setLastMCQ(uint256[TEFsize] memory mcq) public OnlyDSO {
        require(mcq.length == TEFsize);
        for(uint i = 0; i <= (TEFsize - 1); i++){
            MCQ[i] = mcq[i];
        }
    }

    function getBids() public view returns (Bid[] memory){
        return bids;
    }

    function getBidsLength() public view returns (uint){
        return bids.length;
    }

    function addTransaction(
        address _owner,
        address _counterparty,
        uint _tslot,
        uint256 _quantity,
        uint256 _price
    ) public {
        Transactions.push(Transaction(_owner, _counterparty, _tslot, _quantity, _price, false));
    }

    function getTransactions() public view returns (Transaction[] memory){
        return Transactions;
    }
    
    function abs(int256 x) private pure returns (int256) {
        return x >= 0 ? x : -x;
    }

    function max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a : b;
    }

    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }

}