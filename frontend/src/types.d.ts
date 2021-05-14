import { API } from './generated';
import {
    Text,
    Descendant,
    BaseEditor,
} from 'slate'
import { ReactEditor } from 'slate-react'
import { HistoryEditor } from 'slate-history'
  

declare module "*.png";
declare module "*.svg";


export type Endpoint = {
    id: number;
    method: string;
    value: string;
};

export type AppState = {
    api?: API;
    saving: boolean;
    currentUser?: User;
};


export type TitleElement = { type: 'title'; children: Descendant[] };
export type ParagraphElement = { type: 'paragraph'; children: Descendant[] };
export type CustomElement = TitleElement | ParagraphElement;
export type CustomEditor = BaseEditor & ReactEditor & HistoryEditor;
export type CustomText = {
    bold?: boolean;
    italic?: boolean;
    code?: boolean;
    text: string;
}
export type EmptyText = {
    text: string;
}

declare module 'slate' {
    interface CustomTypes {
        Editor: CustomEditor;
        Element: CustomElement;
        Text: CustomText | EmptyText;
    }
}
