package com.webank.webase.transaction;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Objects;


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
