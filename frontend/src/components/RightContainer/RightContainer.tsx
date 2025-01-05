import React, { useState } from "react";
import "./RightContainer.css";
import MessageElement, {Message, User} from "./Message/MessageComponent";
import SessionManager from "../../SessionManager/SessionManager";

let currentId = 0;

const RightContainer = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState<string>("");
    const [generatingAnswer, setgeneratingAnswer] = useState<boolean>(false);
    
    const addMessage = (user: User, message: string) => {
        const msg: Message = {
            id: currentId,
            user: user,
            text: message,
        };
        currentId = currentId + 1

        setMessages(prevMessages => [...prevMessages, msg]);
        setInputText("");
    };

    const autoGrow = (element: HTMLTextAreaElement) => {
        element.style.height = "44px";
        element.style.height = `${element.scrollHeight}px`;

        const inputEnter = document.querySelector(
            "#input_container > input:last-child"
        ) as HTMLElement;
        if (inputEnter !== null) {
            inputEnter.style.opacity = element.value === "" ? "0.2" : "1";
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInputText(e.target.value);
        autoGrow(e.target);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const getAnswer = async (question: string) => {
        const answer: string = await SessionManager.askQuestion(inputText);
        setgeneratingAnswer(false);
        addMessage({ name: "System" }, answer)
        const e = document.getElementById("input_inner") as HTMLTextAreaElement;
        if (e !== null) {
            e.disabled = false;
        }
    }
    
    const handleSubmit = () => {
        if (inputText.trim() !== "") {
            addMessage({ name: "User" }, inputText);

            const e = document.getElementById("input_inner") as HTMLTextAreaElement;
            if (e !== null) {
                e.style.height = "44px";
                e.disabled = true;
                const inputEnter = document.querySelector(
                    "#input_container > input:last-child"
                ) as HTMLElement;
                if (inputEnter !== null) {
                    inputEnter.style.opacity = "0.2"
                }
                setgeneratingAnswer(true);
                getAnswer(inputText)
            }
        }
    };

    return (
        <div id="Right">
            <div id="chatbox_container">
                <div id="chatbox">
                    {messages.map((message) => (
                        <MessageElement key={message.id} message={message} />
                    ))}
                    {generatingAnswer &&
                        <MessageElement key={-1} message={{ id: -1, user: {name:'System'}, text: 'Generating answer...' }} />
                    }
                    <div id="chatbox_empty"></div>
                </div>
            </div>

            <div id="input_container">
            <input type="image" src="images/question_mark.png" alt="Question Mark" />
            <textarea
                id="input_inner"
                placeholder="Message AIChat"
                value={inputText}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                disabled={true}
            />
            <input
                type="image"
                src="images/input_enter.png"
                alt="Submit"
                onClick={handleSubmit}
            />
            </div>
        </div>
    );
};

export default RightContainer;