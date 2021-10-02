type CodeBlock = string;

type SMSTrigger = {
    type: 'SMS',
};

type HTTPTrigger = {
    type: 'HTTP',
    method: 'GET' | 'POST' | 'PATCH' | 'DELETE',
    url: string,
};

type Trigger = HTTPTrigger | SMSTrigger;

type Endpoint = {
    when: Trigger,
    def: string,
    impl: CodeBlock,
};

type APISettings = {
    version: '1',
    name: string,
    endpoints: Endpoint[],
};

const settings: APISettings = {
    version: '1',
    name: 'My API',
    endpoints: [
        {
            when: {
                type: 'HTTP',
                method: 'GET',
                url: '/users/{id}',
            },
            def: '# (id: number) -> User',
            impl: `
                user <- sql: get a user with id {id}
                if user is not defined
                    report 400: "No such user"
                otherwise
                    user <- python: user without the email field
                    return user
            `,
        },
        {
            when: {
                type: 'HTTP',
                method: 'GET',
                url: '/users/{id}',
            },
            def: '# (current user: User)',
            impl: `
                if the current user is not an admin
                    report 400: "Forbidden"
                user <- sql: get a user with email {email}
                if user is not defined
                    raise 400: No such user
                otherwise
                    return {user}
            `
        },
    ],
};

export default settings;

triggers:
    when:
        http GET at url /users/with-email/{email}
        requiring authentication
    do:

    when:
        http GET at url /users
        requiring authentication
    do:
        # (current user: User)
        if the current user is not an admin
            report 400: "Forbidden"
        report sql: all the users from the db

    when:
        http GET at url /users/email/{id}
        requiring auth
    do:
        # (current user: User)
        if the current user is not an admin and their id is not equal to {id}
            report 400 "Forbidden"
        return sql: the email of the user with id {id}

    when:
        http POST at url /users/signup
        requiring an email (string), and password (string) in the response body as JSON
    do:
        # (email: string, password: string) -> a user
        existing user = get a user with email equal to {email}
        if existing user is defined
            report "A user with that email already exists"
        if {password} is not a good password
            report "Bad password"
        hashed password <- func: hash {password}
        nickname <- func: get a random name
        now <- func: get the current utc time
        new user <- sql: create a new user (not admin) with nickname = {nickname}, created and updated set to {now}, email set to {email}, verified set to false, and a score of 0
        func: send verification email to {email} with {nickname}
        return {new user}

    when:
        http POST at url /users/login
        requiring an email (string) and password (string)
    do:
        user <- sql: get a user with email equal to {email}
        if user is not defined
            report "Invalid email or password"
        if the {password} doesn't match the user's hashed password
            report "Invalid email or password"
        token <- func: create a JWT token with sub = {email} and exp = 30 days from now
        return an object with access_token = {token}, token_type = "bearer", and id = the user's id
        
    when
        http DELETE at url /users/delete/{id}
        requires auth
    do:
        user <- sql: get a user with id {id}
        if user is not defined or user's id is not equal to the current user's id
            report "Invalid request"
        sql: delete the user with id {id}
        return "Ok"
