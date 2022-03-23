import React, {useContext} from 'react';
import {useImmerReducer} from 'use-immer';
import {cloneDeep} from 'lodash';


import {SelectInput} from '../../forms/select';
import {HiddenInput} from '../../forms/inputs';
import {ReviewersContext} from './context';


const EMPTY_REVIEWER = {
    id: '',
    disabled: false,
    required: true,
};

const INITIAL_STATE = {
    reviewers: [EMPTY_REVIEWER],
};

const reducer = (draft, action) => {
    switch (action.type) {
        case 'ADD_REVIEWER': {
            let reviewerDetails = {...action.payload} || {};
            // If the last reviewer has not been filled in yet and a new one is added, then it is disabled.
            if (!draft.reviewers[draft.reviewers.length-1].id) {
                reviewerDetails.disabled = true;
            }

            draft.reviewers.push({...EMPTY_REVIEWER, ...reviewerDetails});
            break;
        }
        case 'DELETE_REVIEWER': {
            const {index} = action.payload;
            let updatedReviewers = [...draft.reviewers];
            if (index >= 0 && updatedReviewers[index+1]) {
                if (index === 0 || updatedReviewers[index-1].id) {
                    updatedReviewers[index+1].disabled = false;
                }
            }
            updatedReviewers.splice(index, 1);
            draft.reviewers = updatedReviewers;
            break;
        }
        case 'UPDATE_REVIEWER': {
            const {index, id} = action.payload;

            draft.reviewers[index].id = id;
            if (id) {
                if (draft.reviewers[index + 1]) {
                    draft.reviewers[index + 1].disabled = false;
                }
            } else {
                if (draft.reviewers[index + 1]) {
                    draft.reviewers[index + 1].disabled = true;
                }
            }
            break;
        }
        default: {
            throw new Error(`Unknown action ${action.type}`);
        }
    }
};

const SelectReviewers = ({multipleReviewersMandatory}) => {
    let initialState = cloneDeep(INITIAL_STATE);
    if (multipleReviewersMandatory) {
        initialState.reviewers.push({...EMPTY_REVIEWER, disabled: true});
    }

    const [state, dispatch] = useImmerReducer(reducer, initialState);

    const onChange = (index, value) => {
        dispatch({type: 'UPDATE_REVIEWER', payload: {index: index, id: value}});
    };

    const onDelete = (index) => {
        dispatch({type: 'DELETE_REVIEWER', payload: {index: index}});
    };

    return (
        <React.Fragment>
            {state.reviewers.map((reviewer, key) => (
                <Reviewer
                    key={key}
                    index={key}
                    reviewer={reviewer}
                    onChange={onChange.bind(null, key)}
                    onDelete={onDelete.bind(null, key)}
                />
            ))}
            <button type="button" className="btn" onClick={() => dispatch({type: 'ADD_REVIEWER'})}>
                <span className="addLink">Voeg reviewer toe</span>
            </button>
        </React.Fragment>
    );
};


const Reviewer = ({index, reviewer, onChange, onDelete}) => {
    const reviewerChoices = useContext(ReviewersContext);

    const onConfirm = (event) => {
        event.preventDefault();
        if (window.confirm(`Wilt u reviewer ${index+1} verwijderen?`)) {
            onDelete();
        }
    }

    return (
        <React.Fragment>
            <button onClick={onConfirm}>X</button>
            <HiddenInput
                name="reviewers"
                id={`id_reviewers_${index}`}
                value={reviewer.id}
            />
            <SelectInput
                name="reviewer"
                selected={reviewer.id}
                label={`Reviewer ${index+1}`}
                helpText="Kies een medewerker om de lijst te beoordelen"
                choices={reviewerChoices}
                id={"id_reviewer"}
                disabled={reviewer.disabled}
                required={reviewer.required}
                onChange={onChange}
            />
        </React.Fragment>

    );
};



export {SelectReviewers};
