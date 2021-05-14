import React, { useEffect, useState, useMemo, useCallback } from 'react';
import {
    logError,
    useBackend,
    fetchApiIdsForUser,
    updateElementAt,
    insertElementAt,
    removeElementAt,
    swapElementsAt,
    moveElementFromTo,
} from './utils';
import { Endpoint } from './types';
import {
    API,
} from './generated';
import debounce from 'debounce';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import DragIcon from './icons/drag_indicator_black_24dp.svg';
import DeleteIcon from './icons/delete_black_24dp.svg';

// slate
import {
    Slate,
    Editable,
    withReact,
} from 'slate-react'
import {
  Transforms,
  createEditor,
  Node,
  Path,
  Element as SlateElement,
  Descendant,
  Editor as SlateEditor,
} from 'slate'
import { withHistory } from 'slate-history'
import {
    CustomEditor,
    TitleElement,
    ParagraphElement,
} from './types';


const withLayout = (editor: CustomEditor) => {
    const { normalizeNode } = editor;

    editor.normalizeNode = ([node, path]) => {
        if (path.length === 0) {
            if (editor.children.length < 1) {
                const title: TitleElement = {
                    type: 'title',
                    children: [{ text: 'Untitled' }],
                }
                Transforms.insertNodes(editor, title, { at: path.concat(0) })
            }

            if (editor.children.length < 2) {
                const paragraph: ParagraphElement = {
                    type: 'paragraph',
                    children: [{ text: '' }],
                }
                Transforms.insertNodes(editor, paragraph, { at: path.concat(1) })
            }

            for (const [child, childPath] of Node.children(editor, path)) {
                const type = childPath[0] === 0 ? 'title' : 'paragraph'
        
                if (SlateElement.isElement(child) && child.type !== type) {
                    const newProperties: Partial<SlateElement> = { type };
                    Transforms.setNodes(editor, newProperties, { at: childPath })
                }
            }
        }

        return normalizeNode([node, path])
    }

    return editor
}

const initialValue: Descendant[] = [
    {
      type: 'title',
      children: [{ text: 'Enforce Your Layout!' }],
    },
    {
      type: 'paragraph',
      children: [
        {
          text:
            'This example shows how to enforce your layout with domain-specific constraints. This document will always have a title block at the top and at least one paragraph in the body. Try deleting them and see what happens!',
        },
      ],
    },
]


export default function App() {
    const { backend, currentUserId, login, logout } = useBackend();
    const [api, setApi] = useState<API | null>(null);
    const [noApis, setNoApis] = useState(true);
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');

    const debouncedUpdateApi = debounce((payload: { apiId: number, title?: string, endpoints?: Endpoint[] }) => {
        backend.updateApiApiV0ApisUpdatePatch({
            apiId: payload.apiId,
            title: payload.title,
            serializedEndpoints: payload.endpoints && JSON.stringify(payload.endpoints),
        });
    }, 300);

    const handleChangeTitle = async (title: string) => {
        if (api) {
            setApi({ ...api, title, });
            debouncedUpdateApi({ apiId: api.id, title });
        }
    };

    const handleAddEndpoint = async (value: Endpoint, location: number) => {
        if (api) {
            const endpoints = insertElementAt(api.endpoints, value, location);
            setApi({ ...api, endpoints, });
            debouncedUpdateApi({ apiId: api.id, endpoints });
        }
    };

    const handleRemoveEndpoint = async (location: number) => {
        if (api) {
            const endpoints = removeElementAt(api.endpoints, location);
            setApi({ ...api, endpoints, });
            debouncedUpdateApi({ apiId: api.id, endpoints });
        }
    };

    const handleUpdateEndpoint = async (value: Endpoint, location: number) => {
        if (api) {
            const endpoints = updateElementAt(api.endpoints, value, location);
            setApi({ ...api, endpoints, });
            debouncedUpdateApi({ apiId: api.id, endpoints });
        }
    }

    const handleMoveEndpoint = async (a: number, b: number) => {
        if (api) {
            console.log(a, b);
            const endpoints = moveElementFromTo(api.endpoints, a, b);
            console.log(endpoints.map(e => e.id), api.endpoints.map(e => e.id));
            setApi({ ...api, endpoints, });
            debouncedUpdateApi({ apiId: api.id, endpoints });
        }
    };

    useEffect(() => {
        (async () => {
            if (currentUserId) {
                console.log(currentUserId);
                const apiIds = await fetchApiIdsForUser(backend, currentUserId);
                if (apiIds.length === 0) {
                    setNoApis(true);
                } else {
                    // just use the first for now
                    setNoApis(false);
                    const api = await backend.readApiApiV0ApisGetByIdGet({ apiId: apiIds[0] });
                    setApi(api);
                }
            }
        })().catch(logError);
    }, [currentUserId, backend]);

    const signup = async (email: string, password: string) => {
        await backend.signupUserApiV0UsersSignupPost({ email, password });
    };

    return (
        <div className="container">
            { api &&
                <Editor
                    title={api.title}
                    endpoints={api.endpoints}
                    onUpdateEndpoint={handleUpdateEndpoint}
                    onChangeTitle={handleChangeTitle}
                    onAddEndpoint={handleAddEndpoint}
                    onRemoveEndpoint={handleRemoveEndpoint}
                    onMoveEndpoint={handleMoveEndpoint}
                />
            }
            <div className="preview">
                { noApis &&
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
                                        setNoApis(false);
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
                <button onClick={ev => {
                    logout();
                }}
                >logout</button>
            </div>
        </div>
    );
}

interface EditorProps {
    title: string;
    endpoints: Endpoint[];
    onChangeTitle(title: string): void;
    onUpdateEndpoint(value: Endpoint, location: number): void;
    onAddEndpoint(value: Endpoint, location: number): void;
    onRemoveEndpoint(location: number): void;
    onMoveEndpoint(a: number, b: number): void;
}

const Element = ({ attributes, children, element }: { attributes: React.Attributes, children: React.ReactChildren, element: React.ReactElement }) => {
    switch (element.type) {
        case 'title':
            return <h2 {...attributes}>{children}</h2>
        case 'paragraph':
            return <p {...attributes}>{children}</p>
        default:
            return null;
    }
}

function Editor({
    title, endpoints, onChangeTitle, onUpdateEndpoint, onAddEndpoint, onRemoveEndpoint, onMoveEndpoint,
}: EditorProps) {
    const [value, setValue] = useState(initialValue);
    const editor = useMemo(
        () => withLayout(withHistory(withReact(createEditor() as any))),
        []
    );
    const renderElement = useCallback(props => <Element {...props} />, [])

    const handleDragEnd = (result: DropResult) => {
        console.log(endpoints.map(e => e.id));
        if (!result.destination) {
            return;
        }
        onMoveEndpoint(result.source.index, result.destination.index);
    };

    return <div className='editor'>
        <input
            className='title-input'
            value={title}
            onChange={ev => onChangeTitle(ev.target.value)}
        />
        <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="droppable">
                {(provided, snapshot) => (
                    <div
                        {...provided.droppableProps}
                        ref={provided.innerRef}
                    >
                        {endpoints.map((endpoint, idx) => (
                            <Draggable key={endpoint.id.toString()} draggableId={endpoint.id.toString()} index={idx}>
                                {(provided, snapshot) => (
                                    <div
                                        ref={provided.innerRef}
                                        {...provided.draggableProps}
                                        {...provided.dragHandleProps}
                                        style={{
                                            ...provided.draggableProps.style,
                                            userSelect: 'none',
                                            backgroundColor: snapshot.isDragging ? '#eee' : 'white',
                                        }}
                                        className='editor-row'
                                    >
                                        <div className='editor-endpoint'>
                                            <img
                                                src={DragIcon}
                                                className='editor-drag-bar'
                                            />
                                            <input
                                                className='editor-input'
                                                value={endpoint.value}
                                                onChange={ev => onUpdateEndpoint({ ...endpoint, value: ev.target.value, }, idx)}
                                            />
                                            <button
                                                className='editor-remove-button'
                                                onClick={ev => {
                                                    ev.preventDefault();
                                                    onRemoveEndpoint(idx);
                                                }}
                                            >
                                                <img
                                                    src={DeleteIcon}
                                                    className='editor-remove-icon'
                                                />
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </Draggable>
                        ))}
                        {provided.placeholder}
                    </div>
                )}
            </Droppable>
        </DragDropContext>
        <div className='editor-row'>
            <button
                className='add-endpoint-button'
                onClick={ev => {
                    onAddEndpoint({ id: Math.floor(Math.random()*10000), method: 'GET', value: '' }, endpoints.length);
                }}
            >
                <span className='add-endpoint-button-text'>+</span>
            </button>
        </div>
        <Slate editor={editor} value={value} onChange={value => setValue(value)}>
            <Editable
                renderElement={renderElement}
                placeholder="Enter a title…"
                spellCheck
                autoFocus
            />
        </Slate>
    </div>;
}
