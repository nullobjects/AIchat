export interface User {
    name: string;
}

export interface Message {
    id: number;
    user: User;
    text: string;
}

const MessageElement: React.FC<{ message: Message }> = ({ message }) => {
    return (
        <pre key={message.id} className="message_container">
            {message.text}
        </pre>
    );
}

export default MessageElement;