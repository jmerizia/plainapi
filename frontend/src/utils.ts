import { useEffect, useState, } from 'react';
import { Configuration, DefaultApi } from './generated';
import { actions } from './redux';
import { AppState, API, Endpoint, EndpointMethod, Field } from './types';


export async function wait(ms: number): Promise<void> {
    return new Promise(r => setTimeout(r, ms));
}

export function useBackend() {
    const [currentUserId, setCurrentUserId] = useState<number | undefined>();
    const [token, setToken] = useState<string | undefined>();
    const backend = new DefaultApi(new Configuration({
        basePath: 'http://localhost:3001',
        accessToken: token ? 'Bearer ' + token : undefined,
    }));

    const getCredentials = (): { userid: number, token: string } | undefined => {
        const userid = localStorage.getItem('userid');
        const token = localStorage.getItem('token');
        if (userid === null || token === null) {
            return undefined;
        }
        return { userid: parseInt(userid), token };
    };

    const setCredentials = (userid: number, token: string) => {
        localStorage.setItem('userid', userid.toString());
        localStorage.setItem('token', token);
    }

    const clearCredentials = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('userid');
    }

    const login = async (username: string, password: string) => {
        const res = await backend.loginUserApiV0UsersLoginPost({ username, password });
        setCredentials(res.id, res.accessToken);
        setToken(res.accessToken);
        setCurrentUserId(res.id);
    };

    const logout = async () => {
        clearCredentials();
        setToken(undefined);
        setCurrentUserId(undefined);
    }

    useEffect(() => {
        const c = getCredentials();
        if (c) {
            setToken(c.token);
            setCurrentUserId(c.userid);
        }
    }, []);

    return { backend, currentUserId, login, logout };
}

export function randomRecordId(): string { return Math.floor(Math.random() * 1000000).toString(); }

export function parseEndpointMethod(method: string): EndpointMethod {
    switch (method) {
        case 'GET':
            return 'GET';
        case 'POST':
            return 'POST';
        case 'DELETE':
            return 'DELETE';
        case 'PATCH':
            return 'PATCH';
        default:
            throw Error('Invalid method');
    }
}

export async function fetchApi(backend: DefaultApi, apiId: number): Promise<API> {
    const api = await backend.readApiApiV0ApisGetByIdGet({ apiId });
    const endpoints = await backend.readEndpointsForApiApiV0EndpointReadAllForApiGet({ apiId })
    return {
        id: randomRecordId(),  // doing this here to catch errors early
        realId: api.id,
        title: api.title,
        endpoints: await Promise.all(endpoints.map(async (endpoint): Promise<Endpoint> => {
            return {
                id: randomRecordId(),  // same as above
                realId: endpoint.id,
                title: endpoint.title,
                location: endpoint.location,
                method: parseEndpointMethod(endpoint.method),
                fields: (await backend.readFieldsForEndpointApiV0FieldReadForEndpointGet({
                    apiId,
                    endpointId: endpoint.id,
                })).map((field): Field => {
                    return {
                        id: randomRecordId(),  // same as above
                        realId: field.id,
                        value: field.value,
                        location: field.location,
                        indent: 0,
                        created: field.created.getTime(),
                        updated: field.updated.getTime(),
                    };
                }),
                created: endpoint.created.getTime(),
                updated: endpoint.updated.getTime(),
            }
        })),
        created: api.created.getTime(),
        updated: api.updated.getTime(),
    }
}

export async function fetchApiIdsForUser(backend: DefaultApi, userId: number): Promise<number[]> {
    const apis = await backend.readApisForUserApiV0ApisGetAllForUserGet({ userId });
    return apis.map(api => api.id);
}

export type WithLocation<T> = T & { location: number };

export function addElementAt<T>(arr: WithLocation<T>[], location: number, newEl: WithLocation<T>): WithLocation<T>[] {
    if (arr.length === 0) {
        return [{ ...newEl, location }];
    }
    const arrSorted = arr.sort((a, b) => a.location - b.location);
    const newArr: WithLocation<T>[] = [];
    let cur = 0;
    for (let i = 0; i < arrSorted.length; i++) {
        const el = arrSorted[i];
        newArr.push({ ...el, location: cur });
        if (cur === location) {
            newArr.push({ ...newEl, location, });
            cur++;
        }
        cur++;
    }
    if (location === arr.length) {
        newArr.push({ ...newEl, location })
    }
    console.log('after', newArr);
    return newArr;
}

export function logError(err: any) {
    console.error(err);
}