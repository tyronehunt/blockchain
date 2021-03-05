// Kcoin ICO

// Version of compiler
pragma solidity ^0.7.4;

contract kcoin_ico { 
    
    // Introducing the maximum number of kcoin available for sale
    uint public max_kcoin = 1000000;
    
    // Introducing USD / Kcoin conversion rate
    uint public usd_to_kcoin = 1000;
    
    // Introducing total number of kcoin bought by investors
    uint public total_kcoin_bought = 0;
    
    
    // Mapping from the investor address to its equity in kcoin and USD
    mapping(address => uint) equity_kcoin;
    mapping(address => uint) equity_usd;
    
    // Checking if investor can buy kcoin
    modifier can_buy_kcoin(uint usd_invested) {
        require (usd_invested * usd_to_kcoin + total_kcoin_bought <= max_kcoin);
        _;
    }
    
    // Getting the equity in Kcoin of an investor (type var_name)
    function equity_in_kcoin(address investor) external constant returns (uint) {
        return equity_kcoin[investor]; 
    }
    
    // Getting the equity in USD of an investor
        function equity_in_usd(address investor) external constant returns (uint) {
        return equity_usd[investor]; 
    }
    
    // Buy Kcoin
    function buy_kcoin(address investor, uint usd_invested) external
    can_buy_kcoin(usd_invested) {
        uint kcoin_bought = usd_invested * usd_to_kcoin;
        equity_kcoin[investor] += kcoin_bought;
        equity_usd[investor] = equity_kcoin[investor] / usd_to_kcoin;
        total_kcoin_bought += kcoin_bought;
    }
    
    // Sell Kcoin
        function sell_kcoin(address investor, uint kcoin_sold) external {
        equity_kcoin[investor] -= kcoin_sold;
        equity_usd[investor] = equity_kcoin[investor] / usd_to_kcoin;
        total_kcoin_bought -= kcoin_sold;
    }
    
}
