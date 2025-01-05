package com.project.aichat.web;

import com.project.aichat.models.Document;
import com.project.aichat.service.DocumentService;
import com.project.aichat.service.LangChainService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

@Controller
@RequestMapping("/document")
public class DocumentController {

    private final DocumentService documentService;
    private final LangChainService langChainService;

    @Autowired
    public DocumentController(DocumentService documentService, LangChainService langChainService) {
        this.documentService = documentService;
        this.langChainService = langChainService;
    }

    @GetMapping
    public String index(Model model) {
        model.addAttribute("documents", documentService.findAllDocuments());
        return "index";
    }

    @PostMapping("/upload")
    public String uploadDocument(@RequestParam("file") MultipartFile file, Model model) throws IOException {
        String content = new String(file.getBytes(), StandardCharsets.UTF_8);
        Document document = new Document(content);
        documentService.saveDocument(document);
        langChainService.uploadDocument(file);
        model.addAttribute("message", "Document uploaded and saved.");
        return "redirect:/";
    }

    @GetMapping("/ask")
    public String askQuestion(@RequestParam("id") Long id, @RequestParam("question") String question, Model model) {
        Document document = documentService.findDocumentById(id);
        if (document == null) {
            model.addAttribute("error", "Document not found.");
            return "error";
        }
        String answer = langChainService.askQuestion(document.getContent(), question);

        model.addAttribute("document", document);
        model.addAttribute("question", question);
        model.addAttribute("answer", answer);
        return "answer";
    }
}
