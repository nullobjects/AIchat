import React, { useState } from "react";
import "./RightContainer.css";
import MessageElement, {Message, User} from "./Message/MessageComponent";
import SessionManager from "../../SessionManager/SessionManager";

let currentId = 0;

const RightContainer = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState<string>("");
    const [generatingAnswer, setGeneratingAnswer] = useState<boolean>(false);
    const [questions, setQuestions] = useState<string[]>([]);
    const [generatingQuestions, setGeneratingQuestions] = useState<boolean>(false);

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
        const answer: string = await SessionManager.askQuestion(question);
        setGeneratingAnswer(false);
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
                setGeneratingAnswer(true);
                getAnswer(inputText)
            }
        }
    };

    const handleGetQuestions = async () => {
        setGeneratingQuestions(true)
        const questions: string[] = await SessionManager.getQuestions();
        setQuestions(questions)
    };

    const SelectRandomQuestion = async (idx: number) => {
        setGeneratingQuestions(false)

        const question = questions[idx];
        addMessage({ name: "User" }, question);

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
            setGeneratingAnswer(true);
            getAnswer(question)
        }

        setQuestions([])
    }

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
                <div id="question_container">
                    <input type="image" src="images/question_mark.png" alt="Question Mark" onClick={handleGetQuestions}/>
                    
                    {generatingQuestions && (
                        <div id="question_tooltip">
                            {questions.length === 0 ? (
                                <div id="question_thinking">Thinking...</div>
                            ) : (
                                questions.map((question, index) => (
                                    <input
                                        type="button"
                                        className="random_question"
                                        key={index}
                                        value={question}
                                        onClick={() => SelectRandomQuestion(index)}
                                    />
                                ))
                            )}
                        </div>
                    )}
                </div>

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
                    id="submit_button"
                />
            </div>
        </div>
    );
};

export default RightContainer;