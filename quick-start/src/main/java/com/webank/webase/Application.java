package com.webank.webase;

import com.webank.webase.transaction.TransactionService;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        ConfigurableApplicationContext applicationContext = SpringApplication.run(Application.class, args);
        TransactionService tranService = applicationContext.getBean(TransactionService.class);
        tranService.sendTransaction();
    }

    @Bean
    public RestTemplate getRestTemplate() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setReadTimeout(10000);// ms
        factory.setConnectTimeout(10000);// ms
        return new RestTemplate(factory);
    }
}
