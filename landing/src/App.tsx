import React from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from 'react-router-dom';
import {
  Container,
  Row,
  Col,
} from 'react-bootstrap'


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
  return <Container style={{ maxWidth: '850px' }} fluid="md">
    <Header />
    <Row>
      <div className='v-spacer' />
      <Col>
        <h2 className='center-text'>
          Create APIs with plain English.
        </h2>
      </Col>
      <div className='v-spacer' />
    </Row>
    <Row>
      <Col style={{ display: 'flex', justifyContent: 'center', }}>
        <video
          src='/demo-video.mov'
          autoPlay
          controls
          // alt='screenshot showcasing how the application allows converting English to API endpoints'
          className='App-demo-video'
        />
      </Col>
    </Row>
    <Row>
      <div className='v-spacer' />
    </Row>
    <Row>
      <Col xs={12} md={6}>
        <img
          src='/animation1.gif'
          // alt='screenshot showcasing how the application allows converting English to API endpoints'
          className='App-dynamic-image'
        />
      </Col>
      <Col xs={12} md={6}>
        <h2 className='font-italic margin-top-15'>
          Writing code is hard—explaining it is easy.
        </h2>
        <p>
          PlainAPI understands what you write and generates
          functions, classes, and SQL statements for you.
        </p>
      </Col>
    </Row>
    <Row>
      <div className='v-spacer' />
    </Row>
    <Row>
      <Col xs={{ span: 12, order: 2 }} md={{ span: 6, order: 1 }}>
        <h2 className='font-italic margin-top-15'>
          Type-Check your English
        </h2>
        <p>
          PlainAPI type-checks everything you write so you
          can work quickly and confidently.
        </p>
      </Col>
      <Col xs={{ span: 12, order: 1 }} md={{ span: 6, order: 2 }}>
        <img
          src='/screenshot-types.png'
          alt='screenshot showcasing how the application allows converting English to API endpoints'
          className='App-dynamic-image padding-20'
        />
      </Col>
    </Row>
    <Row>
      <div className='v-spacer-big' />
    </Row>
    <Row>
      <Col>
        <button
          onClick={ev => {
            window.location.href = '/waitlist';
          }}
          className='App-waitlist-button center-text'
        >
          Join the waitlist
        </button>
      </Col>
    </Row>
    <Row>
      <div className='v-spacer' />
    </Row>
    <Row>
      <Col>
        <h3 className='center-text'>
          We release this fall.
        </h3>
      </Col>
    </Row>
    <Footer />
  </Container>;
}

function WaitlistPage() {
  return <Container style={{ maxWidth: '850px' }}>
    <Header />
    <Row>
      <Col>
        <h2 className='center-text'>
          Join the waitlist
        </h2>
      </Col>
    </Row>
    <Row>
      <Col style={{ display: 'flex', justifyContent: 'center', }}>
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
      </Col>
    </Row>
    <Footer />
  </Container>;
}

function Logo() {
  return <Link to='/' style={{ textDecoration: 'none', color: 'black' }}>
    <h1 className='App-logo'>
      PlainAPI
    </h1>
  </Link>;
}

function Header() {
  return <Row>
    <Col xs={6}>
      <Logo />
    </Col>
    <Col>
      <a
        href='/waitlist'
        className='App-signup-button'
      >
        Sign Up
      </a>
    </Col>
  </Row>;
}

function Footer() {
  return <Row>
    <div className='v-spacer' />
  </Row>;
}

export default App;
