import axios from "axios";

axios.defaults.withCredentials = true

const SessionManager = {
    url: "http://localhost:5000",

    startSession: async function() {
        try {
            axios.post(this.url + "/start_session");
            return true;
        } catch (error) {
            console.error("Error starting session:", error);
            throw error;
        }
    },

    checkSession: async function() {
        try {
            const response = await axios.get(this.url + "/check_session");
            if (response.data.message === "Invalid token") {
                return false;
            }
            return true;
        } catch (error) {
            console.error("Error getting session:", error);
            throw error;
        }
    },

    // We will read the content of the file client-side in order to save server performance //
    // Send the content of the file directly as a string //
    uploadFile: async function(content: String) {
        try {
            //const formData = new FormData();
            //formData.append("file", file);        
            //const response = await axios.post(this.url + "/upload", formData, {
            //    headers: {
            //        'Content-Type': 'multipart/form-data',
            //    },
            //});
            
            const response = await axios.post(this.url + "/upload", content, {
                headers: {
                    'Content-Type': 'text/plain',
                },
            });
            
            console.log("File uploaded successfully:", response.data);
            //alert(`File "${file.name}" uploaded successfully!`);
            return true;
        } catch (error) {
            console.error("Upload error:", error);
            alert("Upload failed. Please try again.");
        }

        return false
    },

    askQuestion: async function(message : String) {
        try {
            const response = await axios.post(this.url + "/ask_question", message, {
                headers: {
                    'Content-Type': 'text/plain',
                },
            });
            return response.data.message
        } catch (error) {
            console.error("Unexpected error:", error);
            alert("Your question couldn't be submitted due to an unexpected error.");
        }
    },

    getQuestions: async function() {
        try {
            const response = await axios.get(this.url + "/get_questions", {
                headers: {
                    'Content-Type': 'text/plain',
                },
            });
            return response.data.message
        } catch (error) {
            console.error("Unexpected error:", error);
            alert("We couldn't generate questions for you.");
        }
    }
}

// Initialize the session //
const initializeSession = async () => {
    try {
        const good = await SessionManager.checkSession();
        if (!good) {
            SessionManager.startSession();
        }
    } catch (error) {
        console.error("Error initializing session:", error);
    }
};

initializeSession();

export default SessionManager;