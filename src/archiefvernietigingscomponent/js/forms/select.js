import React, {useState} from 'react';

import {HiddenInput, RadioInput, TextArea, TextInput} from './inputs';
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
            required={required}
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

const SelectWithCustomOption = (props) => {
    const {choices, label, required, name, id, customOtherChoiceLabel} = props;
    const [selectedOption, setSelectedOption] = useState('');
    const [commentValue, setCommentValue] = useState('');

    const emptyChoice = [['', '------']];
    const otherChoiceLabel = customOtherChoiceLabel ? customOtherChoiceLabel : 'Other'
    const allChoices = emptyChoice.concat(choices, [[otherChoiceLabel, otherChoiceLabel]]);

    const internalOnChange = (chosenValue) => {
        setSelectedOption(chosenValue);
        if (chosenValue !== otherChoiceLabel) {
            setCommentValue(chosenValue)
        }
    }

    return (
        <React.Fragment>
            <SelectInput
              name={`${name}_select`}
              id={`${id}_select`}
              initial={''}
              label={label}
              choices={allChoices}
              selected={selectedOption}
              required={required}
              onChange={internalOnChange}
            />
            <HiddenInput id={id} name={name} value={commentValue} />
            {selectedOption !== otherChoiceLabel ? null :
                <React.Fragment>
                    <label>Voeg nog een reden toe:</label>
                    <TextArea
                        disabled={selectedOption !== otherChoiceLabel}
                        required={selectedOption === otherChoiceLabel}
                        onChange={(event) => {setCommentValue(event.target.value)}}
                    />
                </React.Fragment>
            }

        </React.Fragment>
    );

}


export {SelectInput, SelectMultipleInput, RadioSelect, SelectWithCustomOption};
