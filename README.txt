REMIX DEFAULT WORKSPACE

Remix default workspace is present when:
i. Remix loads for the very first time 
ii. A new workspace is created with 'Default' template
iii. There are no files existing in the File Explorer

This workspace contains 3 directories:

1. 'contracts': Holds three contracts with increasing levels of complexity.
2. 'scripts': Contains four typescript files to deploy a contract. It is explained below.
3. 'tests': Contains one Solidity test file for 'Ballot' contract & one JS test file for 'Storage' contract.

SCRIPTS

The 'scripts' folder has four typescript files which help to deploy the 'Storage' contract using 'web3.js' and 'ethers.js' libraries.

For the deployment of any other contract, just update the contract name from 'Storage' to the desired contract and provide constructor arguments accordingly 
in the file `deploy_with_ethers.ts` or  `deploy_with_web3.ts`

In the 'tests' folder there is a script containing Mocha-Chai unit tests for 'Storage' contract.

To run a script, right click on file name in the file explorer and click 'Run'. Remember, Solidity file must already be compiled.
Output from script will appear in remix terminal.

Please note, require/import is supported in a limited manner for Remix supported modules.
For now, modules supported by Remix are ethers, web3, swarmgw, chai, multihashes, remix and hardhat only for hardhat.ethers object/plugin.
For unsupported modules, an error like this will be thrown: '<module_name> module require is not supported by Remix IDE' will be shown.


How to use it:
# Fill .env file first

# Create Virtual Environment (there is already virtual environment in this repository but sometimes it's broken so you must recreate it)
python -m venv .venv

# Activate Virtual Environment
# In cmd.exe
.venv\Scripts\activate.bat
# In PowerShell
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

python msds_cli.py register --id MSDS-001 --file test_files/acetone_msds.txt
python msds_cli.py verify --id MSDS-001 --file test_files/acetone_msds.txt
python msds_cli.py revoke --id MSDS-001 --file test_files/acetone_msds.txt
