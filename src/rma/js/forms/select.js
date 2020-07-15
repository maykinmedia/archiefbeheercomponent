import React from 'react';

import { RadioInput } from './inputs';
import { Help } from './help';
import { Label } from './label';
import { ErrorList, Wrapper } from './wrapper';


const SelectInput = ({ name, label='', required=false, choices=[], id='', helpText='', classes=null, onChange, disabled=false, selected='' }) => {
    const classNames = classes ?? 'input__control input__control--select';
    const options = choices.map(([value, label], index) => {
        return (
            <option key={index} value={value}>{label}</option>
        );
    });

    const select = (
        <select
            name={name}
            id={id}
            className={classNames}
            disabled={!!disabled}
            value={selected}
            onChange={(event) => {
                if (onChange) {
                    onChange(event.target.value)
                }
            }}
        >
            { options }
        </select>
    );

    return (
        <Wrapper>
            <Label label={label} required={required} />
            <Help helpText={helpText} />
            <ErrorList />
            { select }
        </Wrapper>
    );
};


const SelectMultipleInput = (props) => {
    const { choices, name, id, classes, onChange, size} = props;

    const options = choices.map(([value, label], index) => {
        return (
            <option key={index} value={value}>{label}</option>
        );
    });

    return (
        <select
            multiple={true}
            size={size}
            name={name}
            id={id}
            className={classes}
            onChange={(event) => {
                const selectedOptions = Array.from(
                    event.target.selectedOptions,
                    option => option.value
                    );
                onChange(selectedOptions);
            }}
        >
            { options }
        </select>
    );
};


const RadioSelect = (props) => {
    const { choices, name, onChange, initialValue } = props;

    const radios = choices.map( ([value, label], index) => {
        return (
            <li key={index}>
                <label>
                    <RadioInput
                        name={name}
                        initial={value}
                        label={label}
                        checked={value === initialValue}
                        onChange={ (event) => {
                            if (onChange) {
                                onChange(event);
                            }
                        }}
                    />
                    {label}
                </label>
            </li>
        );
    });

    return (
        <ul>
            { radios }
        </ul>
    )
};


export {SelectInput, SelectMultipleInput, RadioSelect};
