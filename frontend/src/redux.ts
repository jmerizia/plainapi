import thunk from 'redux-thunk';
import { createSlice, /* createAsyncThunk, */ PayloadAction, configureStore, /* combineReducers, */ } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux'
import { randomRecordId, addElementAt } from './utils';
import { AppState, AppStatus, API, Endpoint, EndpointMethod, Field } from './types';
import { APIFromJSON } from './generated';
import { act } from '@testing-library/react';


export function findApi(state: AppState, apiId: string): API | undefined {
    return state.apis.find(api => api.id === apiId);
};

export function findEndpoint(state: AppState, apiId: string, endpointId: string): Endpoint | undefined {
    return findApi(state, apiId)?.endpoints.find(endpoint => endpoint.id === endpointId);
};

export function findField(state: AppState, apiId: string, endpointId: string, fieldId: string): Field | undefined {
    return findEndpoint(state, apiId, endpointId)?.fields.find(field => field.id === fieldId);
}

const initialAppState: AppState = {
    apis: [],
    status: 'loading',
    currentUser: undefined,
};

const updateApi = (state: AppState, apiId: string, f: (api: API) => API): AppState => ({
    ...state,
    apis: state.apis.map(api => api.id === apiId ? f(api) : api),
});

const updateEndpoint = (state: AppState, apiId: string, endpointId: string, f: (endpoint: Endpoint) => Endpoint): AppState => 
    updateApi(state, apiId, api => ({
        ...api,
        endpoints: api.endpoints.map(endpoint => endpoint.id === endpointId ? f(endpoint) : endpoint),
    }));

const updateField = (state: AppState, apiId: string, endpointId: string, fieldId: string, f: (field: Field) => Field): AppState =>
    updateEndpoint(state, apiId, endpointId, endpoint => ({
        ...endpoint,
        fields: endpoint.fields.map(field => field.id === fieldId ? f(field) : field),
    }));

export const slice = createSlice({
    name: 'primary',
    initialState: initialAppState,
    reducers: {
        setAPIId(state, action: PayloadAction<{ apiId: string, realId: number }>): AppState {
            return updateApi(state, action.payload.apiId, api => ({
                ...api,
                realId: action.payload.realId,
            }));
        },
        setEndpointId(state, action: PayloadAction<{ apiId: string, endpointId: string, realId: number }>): AppState {
            return updateEndpoint(state, action.payload.apiId, action.payload.endpointId, endpoint => ({
                ...endpoint,
                realId: action.payload.realId,
            }));
        },
        setFieldId(state, action: PayloadAction<{ apiId: string, endpointId: string, fieldId: string, realId: number }>): AppState {
            return updateField(state, action.payload.apiId, action.payload.endpointId, action.payload.fieldId, field => ({
                ...field,
                realId: action.payload.realId,
            }));
        },
        setAPIs(state, action: PayloadAction<{ apis: API[] }>): AppState {
            return {
                ...state,
                apis: action.payload.apis,
            };
        },
        setStatus(state, action: PayloadAction<{ status: AppStatus }>): AppState {
            return {
                ...state,
                status: action.payload.status,
            };
        },
        addAPI(state, action: PayloadAction<void>): AppState {
            return {
                ...state,
                apis: [
                    ...state.apis,
                    {
                        id: randomRecordId(),
                        realId: 'unknown',
                        title: 'New API',
                        endpoints: [],
                        created: new Date().getTime(),
                        updated: new Date().getTime(),
                    }
                ],
            };
        },
        removeAPI(state, action: PayloadAction<{ apiId: string }>): AppState {
            return {
                ...state,
                apis: state.apis.filter(api => api.id !== action.payload.apiId),
            };
        },
        changeAPITitle(state, action: PayloadAction<{ apiId: string, title: string }>): AppState {
            return updateApi(
                state,
                action.payload.apiId,
                api => ({ ...api, title: action.payload.title })
            );
        },
        addEndpoint(state, action: PayloadAction<{ apiId: string, title: string, method: EndpointMethod, location: number }>): AppState {
            return updateApi(
                state,
                action.payload.apiId,
                api => ({
                    ...api,
                    endpoints: addElementAt(api.endpoints, action.payload.location, {
                        id: randomRecordId(),
                        realId: 'unknown',
                        title: action.payload.title,
                        method: action.payload.method,
                        location: action.payload.location,
                        fields: [],
                        created: new Date().getTime(),
                        updated: new Date().getTime(),
                    })
                })
            );
        },
        removeEndpoint(state, action: PayloadAction<{ apiId: string, endpointId: string }>): AppState {
            return updateApi(
                state,
                action.payload.apiId,
                api => ({
                    ...api,
                    endpoints: api.endpoints.filter(e => e.id !== action.payload.endpointId)
                })
            )
        },
        changeEndpointTitle(state, action: PayloadAction<{ apiId: string, endpointId: string, title: string }>): AppState {
            return updateEndpoint(
                state,
                action.payload.apiId,
                action.payload.endpointId,
                endpoint => ({ ...endpoint, title: action.payload.title })
            )
        },
        changeEndpointMethod(state, action: PayloadAction<{ apiId: string, endpointId: string, method: EndpointMethod }>): AppState {
            return updateEndpoint(
                state,
                action.payload.apiId,
                action.payload.endpointId,
                endpoint => ({
                    ...endpoint,
                    method: action.payload.method,
                })
            )
        },
        addField(state, action: PayloadAction<{ apiId: string, endpointId: string, location: number, value: string, indent: number }>): AppState {
            return updateEndpoint(
                state,
                action.payload.apiId,
                action.payload.endpointId,
                endpoint => ({
                    ...endpoint,
                    fields: addElementAt(endpoint.fields, action.payload.location, {
                        id: randomRecordId(),
                        realId: 'unknown',
                        value: action.payload.value,
                        location: action.payload.location,
                        indent: action.payload.indent,
                        created: new Date().getTime(),
                        updated: new Date().getTime(),
                    })
                })
            )
        },
        removeField(state, action: PayloadAction<{ apiId: string, endpointId: string, fieldId: string }>): AppState {
            return updateEndpoint(
                state,
                action.payload.apiId,
                action.payload.endpointId,
                endpoint => ({
                    ...endpoint,
                    fields: endpoint.fields.filter(field => field.id !== action.payload.fieldId),
                })
            )
        },
        changeFieldValue(state, action: PayloadAction<{ apiId: string, endpointId: string, fieldId: string, value: string }>): AppState {
            return updateField(
                state,
                action.payload.apiId,
                action.payload.endpointId,
                action.payload.fieldId,
                field => ({
                    ...field,
                    value: action.payload.value,
                })
            )
        },
    },
    
    // extraReducers: (builder) => {
    //     builder.addCase(fetchInitNumber.uflfill, (state, action) => {
    //         return state = -1;
    //     });
    //     builder.addCase(fetchInitNumber.fulfilled, (state, action) => {
    //         return state = action.payload;
    //     });
    // },
});

export const store = configureStore({
    reducer: slice.reducer,
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().prepend(thunk),
});
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<AppState> = useSelector;
export const actions = slice.actions;
// export const asyncActions = {
//     login
// }
