# PlainAPI

PlainAPI is a compiler and IDE for a new kind of programming language that incorporates natural language.

Using recent advancements in language models, we are able to build

Note: You will need to be in the OpenAI API Beta program in order to use this.
If you are not in the program and would still like to use this,
sign up at [plainapi.co](https://plainapi.co).


## Installation

You should have Python 3.6+ to run this.

Run `pip install plainapi` in your terminal to get started.

## Generate an API

Run `plain init` in your terminal
to get started with a new project in the local directory.
This will create some initial boilerplate.

## Development roadmap

### short term

- [ ] language features:
    - [x] endpoint method and url
    - [x] if/else
    - [x] raise error
    - [x] boolean expressions
    - [x] python expressions
    - [ ] function calls
    - [ ] return statements
- [ ] deployment management
    - [ ] adding migrations
    - [ ] start/stop/restart commands
- [ ] language model backends
    - [x] GPT-3
    - [ ] GPT-J
- [ ] efficiency
    - [ ] parallelize endpoint parsing
- [ ] better error handling
- [ ] init command for quick start
- [ ] standard library
    - [ ] getting current date/time
    - [ ] bcrypt hashing
    - [ ] JWT
    - [ ] authentication
- [ ] repo management
    - [ ] GitHub Actions CI
    - [ ] tests (with cached completions?)

### long term
- web IDE
- language server support
- modules/packages
- explore other text-completion language models (something machine-local?)
