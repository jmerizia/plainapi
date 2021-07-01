import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
    logError,
    useBackend,
    fetchApiIdsForUser,
} from './utils/misc';
import Editor from './components/Editor';
import DataEditor from './components/DataEditor';
import { Endpoint } from './types';
import {
    API,
} from './generated';
import debounce from 'debounce';
// import {
//     BrowserRouter as Router,
//     Switch,
//     Route,
//     Link
// } from 'react-router-dom';
import Tooltip from '@material-ui/core/Tooltip';
import { withStyles, Theme } from '@material-ui/core/styles';


const IconTooltip = withStyles((theme: Theme) => ({
    tooltip: {
      backgroundColor: 'black',
      color: 'white',
      boxShadow: 'none',
      fontSize: '17px',
      fontWeight: 'bold',
    },
    arrow: {
        color: 'black',
    },
}))(Tooltip);


export default function App() {
    const { backend, currentUserId } = useBackend();
    const [api, setApi] = useState<API | null>(null);
    const [numApis, setNumApis] = useState<number | null>(null);
    const [previewLoading, setPreviewLoading] = useState(false);
    const iframeRef = useRef<HTMLIFrameElement>(null);
    const [showLoginStuff, setShowLoginStuff] = useState(false);
    const iframeSrc = 'http://localhost:3002/docs';
    const [page, setPage] = useState<'endpoints' | 'data' | 'functions'>('endpoints');

    const handleChange = async ({ title, endpoints }: { title: string, endpoints: Endpoint[] }) => {
        if (api) {
            setApi({ ...api, title, endpoints });
        }
    };

    const handleRestart = async () => {
        if (api && iframeRef.current) {
            setPreviewLoading(true);
            await backend.restartApiApiV0ApisRestartPost({ aPI: api });
            iframeRef.current.src = iframeSrc;
            setPreviewLoading(false);
        }
    };

    useEffect(() => {
        setApi({
            id: 1,
            title: 'My API 🚀',
            endpoints: [{
                value: '',
                url: '/',
                method: 'GET',
            }],
            userId: 1,
            created: new Date(),
            updated: new Date(),
        });
        // (async () => {
            // if (currentUserId) {
                // const apiIds = await fetchApiIdsForUser(backend, currentUserId);
                // setNumApis(apiIds.length);
                // if (apiIds.length > 0) {
                //     // just use the first for now
                //     const api = await backend.readApiApiV0ApisGetByIdGet({ apiId: apiIds[0] });
                //     setApi(api);
                // }
            // }
        // })().catch(logError);
    }, [currentUserId, backend]);

    const renderEndpointsEditor = () => {
        return <div className='editor-container'>
            { api &&
                <Editor
                    title={api.title}
                    endpoints={api.endpoints}
                    onChange={handleChange}
                    onRestart={handleRestart}
                    previewLoading={previewLoading}
                />
            }
            { showLoginStuff &&
                <LoginBox
                    numApis={numApis}
                    setApi={setApi}
                />
            }
        </div>;
    };

    const renderDataEditor = () => {
        return <div className='editor-container'>
            <DataEditor
                migrations={['first', 'second']}
                onChange={() => {}}
            />
        </div>;
    };

    const renderFunctionsEditor = () => {
        return <div className='editor-container'>
            functions
        </div>;
    };

    const renderEditor = () => {
        switch (page) {
            case 'endpoints':
                return renderEndpointsEditor();
            case 'data':
                return renderDataEditor();
            case 'functions':
                return renderFunctionsEditor();
            default:
                return null;
        }
    };

    return (
        <div className="container">
            <div className='left-bar'>
                <IconTooltip title='Endpoints' placement='right' arrow>
                    <div
                        className='left-bar-icon'
                        onClick={ev => {
                            setPage('endpoints');
                        }}
                        style={{
                            backgroundColor: page === 'endpoints' ? '#333' : undefined,
                        }}
                    >
                        <img src='/rocket.svg' width={30} height={30} alt='E' />
                    </div>
                </IconTooltip>
                <IconTooltip title='Data' placement='right' arrow>
                    <div
                        className='left-bar-icon'
                        onClick={ev => {
                            setPage('data');
                        }}
                        style={{
                            backgroundColor: page === 'data' ? '#333': undefined,
                        }}
                    >
                        <img src='/database_white.svg' width={30} height={30} alt='D' />
                    </div>
                </IconTooltip>
                <IconTooltip title='Functions' placement='right' arrow>
                    <div
                        className='left-bar-icon'
                        onClick={ev => {
                            setPage('functions');
                        }}
                        style={{
                            backgroundColor: page === 'data' ? '#333': undefined,
                        }}
                    >
                        &lambda;
                    </div>
                </IconTooltip>
            </div>
            { renderEditor() }
            <div
                className="preview-container"
                style={{
                    opacity: previewLoading ? 0.5 : undefined,
                    userSelect: previewLoading ? 'none' : undefined,
                }}
            >
                <iframe
                    title='preview'
                    ref={iframeRef}
                    className='preview-iframe'
                    src={iframeSrc}
                />
            </div>
            <div
                className='show-login-button'
                onClick={() => setShowLoginStuff(!showLoginStuff)}
            >v0.1.0</div>
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
        // await backend.signupUserApiV0UsersSignupPost({ email, password });
    };

    return <>
        { numApis === 0 &&
            <>
                <p>You have no APIs</p>
                <button
                    onClick={async ev => {
                        try {
                            if (currentUserId) {
                                // const api = await backend.createApiApiV0ApisCreatePost({
                                //     userId: currentUserId, title: 'My API',
                                //     serializedEndpoints: JSON.stringify([]),
                                // });
                                // setApi(api);
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
