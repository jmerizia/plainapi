/* tslint:disable */
/* eslint-disable */
/**
 * PlainAPI
 * Create APIs with plain English
 *
 * The version of the OpenAPI document: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { exists, mapValues } from '../runtime';
/**
 * 
 * @export
 * @interface Endpoint
 */
export interface Endpoint {
    /**
     * 
     * @type {string}
     * @memberof Endpoint
     */
    method: string;
    /**
     * 
     * @type {string}
     * @memberof Endpoint
     */
    url: string;
    /**
     * 
     * @type {string}
     * @memberof Endpoint
     */
    value: string;
}

export function EndpointFromJSON(json: any): Endpoint {
    return EndpointFromJSONTyped(json, false);
}

export function EndpointFromJSONTyped(json: any, ignoreDiscriminator: boolean): Endpoint {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'method': json['method'],
        'url': json['url'],
        'value': json['value'],
    };
}

export function EndpointToJSON(value?: Endpoint | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'method': value.method,
        'url': value.url,
        'value': value.value,
    };
}


