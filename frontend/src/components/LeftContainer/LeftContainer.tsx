import { useState } from "react";
import "./LeftContainer.css";
import SessionManager from "../../SessionManager/SessionManager";
import Docxtemplater from 'docxtemplater';
import PizZip from 'pizzip';
import pdfToText from 'react-pdftotext'

const LeftContainer = () => {
  const [draggingOver, setDraggingOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [fileContent, setFileContent] = useState<String>("");

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];

    if (droppedFile) {
      uploadFile(droppedFile);
    }
    setDraggingOver(false)
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDraggingOver(true)
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDraggingOver(false)
  };

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    readFileContent(file, (content: String) => {
      if (content !== null) {
        SessionManager.uploadFile(content).then((success: boolean) => {
          if (success) {
            setFile(file);
            const e = document.getElementById("input_inner") as HTMLTextAreaElement;
            if (e !== null) {
                e.disabled = false;
            }
          }
        })
      }
    });
  };

  const MAX_FILE_SIZE_MB = 50;
  const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
  const readFileContent = (file: File, callback: Function) => {
    const fileType = file.type;

    if (fileType === "application/pdf") {
      try {
        pdfToText(file).then((text) => {
          setFileContent(text);
          callback(text);
        });
      } catch (error) {
        alert("Failed to read PDF file.");
      }
    } else if (fileType === "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
      try {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const content = event.target?.result as ArrayBuffer;
            const zip = new PizZip(content);
            const doc = new Docxtemplater(zip, { paragraphLoop: true, linebreaks: true });
            const docText = doc.getFullText();
            setFileContent(docText);
            callback(docText);
          } catch (error) {
            alert("Failed to read DOCX file.");
          }
        };
        reader.readAsArrayBuffer(file);
      } catch (error) {
        alert("Failed to read DOCX file.");
      }
    } else if (fileType === "text/plain") {
      const reader = new FileReader();
      reader.onload = () => {
        const content: String = reader.result as string;
        setFileContent(content);
        callback(content);
      };
      reader.readAsText(file);
    } else {
      alert("Unsupported file type.");
    }
    return null;
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();

    const files = e.target.files
    if (files?.length === 0) {
      alert("Please enter a file!")
      return;
    } else if (files?.length !== 1) {
      alert("You can only enter one file!")
      return;
    }
    
    const file: File = files[0];
    if (file.size > MAX_FILE_SIZE_BYTES) {
      alert("File content exceeds the size limit.");
      return;
    }

    readFileContent(file, (content: String) => {
      if (content !== null) {
        SessionManager.uploadFile(content).then((success: boolean) => {
          if (success) {
            setFile(file);
            const e = document.getElementById("input_inner") as HTMLTextAreaElement;
            if (e !== null) {
                e.disabled = false;
            }
          }
        })
      }
    });
  }

  return <div id="Left">
    {file === null ? (
        <div className={`drop-zone ${draggingOver ? 'dragging-over' : ''}`} onDrop={handleDrop} onDragOver={handleDragOver} onDragLeave={handleDragLeave}>
          <div className="drop-zone-container">
            <img src="./images/upload.png" alt=""></img>
            <p>Drag & drop files or <span className="browseBtn">Browse</span></p>
            <p>Supported formats: .txt, .docx, .pdf</p>
          </div>
          <input type="file" className="hidden-fill-input" id="fileInput" accept=".txt,.docx,.pdf" onChange={e => {handleFileUpload(e)}}></input>
        </div>
      ) : (
        <div id = "file_container">
          <pre>
            {fileContent}


          </pre>
        </div>
    )}
  </div>
}

export default LeftContainer;