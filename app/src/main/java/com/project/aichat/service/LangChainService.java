package com.project.aichat.service;

import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

public interface LangChainService {
    String uploadDocument(MultipartFile file) throws IOException;
    String askQuestion(String documentContent,String question);
}
