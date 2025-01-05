package com.project.aichat.service.impl;

import com.project.aichat.models.Document;
import com.project.aichat.repository.DocumentRepository;
import com.project.aichat.service.DocumentService;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DocumentServiceImpl implements DocumentService {
    private final DocumentRepository documentRepository;

    public DocumentServiceImpl(DocumentRepository documentRepository) {
        this.documentRepository = documentRepository;
    }

    @Override
    public Document saveDocument(Document document) {
        return documentRepository.save(document);
    }

    @Override
    public Document findDocumentById(Long id) {
        return documentRepository.findById(id).orElse(null);
    }

    @Override
    public List<Document> findAllDocuments() {
        return documentRepository.findAll();
    }
}
