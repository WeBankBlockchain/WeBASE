中文|[English](README-en.md)

[![Code Lines](https://tokei.rs/b1/github/WeBankBlockchain/WeBASE?category=code)](https://github.com/WeBankFinTech/WeBASE)

![image](https://webasedoc.readthedocs.io/zh_CN/lab/_images/logo.jpg)

# 什么是WeBankBlockchain WeBASE

微众银行开源的自研区块链中间件平台——**WeBankBlockchain WeBASE(WeBank Blockchain Application Software Extension, 简称WBC-WeBASE)** 
是在区块链应用和FISCO BCOS节点之间搭建的一套通用组件，围绕交易、合约、密钥管理，数据，可视化管理来设计各个模块。开发者可以根据业务所需，选择子系统进行部署。

**WBC-WeBASE**屏蔽了区块链底层的复杂度，降低开发者的门槛，大幅提高区块链应用的开发效率，包含**节点前置**、**节点管理**、**Web管理平台**、**签名服务**、**数据导出**等子系统。

**WBC-WeBASE**将区块链应用开发标准化，搭建完FISCO BCOS节点后，只需按照五步标准流程进行区块链应用开发，开发流程请参阅 [使用WBC-WeBASE开发区块链应用](https://github.com/WeBankBlockchain/WeBASE-Doc/blob/master/docs/WeBASE/quick-start.md)

**WBC-WeBASE一键部署**(FISCO BCOS + WeBASE-Front + WeBASE-Node-Manager + WeBASE-Sign + WeBASE-Web)可以参考[WBC-WeBASE一键部署文档](https://webasedoc.readthedocs.io/zh_CN/lab/docs/WeBASE/install.html)，**WBC-WeBASE**整体结构设计与各子系统功能与安装部署的详细介绍，请参考[WBC-WeBASE在线文档](https://webasedoc.readthedocs.io/zh_CN/lab/index.html)

## 各子系统简介
* **节点前置服务 [WeBASE-Front](https://github.com/WeBankBlockchain/WeBASE-Front)** 
集成java-sdk，提供restful风格的接口，客户端可以使用http的形式和节点进行交互，内置内存数据库，采集节点健康度数据。内置web控制台，实现节点的可视化、合约部署IDE等功能。

* **节点管理服务 [WeBASE-Node-Manager](https://github.com/WeBankBlockchain/WeBASE-Node-Manager)**
处理WeBASE-Web前端页面所有web请求，基于前置服务，管理各个节点的状态，管理链上所有智能合约，对区块链的数据进行统计、分析，对异常交易的审计，私钥管理等。

* **WeBASE管理平台 [WeBASE-Web](https://github.com/WeBankBlockchain/WeBASE-Web)**
基于节点管理服务的可视化操作平台，可基于此平台查看节点信息，开发智能合约等。

* **私钥托管和签名服务 [WeBASE-Sign](https://github.com/WeBankBlockchain/WeBASE-Sign)**
托管用户私钥，提供云端签名。

## 贡献说明
请阅读我们的[贡献文档](https://webasedoc.readthedocs.io/zh_CN/lab/docs/WeBASE/CONTRIBUTING.html)，了解如何贡献代码，并提交你的贡献。

希望在您的参与下，WBC-WeBASE会越来越好！

## 社区
联系我们：webase@webank.com

社区小助手微信ID : WeBank_Blockchain
