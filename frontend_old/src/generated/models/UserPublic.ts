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
 * @interface UserPublic
 */
export interface UserPublic {
    /**
     * 
     * @type {number}
     * @memberof UserPublic
     */
    id: number;
    /**
     * 
     * @type {boolean}
     * @memberof UserPublic
     */
    isAdmin: boolean;
    /**
     * 
     * @type {Date}
     * @memberof UserPublic
     */
    joined: Date;
}

export function UserPublicFromJSON(json: any): UserPublic {
    return UserPublicFromJSONTyped(json, false);
}

export function UserPublicFromJSONTyped(json: any, ignoreDiscriminator: boolean): UserPublic {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'id': json['id'],
        'isAdmin': json['is_admin'],
        'joined': (new Date(json['joined'])),
    };
}

export function UserPublicToJSON(value?: UserPublic | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'id': value.id,
        'is_admin': value.isAdmin,
        'joined': (value.joined.toISOString()),
    };
}


