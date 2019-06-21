# 介绍
WeBASE（WeBank Blockchain Application Software Extension） 是在区块链应用和底层之间搭建的一套通用组件，围绕交易、合约、密钥管理，数据，可视化管理来设计各个模块，开发者可以根据业务所需，选择子系统进行部署。可以屏蔽区块链底层的复杂度，降低开发者的门槛，大幅提高区块链应用的开发效率。包含了节点前置、节点管理、交易链路，数据导出，Web管理平台等子系统。

开发者搭建完区块链节点后，部署WeBASE，基于WeBASE开发区块链应用，将会大幅提升效率。



# 设计原则
**按需部署**
WeBASE抽象应用开发的诸多共性模块，形成各类服务组件，开发者根据需要部署所需组件。

**微服务**
WeWeBASE采用微服务架构，基于spring-boot框架，提供Restful风格接口。

**零耦合**
WeBWeBASE所有子系统独立存在，均可独立部署，独立提供服务。

**可定制**
前端页面往往带有自身的业务属性，因此WeBASE采用前后端分离的技术，便于开发者基于后端接口定制自己的前端页面。

# 整体架构

![[架构图]](./images/architecture.png)


# 安装说明
请参考安装说明文档[install.md](https://github.com/WeBankFinTech/WeBASE/blob/dev/install.md)

# 各子系统介绍

<table style="width:100%;border-collapse:collapse">
    <thead>
        <tr>
            <th width="180">子系统名</th>
            <th width="180">功能</th>
            <th>介绍</th>
        </tr>
    </thead>
    <tbody>
       <tr>
            <td>webase-front</td>
            <td>节点前置</td>
            <td>集成web3jsdk，提供restful风格的接口，客户端可以使用http的形式和节点进行交互，如获取节点快高，部署合约，发送交易等。内置内存数据库，采集节点健康度数据。内置web控制台，实现节点的可视化操作。</td>
        </tr>
       <tr>
            <td>webase-transcation</td>
            <td>交易上链代理</td>
            <td>接收交易请求，缓存交易到数据库中，异步上链。可大幅提升吞吐量，解决区块链的tps瓶颈。</td>
        </tr>
      <tr>
            <td>webase-node-mgr</td>
            <td>节点管理</td>
            <td>处理前端页面所有web请求，管理各个节点的状态，管理链上所有智能合约，对区块链的数据进行统计、分析，对异常交易的审计，私钥管理等；</td>
        </tr>
      <tr>
            <td>webase-web</td>
            <td>WeBASE管理平台</td>
            <td>数据概览：可以查看机构、节点、合约、区块和交易详情。节点管理：查看区块链上所有节点的状态。合约管理：编辑、编译、部署、调试、测试合约。私钥管理：管理各用户的公私钥。系统监控：各节点的监控数据查看。交易审计：异常交易事后审计。</td>
        </tr>
    </tbody>
</table>


# 应用开发步骤
1 部署WeBASE。

2 登录WeBASE管理平台，添加节点信息，私钥信息等。

3 开发智能合约，编译、部署、测试合约。

4 根据所写合约和交易api的格式，发送交易。

5 登录管理平台查看交易详情，查看交易统计信息，在线运维管理

# 贡献说明
请阅读我们的贡献[文档](https://github.com/WeBankFinTech/WeBASE/blob/master/CONTRIBUTING.md)，了解如何贡献代码，并提交你的贡献。

希望在您的参与下，WeBASE会越来越好！

# 社区
- 联系我们：webase@webank.com
