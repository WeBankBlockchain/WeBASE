# 使用WeBASE开发区块链应用 quick start

## 1 部署WeBASE
请参考[快速部署](https://)

## 2 登录WeBASE管理平台，添加节点信息，私钥信息等。
* 节点信息：
![[节点]](./images/frontInfo.png)

* 私钥用户：
![[私钥用户]](./images/keyUser.png)

## 3 开发智能合约
以HelloWorld.sol为例
```
pragma solidity ^0.4.2;

contract HelloWorld{
    string name;

    function HelloWorld(){
       name = "Hello, World!";
    }

    function get()constant returns(string){
        return name;
    }

    function set(string n){
     name = n;
    }
}
```

* 通过智能合约IDE部署合约,并获取合约地址等信息
![[合约]](./images/contract.png)



## 4 根据所写合约和交易api的格式，发送交易。
详细信息请参考[交易接口](https://)


### 4.1 接口调用的主要代码：
* application.yml
```
transactionUrl: http://127.0.0.1:8082/webase-front/trans/handle
groupId: 1
userAddress: "0x4f08eac5af5e77b7006d11bee94adba2f721def8"
useAes: true
contract.name: HelloWorld
contract.address: "0xca597170829f4ad5054b618425a56e0be23cbc55"
contract.funcName: set
contract.funcParam: "[\"abc\"]"
```
* TransactionService.java
```
@Slf4j
@Data
@Service
public class TransactionService {
    @Autowired
    private RestTemplate rest;
    @Value("${transactionUrl}")
    private String url;
    @Value("${userAddress}")
    private String user;
    @Value("${groupId}")
    private int groupId;
    @Value("${useAes}")
    private Boolean useAes;
    @Value("${contract.name}")
    private String contractName;
    @Value("${contract.address}")
    private String contractAddress;
    @Value("${contract.funcName}")
    private String funcName;
    @Value("${contract.funcParam}")
    private String funcParam;

    public void sendTransaction() {

        try {
            TransactionParam transParam = new TransactionParam();
            transParam.setGroupId(groupId);
            transParam.setContractAddress(contractAddress);
            transParam.setUseAes(useAes);
            transParam.setUser(user);
            transParam.setContractName(contractName);
            transParam.setFuncName(funcName);
            transParam.setFuncParam(JSONArray.parseArray(funcParam));

            log.info("transaction param:{}", JSON.toJSONString(transParam));
            Object rsp = rest.postForObject(url, transParam, Object.class);
            String rspStr = "null";
            if (Objects.nonNull(rsp)) {
                rspStr = JSON.toJSONString(rsp);
            }
            log.info("transaction result:{}", rspStr);
        } catch (Exception ex) {
            log.error("fail sendTransaction", ex);
        }
       System.exit(1);
    }
}
```



## 5 在线运维管理
* 查看交易解析
![[交易解析]](./images/transHash.png)

* 交易审计
![[交易审计]](./images/monitor.png)





