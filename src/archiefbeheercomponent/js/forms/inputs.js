import React from 'react';

import { Help } from './help';
import { Label } from './label';
import { ErrorList, Wrapper } from './wrapper';


const Input = ({ type='text', id='', name='', initial, classes=null, checked=false, onBlur, onChange, required=false, disabled=false }) => {
    const classNames = classes ??`input__control input__control--${type}`;
    return (
        <input
            name={name}
            type={type}
            id={id}
            defaultValue={initial || ''}
            checked={checked}
            className={classNames}
            onBlur={ (event) => {
                if (onBlur) {
                    onBlur(event);
                }
            }}
            onChange={ (event) => {
                if (onChange) {
                    onChange(event);
                }
            }}
            required={required}
            disabled={disabled}
        ></input>
    );
};


const TextInput = (props) => {
    const { label, helpText, id, required } = props;

    return (
        <Wrapper>
            <Label label={label} required={required} idForLabel={id} />
            <Help helpText={helpText} idForLabel={id} />
            <ErrorList />
            <Input type="text" {...props} />
        </Wrapper>
    );
};

const TextArea = ({
    id='',
    name='',
    label='',
    helpText='',
    initial,
    classes=null,
    onBlur,
    onChange,
    required=false,
    disabled=false
}) => {
    const classNames = classes ??`input__control input__control--text`;

    return (
        <Wrapper>
            <Label label={label} required={required} idForLabel={id} />
            <Help helpText={helpText} idForLabel={id} />
            <ErrorList />
            <textarea
                name={name}
                id={id}
                defaultValue={initial || ''}
                className={classNames}
                onBlur={ (event) => {
                    if (onBlur) {
                        onBlur(event);
                    }
                }}
                onChange={ (event) => {
                    if (onChange) {
                        onChange(event);
                    }
                }}
                required={required}
                disabled={disabled}
            />
        </Wrapper>
    );
};


const DateInput = (props) => {
    return <Input type="date" {...props} />;
};

const CheckboxInput = (props) => {
    return <Input type="checkbox" {...props} />;
};

const RadioInput = (props) => {
    return <Input type="radio" {...props} />;
};

const HiddenInput = ({name, value}) => {
    return <input type="hidden" name={name} defaultValue={value} />
}

const FileInput = (props) => {
    const {label, name, required, id, helpText, ...extra} = props;

    return (
        <Wrapper>
            <Label label={label} required={required} idForLabel={id} />
            <ErrorList />
            <Input id={id} name={name} type="file" {...extra} />
            <Help helpText={helpText} idForLabel={id} />
        </Wrapper>
    );
}


export {Input, TextInput, TextArea, DateInput, CheckboxInput, RadioInput, HiddenInput, FileInput};
