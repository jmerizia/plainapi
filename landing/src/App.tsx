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
        <Container style={{ maxWidth: '850px' }} fluid="md">
          <Header />
          <Switch>
            <Route path='/signup'>
              <WaitlistPage />
            </Route>
            <Route path='/'>
              <IndexPage />
            </Route>
          </Switch>
        </Container>
      </div>
    </Router>
  );
}

function IndexPage() {
  return <>

    {/* header */}
    <Row>
      <div className='v-spacer' />
      <Col>
        <h2 className='center-text'>
          Create APIs with plain English.
        </h2>
      </Col>
      <div className='v-spacer' />
    </Row>

    {/* demo */}
    <Row>
      <Col style={{ display: 'flex', justifyContent: 'center', }}>
        <video
          src='/demo-video.mov'
          controls={true}
          className='App-demo-video'
        />
      </Col>
    </Row>

    {/* row 1 */}
    <Row>
      <div className='v-spacer' />
    </Row>
    <Row>
      <Col xs={12} md={6}>
        <img
          src='/animation1.gif'
          alt='demo of the application converting English to code'
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

    {/* row 2 */}
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

    {/* footer */}
    <Row>
      <div className='v-spacer-big' />
    </Row>
    <Row>
      <Col>
        <button
          onClick={ev => {
            window.location.href = '/signup';
          }}
          className='App-waitlist-button center-text'
        >
          Signup for private beta
        </button>
      </Col>
    </Row>
    <Row>
      <div className='v-spacer' />
    </Row>
    <Row>
      <Col>
        <a href='https://jacob.merizian.com/why-plainapi.html'>
          <h3 className='center-text'>
            Learn more →
          </h3>
        </a>
      </Col>
    </Row>
    <Row>
      <div className='v-spacer' />
    </Row>
  </>;
}

function WaitlistPage() {
  return <>
    <Row>
      <Col style={{ display: 'flex', justifyContent: 'center', }}>
        <iframe
          src="https://docs.google.com/forms/d/e/1FAIpQLScRksxuXbtJg3KzV-oQDXGF-LEgtgU1wfLnk-VRAFQe3nrmVw/viewform?embedded=true"
          title='waitlist-form'
          width="640"
          height="1500"
          frameBorder={0}
          marginHeight={0}
          marginWidth={0}
        >
            Loading…
        </iframe>
      </Col>
    </Row>
  </>;
}


function Header() {
  return <Row>

    <Col xs={6} style={{ display: 'flex', }}>
      {/* logo */}
      <Link to='/' style={{ textDecoration: 'none', color: 'black' }}>
        <h1 className='logo'>
          PlainAPI
        </h1>
      </Link>

    </Col>

    <Col xs={6}>
      {/* signup link */}
      <a
        href='/signup'
        className='App-signup-button'
      >
        Sign Up
      </a>
    </Col>
  </Row>;
}

export default App;
