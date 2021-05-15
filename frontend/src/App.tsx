import React, { useCallback, useEffect, useState } from 'react';
import {
    logError,
    useBackend,
    fetchApiIdsForUser,
} from './utils';
import Editor from './Editor';
import { Endpoint } from './types';
import {
    API,
} from './generated';
import debounce from 'debounce';


export default function App() {
    const { backend, currentUserId, login, logout } = useBackend();
    const [api, setApi] = useState<API | null>(null);
    const [numApis, setNumApis] = useState<number | null>(null);

    const debouncedUpdateApi = debounce((payload: { apiId: number, title?: string, endpoints?: Endpoint[] }) => {
        backend.updateApiApiV0ApisUpdatePatch({
            apiId: payload.apiId,
            title: payload.title,
            serializedEndpoints: payload.endpoints && JSON.stringify(payload.endpoints),
        });
    }, 300);

    const handleChange = async (title: string, endpoints: Endpoint[]) => {
        if (api) {
            setApi({ ...api, title, endpoints });
            debouncedUpdateApi({ apiId: api.id, title, endpoints });
        }
    };

    useEffect(() => {
        (async () => {
            if (currentUserId) {
                const apiIds = await fetchApiIdsForUser(backend, currentUserId);
                setNumApis(apiIds.length);
                if (apiIds.length > 0) {
                    // just use the first for now
                    const api = await backend.readApiApiV0ApisGetByIdGet({ apiId: apiIds[0] });
                    setApi(api);
                }
            }
        })().catch(logError);
    }, [currentUserId, backend]);

    return (
        <div className="container">
            <div className='editor-container'>
                { api &&
                    <Editor
                        title={api.title}
                        endpoints={api.endpoints}
                        onChange={handleChange}
                    />
                }
                <LoginBox
                    numApis={numApis}
                    setApi={setApi}
                />
            </div>
            <div className="preview-container">
                <iframe
                    className='preview-iframe'
                    src='http://localhost:3001/api/v0/docs'
                />
            </div>
        </div>
    );
}


interface LoginBoxProps {
    numApis: number | null;
    setApi(api: API): void;
}

function LoginBox ({ numApis, setApi }: LoginBoxProps) {
    const { backend, currentUserId, login, logout } = useBackend();
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');

    const signup = async (email: string, password: string) => {
        await backend.signupUserApiV0UsersSignupPost({ email, password });
    };

    return <>
        { numApis === 0 &&
            <>
                <p>You have no APIs</p>
                <button
                    onClick={async ev => {
                        try {
                            if (currentUserId) {
                                const api = await backend.createApiApiV0ApisCreatePost({
                                    userId: currentUserId, title: 'My API',
                                    serializedEndpoints: JSON.stringify([]),
                                });
                                setApi(api);
                            }
                        } catch (err) {
                            logError(err);
                        }
                    }}
                >Create API</button>
                <br />
            </>
        }
        username: <input
            value={email}
            onChange={ev => setEmail(ev.target.value)}
        /><br />
        password: <input
            value={password}
            onChange={ev => setPassword(ev.target.value)}
        />
        <br />
        <button onClick={ev => {
            login(email, password);
        }}
        >login</button>
        <button onClick={ev => {
            signup(email, password);
            login(email, password);
        }}
        >signup</button>
        <button onClick={ev => {
            logout();
        }}
        >logout</button>
    </>;
}
