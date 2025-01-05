import React from 'react';
import './App.css';
import LeftContainer from './components/LeftContainer/LeftContainer';
import RightContainer from './components/RightContainer/RightContainer';
import SessionManagerComponent from './SessionManager/SessionManagerComponent';

function App() {
  return (
    <div id="App">
      <SessionManagerComponent></SessionManagerComponent>
      <LeftContainer></LeftContainer>
      <RightContainer></RightContainer>
    </div>
  );
}

export default App;
