import React, { useState, useRef, useEffect, useMemo } from 'react';
import { endpointsEqual, listsEqual, updateElementAt } from '../utils/misc';
import {
    Endpoint,
} from '../types';
import RegenIcon from '../icons/sync_white_24dp.svg';
import getCaretCoordinates from 'textarea-caret';
import Tooltip from '@material-ui/core/Tooltip';
import { withStyles, Theme } from '@material-ui/core/styles';
import EndpointEditor from './EndpointEditor';


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
            className='input-base input-api-title'
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


