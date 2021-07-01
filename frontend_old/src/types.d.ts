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
    url: string;
    value: string;
};

export type AppState = {
    api?: API;
    saving: boolean;
    currentUser?: User;
};
