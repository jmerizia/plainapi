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
    method: string;
    value: string;
};

export type AppState = {
    api?: API;
    saving: boolean;
    currentUser?: User;
};


export type CustomText = {
    bold?: boolean;
    italic?: boolean;
    code?: boolean;
    text: string;
}
export type EmptyText = {
    text: string;
}
export type TextElement = CustomText | EmptyText;
export type TitleElement = { type: 'title'; children: TextElement[] };
export type EndpointElement = { type: 'endpoint'; children: TextElement[] };
export type CustomElement = TitleElement | EndpointElement;
export type CustomEditor = BaseEditor & ReactEditor & HistoryEditor;

declare module 'slate' {
    interface CustomTypes {
        Editor: CustomEditor;
        Element: CustomElement;
        Text: TextElement;
    }
}
