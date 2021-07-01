# PlainAPI

This is a tool that lets you create APIs using English language.
It uses GPT3 to translate between user defined queries and SQL statements.

Note: You will need to be in the OpenAI API Beta program in order to use this.
If you are not in the program and would still like to use this,
sign up at [plainapi.co](https://plainapi.co).


## Installation

You should have Python 3.6+ to run this.

Run
`pip install git+https://github.com/jmerizia/plainapi.git#egg=plainapi`
in your terminal to get started.

## Generate an API

Run `plain init` in your terminal
to get started with a new project in the local directory.
This will create some initial boilerplate.

## Development roadmap

### short term

- [ ] language features:
    - [x] endpoint method and url
    - [ ] if/else
    - [ ] raise error
    - [ ] boolean expressions
    - [ ] function calls
    - [ ] return statements
- [ ] deployment management
    - [ ] adding migrations
    - [ ] start/stop/restart commands
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
