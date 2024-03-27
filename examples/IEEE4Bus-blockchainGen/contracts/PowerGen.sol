// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0; 

contract PowerGen{
    event PowerChange(int ActivePower, int ReactivePower);
    
    struct Generator{ 
        int ActivePower;
        int ReactivePower;
    }

    Generator Gen1; 

    function setGenPwr(int ActivePwr, int ReactivePwr) public{
        Gen1.ActivePower = ActivePwr;
        Gen1.ReactivePower = ReactivePwr;
        emit PowerChange(ActivePwr, ReactivePwr);
    }
 
    function getGen() public view returns(Generator memory){
        return Gen1;
    }

}
