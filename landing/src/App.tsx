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
            <Route path='/why'>
              <WhyPage />
            </Route>
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
        <a href='/why'>
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

function WhyPage() {
  return <>
    <Row>
      <div className='v-spacer' />
      <Col>
        <h2 className='center-text'>
          Why PlainAPI?
        </h2>
      </Col>
    </Row>
    <Row>
      <Col>
        <div className='article-container'>
          <p>
            For the past year, I have been working on an AI startup for the physical therapy space.
            AI startups are strange beasts that require pipelines for injesting data,
            labeling/relabeling data, and building up datasets—and that's all separate from the final production
            application!
          </p>
          <p>
            After a while, I found myself maintaining 3-4 different backend applications,
            all of which sprouted out of the same basic boilerplate.
            I tried by best to reuse as much as possible, but that made things very complicated
            to untangle when applications needed to diverge.
          </p>
          <p>
            Overtime, I started seeing patterns in web applications.
            I formed a dependence on type safety to ensure correctness of my applications
            as opposed to comprehensive test suites, which I did not have the time to write.
            I also started using code generation tools for JSON validation,
            backend/frontend communication (with OpenAPI schemas),
            and for database upkeep.
          </p>
          <p>
            I developed a lot of useful patterns, but I couldn't help but think that I could take
            things much further.
          </p>
          <h3 className='article-title'>Code generation will eat software</h3>
          <p>
            Broadly speaking, code generation is the automated production of code from other code.
            It's a simple tradeoff: convert from a high level language (more understandable and faster to write)
            to one that is lower level (less understandable and slower to write),
            forsaking some efficiency and program size.
            Everything including compiling C into assembly,
            transpiling TypeScript into JavaScript, and
            macro expansion (i.e. in Rust)
            is fundamentally just code generation.
          </p>
          <p>
            Up until today, all production-ready code generation tools work with <i>structured</i> languages (more or less).
            With the emergence of intelligent text completion/translation neural networks such as GPT-3,
            we can begin to build code generation tools from <i>very unstructured</i> languages
            to structured ones.
            This can then democratize the production of web applications,
            while still being a versatile alternative to writing whole web applications from
            the ground up.
          </p>
          <h3 className='article-title'>A new paradigm for no-code tools</h3>
          {/* <p>
            Many people solving this problem seem to think that it hinges on some highly tuned and complicated
            neural network for converting sentences to code.
            But that approach sidesteps the human-computer interaction component
            that language creators understand very well.
            The problem is not just about teaching the computer,
            but also teaching the user how to use the tool properly.
          </p>
          <p>
            The way this problem will actually be solved is by patching together existing
            natural language processing algorithms in new and clever ways.
            It turns out that GPT-3 can accurately generate SQL from a sentence description.
            The resulting SQL can then be parsed manually to extract return types,
            which can then be used for data validation and safely connecting multiple statements.
            We can use GPT-3 to parse out conditional logic and determine the relationships
            between different parts of the description.
            We can even ask the author questions to clarify ambiguities.
            We can build a whole new kind of parser for a new kind of language
            that is remarkably similar to plain language.
          </p> */}
          <p>
            {/* There is also something to be said of other no-code/low-code platforms that depend on GUIs. */}
            Programmers notoriously prefer terminals over GUIs and
            languages over node-based programming, but why?
            These seem like strange affinities, both of which I admit to having myself.
            It may be convenient to conclude that these are just remnants of the hacker culture from the 90's,
            but I think the reason {' '}
            <a href='https://news.ycombinator.com/item?id=14482988' target='_blank'>
              is more fundamental
            </a>.
            Text enables several meta-language features, such as comparing, searching, summarizing, filtering, and organizing.
            It opens the door for a wide range of tools to enhance productivity and allows much more expressivity.
            You can automate text in ways that would be intractable with GUIs.
          </p>
          <p>
            This is not to say that visual augmentation is bad.
            The best editors make editing text interactive and describe what's happening with images
            (via auto completion, type defs on hover, debugging, jump to definition, etc.).
            And thus, it's the goal of PlainAPI to bring the efficiency of language to no-code tools,
            or in other words, to make the world's first IDE for unstructured language.
          </p>
          <h3 className='article-title'>Advantages of GPT-3</h3>
          {/* <p>
            With GPT-3, intelligent systems based on natural language can be constructed extremely quickly.
            Many people studying this problem seem to think it will require a highly tuned neural network
            that translates natural language to code.
            However, that would require acquiring a dataset, training a model on that dataset,
            and then slowly adding more data to the dataset as people use the service.
            That can easily turn into years of work
            and offers very little flexibility.
            GPT-3 can generate code from an explanation into several different programming languages,
            answer meta-questions about the relationships between objects in a sentence,
            and even generate explanations of what snippets of code do.
            And all of this can be done in a matter of minutes.
          </p> */}
          {/* <p>
            But how exactly do you use an AGI text-completion algorithm such as GPT-3 to write code?
            Let's suppose we take the traditional machine learning approach and build a text to code dataset.
            Then, we deploy our model and find several examples of mistakes that the algorithm is making.
            We will need to collect dozens of examples per mistake so that our algorithm can properly learn,
            which takes time and effort to curate the dataset.<sup>1</sup>{' '}
            So this is the key insight about GPT-3: 
            The prompt acts as a reduced training dataset, which can be determined at <i>query time</i>.
            A single example in the prompt replaces hundreds of examples collected in the wild,
            because of the amazing inference capabilities of GPT-3.
          </p> */}
          <p>
            It is stunning what GPT-3 is able to infer from a small amount of data.
            In the traditional machine learning approach,
            we would collect a large dataset of examples,
            deploy our model,
            then feed the model tons more data in order to correct the model.<sup><a href='#footer'>1</a></sup>{' '}
            With GPT-3, a single example can serve for hundreds in a traditional dataset,
            since GPT-3 can infer a lot more than what it is given.
            It would simply take too long to try and solve this problem with a highly tuned
            neural network.
          </p>
          <p>
            Moreover, GPT-3 introduces a paradigm shift in that the training dataset no longer has to be a fixed set of examples;
            the training set can be manipulated at <i>query time</i>.
            This means you can tune the inference on a per-customer basis at no additional cost.<sup><a href='#footer'>2</a></sup>
          </p>
          {/* <p>
            But why is code generation so widely used?
            The catch is that code usually takes up more space, and can be more difficult to optimize.
            There's actually an inverse relationship between output program size and efficiency
            when generating (or writing!) code.<sup>1</sup>{' '}
            Human programmers can only write so many functions each day,
            and so they will <i>reuse</i> functions and patterns whenever possible (i.e., with the use of generics).
            This is why we see so many code generation tools around languages that don't support generics (i.e, Golang).
          </p> */}
          {/* There will be a wave of change in the next 10 years
            as the AI community moves towards larger models and datasets.
            This trend will change the way AI startups fundamentally operate.
            Companies of the future will leverage new algorithms that come
            equipped with super-human priors that can be patched together
            in much the same way different digital services can be integrated with one another. */}
          <h3 className='article-title'>Will this affect my job security?</h3>
          <p>
            I don't anticipate programmers to lose their jobs anytime soon,
            but there will be a major shift in the programming workflow in certain subfields.
            Honestly, the tooling and best practices for the web changes on a monthly basis.
            In 3 years, it's unlikely anyone will still be using the same front-end frameworks
            at the current rate anyways.
            Programmers will be important for tasks closer to hardware
            or that require low-level performance hacks.
            For now, AGI can shortcut the process of going from idea to code,
            but the idea must come from somewhere.
            That can be done too, but the goal should be to tackle the low hanging fruit first.
          </p>
          <p style={{ marginBottom: '0px' }}>
            <b>
              So, in short, the mission is:
            </b>
          </p>
          <p style={{ padding: '15px', marginBottom: '0px' }}>
            <i>
              Build an IDE for writing and maintaining natural language that compiles down to a functioning API deployment.
            </i>
          </p>
          <p>
            How hard could it be?
          </p>
          <br />
          <hr />
          <br />
          <div style={{ color: 'grey' }} id='footer'>
            <p>
              <sup>1</sup> I summarized this for brevity. There are a lot more tasks I'm leaving out:
              Removing old datapoints when the training starts to take more than a few days,
              relabeling old data points, etc.
            </p>
            <p>
              <sup>2</sup> You can actually do way more.
              You can chain queries together in clever ways
              (i.e., one layer for parsing conditionals, another for parsing SQL, etc.).
              You can also build decision trees <i>within</i> GPT-3 completion queries.
            </p>
          </div>
        </div>
      </Col>
      <div className='v-spacer' />
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

      {/* navbar */}
      <div className='top-bar'>
        <div className='top-link-wrapper'>
          <Link to='/why' className='top-link'>
            Why?
          </Link>
        </div>
      </div>
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
