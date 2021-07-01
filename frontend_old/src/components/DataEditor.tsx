import React, { useState, useRef, useEffect, useMemo } from 'react';
import { updateElementAt } from '../utils/misc';


export interface DataEditorProps {
    migrations: string[];
    onChange(migrations: string[]): void;
}

export default function DataEditor({ migrations, onChange }: DataEditorProps) {
    return <div className='data-editor'>
        <h1>Migrations</h1>
        { migrations.map((migration, idx) => <>
            <input
                className='input-base'
                value={migration}
                onChange={ev => onChange(updateElementAt(migrations, ev.target.value, idx))}
                style={{
                    backgroundColor: 'white',
                }}
            />
            <br />
        </>) }
    </div>;
}