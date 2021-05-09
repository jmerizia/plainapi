import {
    createStore,
} from 'redux';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux'


export type Field = {
    id: number;
    value: string;
    indent: number;
    created: Date;
    updated: Date;
}

export type EndpointMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE';

export type Endpoint = {
    id: number;
    title: string;
    method: EndpointMethod;
    fields: Field[];
}

interface AppState {
    title: string;
    endpoints: Endpoint[];
    created: Date;
    updated: Date;
}

const initialAppState: AppState = {
    title: 'My Backend API',
    endpoints: [{
        id: 1,
        title: 'Get All Users',
        method: 'GET',
        fields: [
            {
                id: 1,
                value: 'get all users from the database',
                indent: 0,
                created: new Date(),
                updated: new Date(),
            }
        ],
    }],
    created: new Date(),
    updated: new Date(),
};


enum ActionType {
    CHANGE_API_TITLE,
    ADD_ENDPOINT,
    REMOVE_ENDPOINT,
    CHANGE_ENDPOINT_TITLE,
    ADD_FIELD,
    REMOVE_FIELD,
    CHANGE_FIELD_VALUE,
}

type ChangeAPITitleAction = {
    type: ActionType.CHANGE_API_TITLE;
    title: string;
}

export const changeAPITitle = (payload: { title: string }): ChangeAPITitleAction => ({
    type: ActionType.CHANGE_API_TITLE,
    title: payload.title,
});


type AddEndpointAction = {
    type: ActionType.ADD_ENDPOINT;
    after: number;
}

export const addEndpoint = (payload: { after: number }): AddEndpointAction => ({
    type: ActionType.ADD_ENDPOINT,
    after: payload.after,
});


type RemoveEndpointAction = {
    type: ActionType.REMOVE_ENDPOINT;
    endpointId: number;
}

export const removeEndpoint = (payload: { endpointId: number }): RemoveEndpointAction => ({
    type: ActionType.REMOVE_ENDPOINT,
    endpointId: payload.endpointId,
});


type ChangeEndpointTitleAction = {
    type: ActionType.CHANGE_ENDPOINT_TITLE;
    endpointId: number;
    title: string;
}

export const changeEndpointTitle = (payload: { endpointId: number, title: string }): ChangeEndpointTitleAction => ({
    type: ActionType.CHANGE_ENDPOINT_TITLE,
    endpointId: payload.endpointId,
    title: payload.title,
});


type AddFieldAction = {
    type: ActionType.ADD_FIELD;
    field: Field;
    after: number;
}

export const addField = (payload: { field: Field, after: number }): AddFieldAction => ({
    type: ActionType.ADD_FIELD,
    field: payload.field,
    after: payload.after,
});


type RemoveFieldAction = {
    type: ActionType.REMOVE_FIELD;
    fieldId: number;
}

export const removeField = (payload: { fieldId: number }): RemoveFieldAction => ({
    type: ActionType.REMOVE_FIELD,
    fieldId: payload.fieldId,
});


type ChangeFieldValueAction = {
    type: ActionType.CHANGE_FIELD_VALUE,
    fieldId: number;
    value: string;
}

export const changeFieldValue = (payload: { fieldId: number, value: string }): ChangeFieldValueAction => ({
    type: ActionType.CHANGE_FIELD_VALUE,
    fieldId: payload.fieldId,
    value: payload.value,
});


type SomeAction =
    ChangeAPITitleAction |
    AddEndpointAction | RemoveEndpointAction | ChangeEndpointTitleAction |
    AddFieldAction | RemoveFieldAction | ChangeFieldValueAction | ChangeFieldValueAction;


export const reducer = (state: AppState = initialAppState, action: SomeAction): AppState => {
    switch (action.type) {
        case ActionType.CHANGE_API_TITLE:
            return {
                ...state,
                title: action.title,
            };
        case ActionType.ADD_ENDPOINT:
            const endpoints: Endpoint[] = [];
            const newEndpoint: Endpoint = {
                id: Math.floor(Math.random()*10000),
                title: '',
                method: 'GET',
                fields: [
                    {
                        id: Math.floor(Math.random()*10000),
                        value: 'asd',
                        indent: 0,
                        created: new Date(),
                        updated: new Date(),
                    }
                ],
            };
            if (action.after === -1) {
                endpoints.push(newEndpoint);
            }
            state.endpoints.forEach(endpoint => {
                endpoints.push(endpoint);
                if (endpoint.id === action.after) {
                    endpoints.push(newEndpoint);
                }
            });
            console.log(endpoints);
            return {
                ...state,
                endpoints,
            };
        case ActionType.REMOVE_ENDPOINT:
            return {
                ...state,
                endpoints: state.endpoints.filter(endpoint => endpoint.id !== action.endpointId),
            };
        case ActionType.CHANGE_ENDPOINT_TITLE:
            return {
                ...state,
                endpoints: state.endpoints.map(endpoint => 
                    endpoint.id === action.endpointId ? { ...endpoint, title: action.title } : endpoint
                )
            };
        case ActionType.ADD_FIELD:
            return {
                ...state,
                endpoints: state.endpoints.map(endpoint => {
                    const fields = [];
                    if (action.after === -1) {
                        fields.push(action.field);
                    }
                    endpoint.fields.forEach(field => {
                        fields.push(field);
                        if (field.id === action.after) {
                            fields.push(action.field);
                        }
                    });
                    return {
                        ...endpoint,
                        fields,
                    }
                }),
            }
        case ActionType.REMOVE_FIELD:
            return {
                ...state,
                endpoints: state.endpoints.map(endpoint => ({
                    ...endpoint,
                    fields: endpoint.fields.filter(field => field.id !== action.fieldId),
                })),
            };
        case ActionType.CHANGE_FIELD_VALUE:
            return {
                ...state,
                endpoints: state.endpoints.map(endpoint => ({
                    ...endpoint,
                    fields: endpoint.fields.map(field =>
                        field.id === action.fieldId ? { ...field, value: action.value } : field
                    ),
                })),
            };
        default:
            return state;
    }
};

export const store = createStore(reducer);
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<AppState> = useSelector;
