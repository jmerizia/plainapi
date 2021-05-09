import React, { useEffect, useState, useRef } from 'react';
import {
    Field,
    changeAPITitle,
    addEndpoint,
    removeEndpoint,
    changeEndpointTitle,
    addField,
    removeField,
    changeFieldValue,
    useAppDispatch,
    useAppSelector,
    Endpoint,
} from './redux';


export default function App() {
    const title: string = useAppSelector(state => state.title);
    const endpoints: Endpoint[] = useAppSelector(state => state.endpoints);
    const dispatch = useAppDispatch();

    const handleChangeTitle = (title: string) => {
        dispatch(changeAPITitle({ title }))
    };

    const handleAddEndpoint = (after: number) => {
        dispatch(addEndpoint({ after }))
    };

    return (
        <div className="App">
            <div className='App-editor'>
                <input
                    className='App-title-input'
                    value={title}
                    onChange={ev => handleChangeTitle(ev.target.value)}
                />
                {
                    endpoints.map((endpoint, idx) => {
                        return <div className='App-editor-row' key={idx}>
                            <EndpointComponent
                                endpointId={endpoint.id}
                            />
                        </div>;
                    })
                }
                <div className='App-editor-row'>
                    <button
                        className='App-add-endpoint-button'
                        onClick={ev => {
                            if (endpoints.length > 0) {
                                handleAddEndpoint(endpoints[endpoints.length - 1].id);
                            }
                        }}
                    >
                        <span className='App-add-endpoint-button-text'>+</span>
                    </button>
                </div>
            </div>
            <div className="App-preview">
                preview
            </div>
        </div>
    );
}


interface EndpointComponentProps {
    endpointId: number,
}

function EndpointComponent({ endpointId }: EndpointComponentProps) {
    const endpoint: Endpoint | null = useAppSelector(state => {
        const endpoints = state.endpoints.filter(endpoint => endpoint.id === endpointId);
        if (endpoints.length === 1) return endpoints[0];
        return null;
    });
    const [focusedFieldId, setFocusedFieldId] = useState<number>(-1);
    const dispatch = useAppDispatch();

    if (!endpoint) return null;

    const handleChangeTitle = (title: string) => {
        dispatch(changeEndpointTitle({ endpointId: endpoint.id, title: title }))
    };

    const handleDeleteEndpoint = (id: number) => {
        dispatch(removeEndpoint({ endpointId: id }));
    };

    const fields = endpoint.fields;

    return <div className='EndpointComponent-container'>
        <input
            className='EndpointComponent-title'
            placeholder={endpoint.title === '' ? 'name your endpoint...' : ''}
            value={endpoint.title}
            onChange={ev => handleChangeTitle(ev.target.value)}
        />
        {/* <div className='EndpointComponent-method'>
            {endpoint.method}
        </div> */}
        <button
            className='EndpointComponent-delete-button'
            onClick={ev => {
                handleDeleteEndpoint(endpoint.id);
            }}
        >
            <span className='EndpointComponent-delete-button-text'>x</span>
        </button>
        { fields.map((field, idx) => (
            <FieldComponent
                key={idx}
                lineNumber={idx+1}
                fieldId={field.id}
                focused={field.id === focusedFieldId}
                onFocus={setFocusedFieldId}
                onFocusPrev={() => {
                    if (idx > 0 && fields.length > 1) {
                        setFocusedFieldId(fields[idx - 1].id);
                    }
                }}
                onFocusNext={() => {
                    if (idx < fields.length - 1) {
                        setFocusedFieldId(fields[idx + 1].id);
                    }
                }}
            />
        )) }
    </div>;
}

interface FieldComponentProps {
    fieldId: number;
    lineNumber: number;
    focused: boolean;
    onFocus(id: number): void;
    onFocusPrev(): void;
    onFocusNext(): void;
}

function FieldComponent({ fieldId, lineNumber, focused, onFocus, onFocusPrev, onFocusNext }: FieldComponentProps) {
    const field: Field | null = useAppSelector(state => {
        for (const endpoint of state.endpoints) {
            const fields = endpoint.fields.filter(f => f.id === fieldId);
            if (fields.length === 1) return fields[0];
        }
        return null;
    });
    const inputRef = useRef<HTMLInputElement>(null);
    const dispatch = useAppDispatch();

    const handleChangeFieldValue = (id: number, value: string) => {
        dispatch(changeFieldValue({ fieldId: id, value }))
    };

    const handleAddField = (after: number): number => {
        const newId = Math.floor(Math.random()*10000);
        dispatch(addField({
            field: { id: newId, value: '', indent: 0, created: new Date(), updated: new Date(), },
            after,
        }));
        return newId;
    };

    const handleRemoveField = (id: number) => {
        dispatch(removeField({ fieldId: id }));
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
            onFocus={ev => onFocus(field.id)}
            className='FieldComponent-input'
            value={field.value}
            onChange={ev => handleChangeFieldValue(field.id, ev.target.value)}
            onKeyDown={ev => {
                if (ev.key === 'Enter') {
                    ev.preventDefault();
                    const newId = handleAddField(field.id);
                    onFocus(newId);
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