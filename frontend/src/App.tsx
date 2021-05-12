import { current } from 'immer';
import React, { useEffect, useState, useRef } from 'react';
import { idText } from 'typescript';
import {
    findApi,
    findEndpoint,
    findField,
    useAppDispatch,
    useAppSelector,
    actions,
} from './redux';
import {
    API,
    Endpoint,
    Field,
} from './types';
import {
    logError,
    useBackend,
    randomRecordId,
    fetchApi,
    fetchApiIdsForUser,
} from './utils';


const MAX_LENGTH = 60;

export default function App() {
    const { backend, currentUserId, login, logout } = useBackend();
    const apis = useAppSelector(state => state.apis);
    const api = useAppSelector(state => state.apis.length > 0 ? state.apis[0] : undefined);
    const currentUser = useAppSelector(state => state.currentUser);
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const dispatch = useAppDispatch();

    const loadApis = async () => {
        if (currentUserId) {
            const apiIds = await fetchApiIdsForUser(backend, currentUserId);
            const apis = await Promise.all(apiIds.map(async apiId => await fetchApi(backend, apiId)));
            dispatch(actions.setAPIs({ apis }));
        }
    };

    useEffect(() => {
        (async () => {
            await loadApis();
        })().catch(logError);
    }, [currentUserId]);

    const signup = async (email: string, password: string) => {
        const user = await backend.signupUserApiV0UsersSignupPost({ email, password });
        login(email, password);
    };

    return (
        <div className="App">
            { api &&
                <Editor
                    apiId={api.id}
                />
            }
            <div className="App-preview">
                { apis.length === 0 &&
                    <>
                        <p>You have no APIs</p>
                        <button
                            onClick={async ev => {
                                try {
                                    if (currentUserId) {
                                        await backend.createApiApiV0ApisCreatePost({
                                            userId: currentUserId, title: 'My API',
                                        });
                                        await loadApis();
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
                <button onClick={ev => {
                    login(email, password);
                }}
                >login</button>
                <button onClick={ev => {
                    signup(email, password);
                    login(email, password);
                }}
                >signup</button>
            </div>
        </div>
    );
}

interface EditorProps {
    apiId: string,
}

function Editor({ apiId }: EditorProps) {
    const { backend, currentUserId, login, logout } = useBackend();
    const title = useAppSelector(state => findApi(state, apiId)?.title);
    const api = useAppSelector(state => findApi(state, apiId));
    const dispatch = useAppDispatch();

    const handleChangeTitle = async (title: string) => {
        if (api && api.realId != 'unknown') {
            dispatch(actions.changeAPITitle({ apiId, title }))
            await backend.updateApiApiV0ApisUpdatePatch({ apiId: api.realId, title })
        }
    };

    const handleAddField = async (endpointId: string, location: number, value: string) => {
        if (api && api.realId != 'unknown') {
            dispatch(actions.addField({ apiId, endpointId, location, value, indent: 0 }));
            await backend.createFieldApiV0FieldCreatePost({ apiId: api.realId, endpointId: end, value, location })
        }
    };

    const handleAddEndpoint = async (location: number) => {
        const title = 'New Endpoint';
        const method = 'GET';
        dispatch(actions.addEndpoint({ apiId, location, title, method }))
        const endpoint = await backend.createEndpointApiV0EndpointCreatePost({ apiId, location, title, method, });
        await handleAddField(endpoint.id, 0, '');
    };

    return <div className='App-editor'>
        <input
            className='App-title-input'
            value={api?.title || 'loading...'}
            onChange={ev => handleChangeTitle(ev.target.value)}
        />
        {
            api?.endpoints.map((endpoint, idx) => {
                return <div className='App-editor-row' key={idx}>
                    <EndpointComponent
                        apiId={apiId}
                        endpointId={endpoint.id}
                    />
                </div>;
            })
        }
        <div className='App-editor-row'>
            <button
                className='App-add-endpoint-button'
                onClick={ev => {
                    if (api) {
                        handleAddEndpoint(api.endpoints.length);
                    } else {
                        handleAddEndpoint(0);
                    }
                }}
            >
                <span className='App-add-endpoint-button-text'>+</span>
            </button>
        </div>
    </div>;
}


interface EndpointComponentProps {
    apiId: number,
    endpointId: number,
}

function EndpointComponent({ apiId, endpointId }: EndpointComponentProps) {
    const { backend, currentUserId, login, logout } = useBackend();
    const endpoint = useAppSelector(state => findEndpoint(state, apiId, endpointId));
    const [focusedFieldLocation, setFocusedFieldLocation] = useState<number>(-1);
    const dispatch = useAppDispatch();

    const handleChangeTitle = async (title: string) => {
        dispatch(actions.changeEndpointTitle({ apiId, endpointId, title }))
        await backend.updateEndpointApiV0EndpointUpdatePatch({ apiId, endpointId, title });
    };

    const handleDelete = async () => {
        dispatch(actions.removeEndpoint({ apiId, endpointId }));
        await backend.deleteEndpointApiV0EndpointDeleteDelete({ apiId, endpointId });
    };

    return <div className='EndpointComponent-container'>
        <input
            className='EndpointComponent-title'
            placeholder={endpoint?.title || ''}
            value={endpoint?.title || ''}
            onChange={async ev => {
                try {
                    await handleChangeTitle(ev.target.value)
                } catch (err) {
                    logError(err);
                }
            }}
        />
        {/* <div className='EndpointComponent-method'>
            {endpoint.method}
        </div> */}
        <button
            className='EndpointComponent-delete-button'
            onClick={async ev => {
                try {
                    await handleDelete();
                } catch (err) {
                    logError(err);
                }
            }}
        >
            <span className='EndpointComponent-delete-button-text'>x</span>
        </button>
        { endpoint?.fields.map((field, idx) => (
            <FieldComponent
                key={idx}
                lineNumber={idx+1}
                apiId={apiId}
                endpointId={endpointId}
                fieldId={field.id}
                focused={idx === focusedFieldLocation}
                onFocus={setFocusedFieldLocation}
                onFocusPrev={() => {
                    if (endpoint) {
                        if (idx > 0) {
                            setFocusedFieldLocation(idx - 1);
                        }
                    }
                }}
                onFocusNext={() => {
                    if (endpoint) {
                        if (idx < endpoint.fields.length - 1) {
                            setFocusedFieldLocation(idx + 1);
                        }
                    }
                }}
            />
        )) }
    </div>;
}

interface FieldComponentProps {
    apiId: number;
    endpointId: number;
    fieldId: number;
    lineNumber: number;
    focused: boolean;
    onFocus(id: number): void;
    onFocusPrev(): void;
    onFocusNext(): void;
}

function FieldComponent({ apiId, endpointId, fieldId, lineNumber, focused, onFocus, onFocusPrev, onFocusNext }: FieldComponentProps) {
    const { backend, currentUserId, login, logout } = useBackend();
    const field: Field | undefined = useAppSelector(state => findField(state, apiId, endpointId, fieldId));
    const inputRef = useRef<HTMLInputElement>(null);
    const dispatch = useAppDispatch();

    const handleChangeFieldValue = async (id: number, value: string) => {
        if (value.length <= MAX_LENGTH) {
            dispatch(actions.changeFieldValue({ apiId, endpointId, fieldId: id, value }))
            await backend.updateFieldApiV0FieldUpdatePatch({ apiId, endpointId, fieldId, value, });
        }
    };

    const handleAddField = async (location: number) => {
        const value = '';
        const indent = 0;
        dispatch(actions.addField({ apiId, endpointId, location, value, indent }));
        await backend.createFieldApiV0FieldCreatePost({ apiId, endpointId, location, value });
    };

    const handleRemoveField = async (id: number) => {
        dispatch(actions.removeField({ apiId, endpointId, fieldId: id }));
        await backend.deleteFieldApiV0FieldDeleteDelete({ apiId, endpointId, fieldId });
    };

    useEffect(() => {
        if (inputRef.current && focused) {
            inputRef.current.focus();
        }
    }, [focused, inputRef]);

    if (!field) return null;

    return <p className='FieldComponent-container'>
        <span className='FieldComponent-line-number'>
            {lineNumber < 10 ? ' ' + lineNumber.toString() : lineNumber}
        </span>
        <input
            ref={inputRef}
            placeholder={lineNumber === 1 ? 'type something...' : ''}
            onFocus={ev => onFocus(field.location)}
            className='FieldComponent-input'
            value={field.value}
            onChange={ev => handleChangeFieldValue(field.id, ev.target.value)}
            onKeyDown={ev => {
                if (ev.key === 'Enter') {
                    ev.preventDefault();
                    handleAddField(field.location+1);
                    onFocus(field.location+1);
                }
                if (ev.key === 'ArrowUp') {
                    onFocusPrev();
                }
                if (ev.key === 'ArrowDown') {
                    onFocusNext();
                }
                if (ev.key === 'Backspace') {
                    if (field.value === '' && lineNumber > 1) {
                        onFocusPrev();
                        handleRemoveField(field.id);
                    }
                }
                if (ev.key === 'Tab') {
                    ev.preventDefault();
                }
            }}
        />
    </p>;
}