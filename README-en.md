[中文](README.md)|English

![image](https://webasedoc.readthedocs.io/zh_CN/latest/_images/logo.jpg)

# What's WeBASE?

**WeBASE** (WeBank Blockchain Application Software Extension) is a set of general components building between blockchain application and FISCO-BCOS Nodes. Each module is designed around blockchain transaction, contract, key management, data and visual management. Developers can choose subsystems for deployment according to business needs.

**WeBASE** shields the complexity of the bottom layer of the blockchain, reduces the threshold of developers, and greatly improves the development efficiency of the blockchain application. It includes subsystems such as node front, node management, web management platform, sign service, data export etc..

**WeBASE** standardizes the application and development of blockchain. After building the FISCO BCOS nodes, only five steps needed to develop and build the application of blockchain. For details of developing process, please refer to [Using WeBASE to develop blockchain application](https://github.com/WeBankFinTech/WeBASE-Doc/blob/master/docs/WeBASE/quick-start.md)

 **WeBASE One Click Installation** (including FISCO BCOS nodes + WeBASE-Front + WeBASE-Node-Manager + WeBASE-Web) refers to [WeBASE One-Click-Installation Documentation](https://webasedoc.readthedocs.io/zh_CN/latest/docs/WeBASE/install.html)，**WeBASE**'s overall structure design and the detailed introduction of the functions and installation of each subsystem, please refer to [WeBASE Online Documentation](https://webasedoc.readthedocs.io/zh_CN/latest/index.html)

## Subsystem introduction
* **Node Front service [WeBASE-Front](https://github.com/WeBankFinTech/WeBASE-Front)** 
It integrates web3sdk and provides restful interface. The client can interact with the node in the form of HTTP. The built-in memory database collects the health data of the node. Built in Web console to realize the visual operation of nodes and solidity IDE etc..

* **Node management service [WeBASE-Node-Manager](https://github.com/WeBankFinTech/WeBASE-Node-Manager)**
Based on WeBASE-Front, handle all web requests from WeBASE-Web pages, manage the status of each node, manage all smart contracts on the chain, make statistics and Analysis on the data of the blockchain, audit abnormal transactions, private key management, etc.

* **WeBASE management platform [WeBASE-Web](https://github.com/WeBankFinTech/WeBASE-Web)**
Visual operation platform, based on which node information can be viewed and smart contracts can be developed.

* **Transcation service [WeBASE-Transcation](https://github.com/WeBankFinTech/WeBASE-Transcation)**
Receive transaction request, cache transaction to database and asynchronously chain up, which can greatly improve throughput and solve the TPS bottleneck problem of blockchain.

* **Private key Hosting and cloud signature service [WeBASE-Sign](https://github.com/WeBankFinTech/WeBASE-Sign)**
Hosting user private key, providing cloud signature.
<!--
* **Data export code generation tool [WeBASE-Codegen-Monkey](https://github.com/WeBankFinTech/WeBASE-Codegen-Monkey)**
The code generation tool can generate the core code of data export through configuration.

* **Data export service [WeBASE-Collect-Bee](https://github.com/WeBankFinTech/WeBASE-Collect-Bee)**
Export the basic data on the blockchain, such as the current block height, total transaction volume, etc. export the business data of the contract on the blockchain, including the event, constructor, contract address, execution function information, etc. through the configuration of the smart contract.
 -->

* **Chain manage service [WeBASE-Chain-Manager](https://github.com/WeBankFinTech/WeBASE-Chain-Manager)** 
Manage multiple chains, support national secret chain, non-national secret chain. Provide group add, delete, check and change interface, so that users can easily establish their own application groups.

* **Contract security check service [WeBASE-Solidity-Security](https://github.com/WeBankFinTech/WeBASE-Solidity-Security)** 
Inherit contract detection tool Slither, provide external detection interface.

* **Data statistics service [WeBASE-Stat](https://github.com/WeBankFinTech/WeBASE-Stat)** 
Rely on WeBASE-Front,drag data on CPU, memory, IO, group size, group GAS, group network traffic and store into database.

* **Data monitoring service [WeBASE-Data](https://github.com/WeBankFinTech/WeBASE-Data)** 
Rely on WeBASE-Front,export and parse blockchain data to provide a visual view of governance. You can check which chain, which user and which contract the transaction belongs to, and ensure that the data on the chain can be checked and managed.

## Contribution
Please read our [contribution document](https://webasedoc.readthedocs.io/zh_CN/latest/docs/WeBASE/CONTRIBUTING.html) to learn how to contribute your code and submit your contribution.

I hope that with your participation, WeBASE will get better and better!

## Community
Contact us: webase@webank.com
