async function main() {
  const MSDSValidator = await ethers.getContractFactory("MSDSValidator");
  console.log("Deploying MSDSValidator...");
  
  const msds = await MSDSValidator.deploy();
  await msds.waitForDeployment();
  
  const address = await msds.getAddress();
  console.log("✅ MSDSValidator deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});