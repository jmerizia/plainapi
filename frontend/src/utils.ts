import { useEffect, useState, useMemo } from 'react';
import { Configuration, DefaultApi, API } from './generated';


export async function wait(ms: number): Promise<void> {
    return new Promise(r => setTimeout(r, ms));
}

export function useBackend() {
    const [currentUserId, setCurrentUserId] = useState<number | undefined>();
    const [token, setToken] = useState<string | undefined>();
    const backend = useMemo(() => new DefaultApi(new Configuration({
        basePath: 'http://localhost:3001',
        accessToken: token ? 'Bearer ' + token : undefined,
    })), [token]);

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

export async function fetchApiIdsForUser(backend: DefaultApi, userId: number): Promise<number[]> {
    const apis = await backend.readApisForUserApiV0ApisGetAllForUserGet({ userId });
    return apis.map(api => api.id);
}

export function insertElementAt<T>(ar: T[], e: T, location: number): T[] {
    const nar = ar.slice();
    nar.splice(location, 0, e);
    return nar;
}

export function removeElementAt<T>(ar: T[], location: number): T[] {
    const nar = ar.slice();
    nar.splice(location, 1);
    return nar;
}

export function updateElementAt<T>(ar: T[], v: T, location: number): T[] {
    const nar = ar.slice();
    nar[location] = v;
    return nar;
}

export function swapElementsAt<T>(ar: T[], a: number, b: number): T[] {
    const nar = ar.slice();
    const tmp = nar[a];
    nar[a] = nar[b];
    nar[b] = tmp;
    return nar;
}

export function moveElementFromTo<T>(ar: T[], s: number, t: number): T[] {
    const nar = ar.slice();
    const [removed] = nar.splice(s, 1);
    nar.splice(t, 0, removed);
    return nar;
}

export function logError(err: any) {
    console.error(err);
}