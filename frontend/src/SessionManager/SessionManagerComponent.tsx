import React, { useEffect, useState } from "react";
import SessionManager from "./SessionManager";

const SessionManagerComponent: React.FC = () => {
    //const [sessionId, setSessionId] = useState<string | null>(null);

    // We're using useEffect for when the browser refreshes to get a new session //
    useEffect(() => {
        /*const CheckSession = async () => {
            const good = await SessionManager.checkSession();
            console.log(good)
        }*/
    }, []);


    return (<div></div>);
};

export default SessionManagerComponent;