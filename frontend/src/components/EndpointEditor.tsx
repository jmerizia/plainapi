import React, { useState, useRef, useEffect, useMemo } from 'react';
import { endpointsEqual, listsEqual, updateElementAt } from '../utils/misc';
import {
    Endpoint,
} from '../types';
import RegenIcon from './icons/sync_white_24dp.svg';
import getCaretCoordinates from 'textarea-caret';
import Tooltip from '@material-ui/core/Tooltip';
import { withStyles, Theme } from '@material-ui/core/styles';
import { FocusDispatcher, getMethodStyle } from '../utils/misc';
import Field from './Field';
import LightTooltip from './LightTooltip';


interface EndpointEditorProps {
    endpoint: Endpoint;
    onChange(endpoint: Endpoint): void;
    onRegen(): void;
}

export default function EndpointEditor({ endpoint, onChange, onRegen }: EndpointEditorProps) {

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
        <div style={{ display: 'flex', padding: '5px', marginLeft: '5px', }}>
            <LightTooltip title="() → User[]"  placement='right' arrow>
                <span>
                    () → list of users
                </span>
            </LightTooltip>
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

