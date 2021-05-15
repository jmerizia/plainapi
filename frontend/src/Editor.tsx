import React, { useMemo, useCallback } from 'react';
import {
    Slate,
    Editable,
    withReact,
} from 'slate-react'
import { endpointsEqual, zip } from './utils';
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



export interface EditorProps {
    title: string;
    endpoints: Endpoint[];
    onChange(title: string, endpoints: Endpoint[]): void;
    onRestart(): void;
    previewLoading: boolean;
}

export default function Editor({
    title, endpoints, onChange, onRestart, previewLoading
}: EditorProps) {
    const value: Descendant[] = [
        {
            type: 'title',
            children: [{ text: title }],
        },
    ];
    endpoints.forEach(endpoint => {
        value.push({
            type: 'endpoint',
            children: [{ text: endpoint.value }]
        });
    });

    const editor = useMemo(
        () => withLayout(withHistory(withReact(createEditor()))),
        []
    );
    const renderElement = useCallback((props: RenderElementProps) => <Element {...props} />, []);

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
        <Slate
            editor={editor}
            value={value}
            onChange={newValue => {
                const newTitle = treeToTitle(newValue);
                const newEndpoints = treeToEndpoints(newValue);
                if (title !== newTitle || zip(endpoints, newEndpoints).some(([a, b]) => !endpointsEqual(a, b))) {
                    onChange(newTitle, newEndpoints);
                }
            }}
        >
            <Editable
                renderElement={renderElement}
                placeholder="Enter a title…"
                spellCheck={false}
                autoFocus
            />
        </Slate>
    </div>;
}


function Element({ attributes, children, element }: RenderElementProps) {
    switch (element.type) {
        case 'title':
            return <h2 className='editor-title' {...attributes}>{children}</h2>
        case 'endpoint':
            return <p className='editor-endpoint' {...attributes}>{children}</p>
        default:
            return null;
    }
}

function treeToTitle(tree: Descendant[]): string {
    const child = tree[0] as TitleElement;
    const textElem = child.children[0];
    return textElem.text;
}

function treeToEndpoints(tree: Descendant[]): Endpoint[] {
    const endpoints: Endpoint[] = [];
    tree.forEach((child, idx) => {
        if (idx === 0) return;
        const childCasted = child as EndpointElement;
        endpoints.push({
            method: 'GET',
            value: childCasted.children[0].text,
        });
    });
    return endpoints;
}


function withLayout (editor: CustomEditor) {
    const { normalizeNode } = editor;

    editor.normalizeNode = ([node, path]) => {
        if (path.length === 0) {
            if (editor.children.length < 1) {
                const title: TitleElement = {
                    type: 'title',
                    children: [{ text: 'Untitled' }],
                };
                Transforms.insertNodes(editor, title, { at: path.concat(0) });
            }

            if (editor.children.length < 2) {
                const paragraph: EndpointElement = {
                    type: 'endpoint',
                    children: [{ text: '' }],
                };
                Transforms.insertNodes(editor, paragraph, { at: path.concat(1) });
            }

            for (const [child, childPath] of Node.children(editor, path)) {
                const type = childPath[0] === 0 ? 'title' : 'endpoint';
        
                if (SlateElement.isElement(child) && child.type !== type) {
                    const newProperties: Partial<SlateElement> = { type };
                    Transforms.setNodes(editor, newProperties, { at: childPath });
                }
            }
        }

        return normalizeNode([node, path]);
    }

    return editor;
}
