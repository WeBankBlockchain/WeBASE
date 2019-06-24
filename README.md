# 什么是WeBASE

WeBASE（WeBank Blockchain Application Software Extension） 是在区块链应用和fisco bcos节点之间搭建的一套通用组件。围绕交易、合约、密钥管理，数据，可视化管理来设计各个模块，开发者可以根据业务所需，选择子系统进行部署。WeBASE屏蔽了区块链底层的复杂度，降低开发者的门槛，大幅提高区块链应用的开发效率，包含节点前置、节点管理、交易链路，数据导出，Web管理平台等子系统。

WeBASE将区块链应用开发标准化，搭建完fisco bcos节点后，只需按照五步标准流程进行区块链应用开发，开发流程请参阅 [使用WeBASE开发区块链应用](https://)

## 整体架构
完整的部署架构如下，其中webase-front需要和区块链节点同机部署。
![[架构图]](../../images/webase/architecture.png)

## 各子系统简介
* 节点前置服务 **[WeBASE-Front](https://github.com/WeBankFinTech/WeBASE-Front)**
```
集成web3jsdk，提供restful风格的接口，客户端可以使用http的形式和节点进行交互，内置内存数据库，采集节点健康度数据。内置web控制台，实现节点的可视化操作。
```
* 节点管理服务 **[WeBASE-Node-Manager](https://github.com/WeBankFinTech/WeBASE-Node-Manager)**
```
处理前端页面所有web请求，管理各个节点的状态，管理链上所有智能合约，对区块链的数据进行统计、分析，对异常交易的审计，私钥管理等。
```
* WeBASE管理平台 **[WeBASE-Web](https://github.com/WeBankFinTech/WeBASE-Web)**
```
可视化操作平台，可基于此平台查看节点信息，开发智能合约等。
```
* 交易服务 **[WeBASE-Transcation](https://github.com/WeBankFinTech/WeBASE-Transcation)**
```
接收交易请求，缓存交易到数据库中，异步上链，可大幅提升吞吐量，解决区块链的tps瓶颈。
```
* 私钥托管和签名服务 **[WeBASE-Sign](https://github.com/WeBankFinTech/WeBASE-Sign)**
```
托管用户私钥，提供云端签名。
```
* 数据导出代码生成工具 **[WeBASE-Codegen-Monkey](https://github.com/WeBankFinTech/WeBASE-Codegen-Monkey)**
```
代码生成工具，通过配置可以生成数据导出的核心代码。
```
* 数据导出服务 **[WeBASE-Collect-Bee](https://github.com/WeBankFinTech/WeBASE-Collect-Bee)**
```
导出区块链上的基础数据，如当前块高、交易总量等，通过智能合约的配置，导出区块链上合约的业务数据，包括event、构造函数、合约地址、执行函数的信息等。
```
## 设计原则
**按需部署**
WeBASE抽象应用开发的诸多共性模块，形成各类服务组件，开发者根据需要部署所需组件。

**微服务**
WeBASE采用微服务架构，基于spring-boot框架，提供Restful风格接口。

**零耦合**
WeBASE所有子系统独立存在，均可独立部署，独立提供服务。

**可定制**
前端页面往往带有自身的业务属性，因此WeBASE采用前后端分离的技术，便于开发者基于后端接口定制自己的前端页面。
