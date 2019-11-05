![image](https://webasedoc.readthedocs.io/zh_CN/latest/_images/logo.jpg)

# What's WeBASE?

WeBASE (WeBank Blockchain Application Software Extension) is a set of general components building between blockchain application and FISCO-BCOS Nodes. Each module is designed around transaction, contract, key management, data and visual management. Developers can choose subsystems for deployment according to business needs. WeBASE shields the complexity of the bottom layer of the blockchain, reduces the threshold of developers, and greatly improves the development efficiency of the blockchain application. it includes subsystems such as node front, node management, transaction link, data export, web management platform, etc.For details, please refer to [WeBASE Online documentation](https://webasedoc.readthedocs.io/zh_CN/latest/index.html)

WeBASE standardizes the application and development of blockchain. After building the FISCO BCOS nodes, only five step standard process is needed for the application and development of blockchain. For the development process, please refer to [using webase to develop blockchain application](https://github.com/WeBankFinTech/WeBASE-Doc/blob/master/docs/WeBASE/quick-start.md)

## Subsystem introduction
* **Node Front service [WeBASE-Front](https://github.com/WeBankFinTech/WeBASE-Front)** 
It integrates web3jsdk and provides restful interface. The client can interact with the node in the form of HTTP. The built-in memory database collects the health data of the node. Built in Web console to realize the visual operation of nodes.

* **Node management service [WeBASE-Node-Manager](https://github.com/WeBankFinTech/WeBASE-Node-Manager)**
Handle all web requests on the front-end page, manage the status of each node, manage all smart contracts on the chain, make statistics and Analysis on the data of the blockchain, audit abnormal transactions, private key management, etc.

* **WeBASE management platform [WeBASE-Web](https://github.com/WeBankFinTech/WeBASE-Web)**
Visual operation platform, based on which node information can be viewed and smart contracts can be developed.

* **Transcation service [WeBASE-Transcation](https://github.com/WeBankFinTech/WeBASE-Transcation)**
Receive transaction request, cache transaction to database and asynchronously chain up, which can greatly improve throughput and solve the TPS bottleneck of blockchain.

* **Private key Hosting and cloud signature service [WeBASE-Sign](https://github.com/WeBankFinTech/WeBASE-Sign)**
Hosting user private key, providing cloud signature.

* **Data export code generation tool [WeBASE-Codegen-Monkey](https://github.com/WeBankFinTech/WeBASE-Codegen-Monkey)**
The code generation tool can generate the core code of data export through configuration.

* **Data export service [WeBASE-Collect-Bee](https://github.com/WeBankFinTech/WeBASE-Collect-Bee)**
Export the basic data on the blockchain, such as the current block height, total transaction volume, etc. export the business data of the contract on the blockchain, including the event, constructor, contract address, execution function information, etc. through the configuration of the smart contract.

## Contribution
Please read our [contribution document](https://webasedoc.readthedocs.io/zh_CN/latest/docs/WeBASE/CONTRIBUTING.html) to learn how to contribute your code and submit your contribution.

I hope that with your participation, webase will get better and better!

## Community
Contact us：webase@webank.com
