module.exports = {
   networks: {
    development: {
      host: "127.0.0.1",     // Localhost (default: none)
      port: 7545,            // Standard Ethereum port (default: none)
      network_id: "1515",       // Any network (default: none)
      // gasPrice: 2000000,  // 20 gwei (in wei) (default: 100 gwei)
      // gas: 6700000,           // Gas sent with each transaction (default: ~6700000)
     }
  },

  // Set default mocha options here, use special reporters etc.
  mocha: {
    // timeout: 100000
  },

  contracts_directory: './contracts/',
  contracts_build_directory: './abis',
  // Configure your compilers
  compilers: {
    solc: {
      version: "0.8.13",      // Fetch exact version from solc-bin (default: truffle's version)
      settings: {          // See the solidity docs for advice about optimization and evmVersion
       optimizer: {
         enabled: true,
         runs: 200
       }
      }
    }
  }
};
