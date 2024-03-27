const PowerGen = artifacts.require("PowerGen");

module.exports = async function(deployer) {
  await deployer.deploy(PowerGen)
};
