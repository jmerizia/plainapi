import React from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from 'react-router-dom';


function App() {
  return (
    <Router>
      <div>
        <Switch>
          <Route path='/waitlist'>
            <WaitlistPage />
          </Route>
          <Route path='/'>
            <IndexPage />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}


function IndexPage() {
  return <div className="App">
    <div className='App-row'>
      <div className='App-col'>
        <Logo />
      </div>
      <div className='App-col'>
        <Link
          to='/waitlist'
          className='App-signup-button'
        >
          Sign Up
        </Link>
      </div>
    </div>
    <div className='App-row'>
      <div className='App-col'>
        <h2 className='App-sub-title'>
          Create APIs with plain English.
        </h2>
      </div>
    </div>
    <div className='App-row'>
      <div className='App-col' style={{ display: 'flex', justifyContent: 'center', }}>
        <img
          src='/screenshot.png'
          alt='screenshot'
          className='App-demo-video'
        />
      </div>
    </div>
  </div>;
}


function WaitlistPage() {
  return <div className="App">
    <div className='App-row'>
      <div className='App-col'>
        <Logo />
      </div>
      <div className='App-col'>
        <a
          href='/'
          className='App-signup-button'
        >
          Sign Up
        </a>
      </div>
    </div>
    <div className='App-row'>
      <div className='App-col'>
        <h2 className='App-sub-title'>
          Join the waitlist
        </h2>
      </div>
    </div>
    <div className='App-row'>
      <div className='App-col' style={{ display: 'flex', justifyContent: 'center', }}>
        <iframe
          src="https://docs.google.com/forms/d/e/1FAIpQLScRksxuXbtJg3KzV-oQDXGF-LEgtgU1wfLnk-VRAFQe3nrmVw/viewform?embedded=true"
          width="640"
          height="850"
          frameBorder={0}
          marginHeight={0}
          marginWidth={0}
        >
            Loading…
        </iframe>
      </div>
    </div>
  </div>;
}

function Logo() {
  return <Link to='/' style={{ textDecoration: 'none', color: 'black' }}>
    <h1 className='App-logo'>
      PlainAPI
    </h1>
  </Link>;
}

export default App;
