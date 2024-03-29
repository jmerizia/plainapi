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
 * @interface Migration
 */
export interface Migration {
    /**
     * 
     * @type {number}
     * @memberof Migration
     */
    id: number;
    /**
     * 
     * @type {number}
     * @memberof Migration
     */
    apiId: number;
    /**
     * 
     * @type {string}
     * @memberof Migration
     */
    value: string;
    /**
     * 
     * @type {boolean}
     * @memberof Migration
     */
    applied: boolean;
    /**
     * 
     * @type {string}
     * @memberof Migration
     */
    sqlQuery: string;
}

export function MigrationFromJSON(json: any): Migration {
    return MigrationFromJSONTyped(json, false);
}

export function MigrationFromJSONTyped(json: any, ignoreDiscriminator: boolean): Migration {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'id': json['id'],
        'apiId': json['api_id'],
        'value': json['value'],
        'applied': json['applied'],
        'sqlQuery': json['sql_query'],
    };
}

export function MigrationToJSON(value?: Migration | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'id': value.id,
        'api_id': value.apiId,
        'value': value.value,
        'applied': value.applied,
        'sql_query': value.sqlQuery,
    };
}


