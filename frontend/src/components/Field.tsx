import React, { useState, useRef, useEffect, useMemo } from 'react';
import { endpointsEqual, listsEqual, updateElementAt } from '../utils/misc';
import {
    Endpoint,
} from '../types';
import RegenIcon from '../icons/sync_white_24dp.svg';
import getCaretCoordinates from 'textarea-caret';
import Tooltip from '@material-ui/core/Tooltip';
import { withStyles, Theme } from '@material-ui/core/styles';
import { FocusDispatcher } from '../utils/misc';
import LightTooltip from './LightTooltip';


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

export default function Field<T>({
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
            <LightTooltip title={
                <React.Fragment>
                    {'{'}<br />
                    &nbsp;&nbsp;&nbsp;{'id: number,'}<br />
                    &nbsp;&nbsp;&nbsp;{'email: string,'}<br />
                    {'}'}
                </React.Fragment>
            }  placement='right' arrow>
                <span>
                    {value}
                </span>
            </LightTooltip>
        </div>;
}

