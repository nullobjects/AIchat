package com.project.aichat.service.impl;

import com.project.aichat.service.LangChainService;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.util.UriComponentsBuilder;

import java.io.File;
import java.io.IOException;

@Service
public class LangChainServiceImpl implements LangChainService {
    private final String langChainServiceUrl = "http://localhost:5000";
    private final RestTemplate restTemplate = new RestTemplate();

    @Override
    public String uploadDocument(MultipartFile file) throws IOException {
        File convFile = new File(System.getProperty("java.io.tmpdir") + "/" + file.getOriginalFilename());
        file.transferTo(convFile);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new FileSystemResource(convFile));

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        ResponseEntity<String> response = restTemplate.postForEntity(langChainServiceUrl + "/upload", requestEntity, String.class);
        return response.getBody();
    }

    @Override
    public String askQuestion(String documentContent, String question) {
        UriComponentsBuilder uriBuilder = UriComponentsBuilder.fromHttpUrl(langChainServiceUrl + "/ask")
                .queryParam("documentContent", documentContent)
                .queryParam("question", question);

        ResponseEntity<String> response = restTemplate.getForEntity(uriBuilder.toUriString(), String.class);
        return response.getBody();
    }
}
