declare type GlobalFetch = WindowOrWorkerGlobalScope;

export type RealId = number | 'unknown';

export type Field = {
    id: string;
    realId: RealId;
    value: string;
    location: number;
    indent: number;
    created: number;
    updated: number;
}

export type EndpointMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE';

export type Endpoint = {
    id: string;
    realId: RealId;
    title: string;
    method: EndpointMethod;
    location: number;
    fields: Field[];
    created: number;
    updated: number;
}

export type API = {
    id: string;
    realId: RealId;
    title: string;
    endpoints: Endpoint[];
    created: number;
    updated: number;
}

export type User = {
    id: string;
    realId: RealId;
    isAdmin: boolean;
    joined: number;
};

export type AppStatus = 'loading' | 'saving' | 'ready';

interface AppState {
    apis: API[];
    status: AppStatus;
    currentUser?: User;
}
