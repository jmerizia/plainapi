import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { endpointsEqual, listsEqual, updateElementAt } from './utils';
import {
  Transforms,
  createEditor,
  Node,
  Element as SlateElement,
  Descendant,
} from 'slate'
import { withHistory } from 'slate-history'
import {
    Endpoint,
    CustomEditor,
    TitleElement,
    EndpointElement,
} from './types';
import { RenderElementProps } from 'slate-react/dist/components/editable';
import RegenIcon from './icons/sync_white_24dp.svg';
import { EndOfLineState } from 'typescript';
import getCaretCoordinates from 'textarea-caret';
import { OpenDirOptions } from 'fs';
import { listenerCount } from 'events';


export interface EditorProps {
    title: string;
    endpoints: Endpoint[];
    onChange(payload: { title: string, endpoints: Endpoint[] }): void;
    onRestart(): void;
    previewLoading: boolean;
}

export default function Editor({
    title, endpoints, onChange, onRestart, previewLoading
}: EditorProps) {

    useEffect(() => {
        if (endpoints.length === 0) {
            const newEndpoint: Endpoint = {
                method: '',
                url: '',
                value: '',
            };
            onChange({ title, endpoints: [newEndpoint] });
        }
    }, []);

    return <div className='editor'>
        <button
            className='regen-button'
            onClick={onRestart}
        >
            <span className='regen-button-text'>
                Regen
            </span>
            <img
                className={`regen-button-icon ${previewLoading ? 'spinning' : ''}`}
                src={RegenIcon}
                alt=''
            />
        </button>
        <input
            className='input-base'
            value={title}
            onChange={ev => onChange({ title: ev.target.value, endpoints })}
        />
        {
            endpoints.map((endpoint, idx) => (
                <EndpointEditor
                    endpoint={endpoint}
                    onChange={endpoint => onChange({
                        endpoints: updateElementAt(endpoints, endpoint, idx),
                        title,
                    })}
                    onRegen={onRestart}
                />
            ))
        }
        <button
            onClick={ev => {
                const newEndpoint = {
                    method: '',
                    url: '/',
                    value: '',
                };
                onChange({ title, endpoints: [...endpoints, newEndpoint] });
            }}
        >
            +
        </button>
    </div>;
}


interface EndpointEditorProps {
    endpoint: Endpoint;
    onChange(endpoint: Endpoint): void;
    onRegen(): void;
}

function EndpointEditor({ endpoint, onChange, onRegen }: EndpointEditorProps) {

    const dispatcher = useMemo(() => new FocusDispatcher<'method' | 'url' | 'value'>(), []);

    return <div>
        <div style={{ display: 'flex', alignContent: 'start' }}>
            <div style={{ padding: '5px' }}>
                <Field
                    value={endpoint.method}
                    onChange={method => onChange({ ...endpoint, method })}
                    onPrevField={() => {}}
                    onNextField={() => dispatcher.focus('url')}
                    renderedStyle={getMethodStyle(endpoint.method)}
                    inputClassName='input-method'
                    renderedClassName='rendered-method'
                    dispatcher={dispatcher}
                    dispatcherType={'method'}
                    onRegen={onRegen}
                />
            </div>
            <div style={{ flex: 1, padding: '5px' }}>
                <Field
                    value={endpoint.url}
                    onChange={url => onChange({ ...endpoint, url })}
                    onPrevField={() => dispatcher.focus('method')}
                    onNextField={() => dispatcher.focus('value') }
                    inputClassName='input-url'
                    renderedClassName='rendered-url'
                    dispatcher={dispatcher}
                    dispatcherType={'url'}
                    onRegen={onRegen}
                />
            </div>
        </div>
        <div style={{ display: 'flex', alignContent: 'start' }}>
            <div style={{ flex: 1, padding: '5px' }}>
                <Field
                    value={endpoint.value}
                    onChange={value => onChange({ ...endpoint, value })}
                    onPrevField={() => dispatcher.focus('url')}
                    onNextField={() => {}}
                    inputClassName='input-value'
                    renderedClassName='rendered-value'
                    dispatcher={dispatcher}
                    dispatcherType={'value'}
                    onRegen={onRegen}
                />
            </div>
        </div>
    </div>;
}


function getMethodStyle(method: string): { backgroundColor?: string, color: string } {
    switch (method) {
        case 'POST':
            return { backgroundColor: 'green', color: 'white' };
        case 'GET':
            return { backgroundColor: 'blue', color: 'white' };
        case 'PUT':
            return { backgroundColor: 'orange', color: 'white' };
        case 'PATCH':
            return { backgroundColor: 'orange', color: 'white' };
        case 'DELETE':
            return { backgroundColor: 'red', color: 'white' };
        default:
            return { color: 'red' };
    }
}


interface FieldProps<T> {
    value: string;
    onChange(value: string): void;
    onPrevField(): void;
    onNextField(): void;
    onRegen(): void;
    inputStyle?: React.CSSProperties;
    renderedStyle?: React.CSSProperties;
    inputClassName?: string;
    renderedClassName?: string;
    dispatcher?: FocusDispatcher<T>;
    dispatcherType?: T;
}

function Field<T>({
    value,
    onChange,
    onPrevField,
    onNextField,
    onRegen,
    inputStyle,
    renderedStyle,
    inputClassName,
    renderedClassName,
    dispatcher,
    dispatcherType,
}: FieldProps<T>) {
    const inputRef = useRef<HTMLInputElement>(null);
    const [editing, setEditing] = useState(false)
    const [lastClickLeft, setLastClickLeft] = useState(0);

    useEffect(() => {
        if (dispatcher && dispatcherType) {
            dispatcher.listen(dispatcherType, () => {
                setEditing(true);
            });
        }
    }, [dispatcher, dispatcherType]);

    useEffect(() => {
        if (inputRef.current) {
            if (editing) {
                inputRef.current.focus();
            }
        }
    }, [inputRef, editing]);

    useEffect(() => {
        if (inputRef.current && editing) {
            let newPos = 0;
            let prevLeft = 0;
            let curLeft = getCaretCoordinates(inputRef.current, newPos).left;
            while (newPos < inputRef.current.value.length && curLeft < lastClickLeft) {
                newPos++;
                const caret = getCaretCoordinates(inputRef.current, newPos);
                prevLeft = curLeft;
                curLeft = caret.left;
            }
            if (Math.abs(prevLeft - lastClickLeft) < Math.abs(curLeft - lastClickLeft)) {
                newPos--;
            }
            inputRef.current.selectionStart = newPos;
            inputRef.current.selectionEnd = newPos;
        }
    }, [inputRef, editing, lastClickLeft]);

    return editing ?
        <input
            className={'input-base ' + (inputClassName || '')}
            ref={inputRef}
            value={value}
            onChange={ev => onChange(ev.target.value)}
            onBlur={ev => {
                ev.preventDefault();
                setEditing(false);
            }}
            onKeyDown={ev => {
                if (ev.key === 'Enter') {
                    if (inputRef.current) {
                        inputRef.current.blur();
                    }
                }
                if (ev.key === 'Tab') {
                    ev.preventDefault();
                    if (ev.shiftKey) {
                        onPrevField();
                    } else {
                        onNextField();
                    }
                }
                if (ev.key === 'Enter') {
                    if (ev.metaKey || ev.ctrlKey) {
                        ev.preventDefault();
                        onRegen();
                    }
                }
            }}
            style={inputStyle}
        />
    :
        <div
            className={'rendered-base ' + (renderedClassName || '')}
            onClick={ev => {
                ev.preventDefault();
                setEditing(true);
                const rect = (ev.target as HTMLDivElement).getBoundingClientRect();
                setLastClickLeft(ev.clientX - rect.left);
            }}
            style={renderedStyle}
        >
            {value}
        </div>;
}


class FocusDispatcher<T> {
    private callbacks: Map<T, () => void>;
    constructor() {
        this.callbacks = new Map();
    }

    public listen(type: T, onFocus: () => void) {
        this.callbacks.set(type, onFocus);
    }

    public focus(type: T) {
        const f = this.callbacks.get(type);
        if (f) {
            f();
        }
    }
}