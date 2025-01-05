package com.project.aichat.service;

import com.project.aichat.models.Document;

import java.util.List;

public interface DocumentService {
    Document saveDocument(Document document);
    Document findDocumentById(Long id);
    List<Document> findAllDocuments();
}
