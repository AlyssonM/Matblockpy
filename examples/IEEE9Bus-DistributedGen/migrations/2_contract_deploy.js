const DLEM = artifacts.require("DLEM");

module.exports = async function(deployer, network, accounts) {
  await deployer.deploy(DLEM)
};
