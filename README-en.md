[中文](README.md)|English

![image](https://webasedoc.readthedocs.io/zh_CN/lab/_images/logo.jpg)

# What's WeBankBlockchain WeBASE?

**WeBankBlockchain WeBASE(called WBC-WeBASE for short)** (WeBank Blockchain Application Software Extension) is a set of general components building between blockchain application and FISCO-BCOS Nodes. Each module is designed around blockchain transaction, contract, key management, data and visual management. Developers can choose subsystems for deployment according to business needs.

**WBC-WeBASE** shields the complexity of the bottom layer of the blockchain, reduces the threshold of developers, and greatly improves the development efficiency of the blockchain application. It includes subsystems such as node front, node management, web management platform, sign service, data export etc..

**WBC-WeBASE** standardizes the application and development of blockchain. After building the FISCO BCOS nodes, only five steps needed to develop and build the application of blockchain. For details of developing process, please refer to [Using WeBASE to develop blockchain application](https://github.com/WeBankFinTech/WeBASE-Doc/blob/lab/docs/WeBASE/quick-start.md)

 **WBC-WeBASE One Click Installation** (including FISCO BCOS nodes + WeBASE-Front + WeBASE-Node-Manager + WeBASE-Web) refers to [WeBASE One-Click-Installation Documentation](https://webasedoc.readthedocs.io/zh_CN/lab/docs/WeBASE/install.html)，**WBC-WeBASE**'s overall structure design and the detailed introduction of the functions and installation of each subsystem, please refer to [WeBASE Online Documentation](https://webasedoc.readthedocs.io/zh_CN/lab/index.html)

## Subsystem introduction
* **Node Front service [WeBASE-Front](https://github.com/WeBankBlockchain/WeBASE-Front)** 
It integrates fisco-bcos-java-sdk and provides restful interface. The client can interact with the node in the form of HTTP. The built-in memory database collects the health data of the node. Built in Web console to realize the visual operation of nodes and solidity IDE etc..

* **Node management service [WeBASE-Node-Manager](https://github.com/WeBankBlockchain/WeBASE-Node-Manager)**
Based on WeBASE-Front, handle all web requests from WeBASE-Web pages, manage the status of each node, manage all smart contracts on the chain, make statistics and Analysis on the data of the blockchain, audit abnormal transactions, private key management, etc.

* **WeBASE management platform [WeBASE-Web](https://github.com/WeBankBlockchain/WeBASE-Web)**
Visual operation platform, based on which node information can be viewed and smart contracts can be developed.

* **Private key Hosting and cloud signature service [WeBASE-Sign](https://github.com/WeBankBlockchain/WeBASE-Sign)**
Hosting user private key, providing cloud signature.

## Contribution
Please read our [contribution document](https://webasedoc.readthedocs.io/zh_CN/lab/docs/WeBASE/CONTRIBUTING.html) to learn how to contribute your code and submit your contribution.

I hope that with your participation, WBC-WeBASE will get better and better!

## Community
Contact us: webase@webank.com

WeChat Community ID : WeBank_Blockchain
